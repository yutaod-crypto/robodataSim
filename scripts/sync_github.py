#!/usr/bin/env python3
"""Publish this skill to the authenticated user's private robodataSim repository.

--prepare builds the isolated checkout without credentials or network access.
--watch checks for changes every 5 seconds and publishes after 10 quiet seconds.
No credentials are written to disk; remote conflicts stop synchronization.
"""
import argparse, base64, hashlib, json, os, shutil, subprocess, time, urllib.request, urllib.error
from pathlib import Path

REPO = 'robodataSim'

def git(path, *args, env=None):
    p = subprocess.run(['git', '-C', str(path), *args], capture_output=True, text=True, env=env)
    if p.returncode:
        raise RuntimeError('Git operation failed: ' + args[0] + '. Check authentication or remote changes; no force push was attempted.')
    return p.stdout.strip()

def files(source):
    return {str(p.relative_to(source)):p.read_bytes() for p in source.rglob('*')
            if p.is_file() and not any(x.startswith('.') or x=='__pycache__' for x in p.relative_to(source).parts)
            and p.suffix in ('.md','.py','.yaml','.yml','.json','.svg')}

def fingerprint(source):
    return hashlib.sha256(b''.join(k.encode()+v for k,v in sorted(files(source).items()))).hexdigest()

def token():
    value=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if value:return value
    if shutil.which('gh'):
        p=subprocess.run(['gh','auth','token'],capture_output=True,text=True)
        if p.returncode==0 and p.stdout.strip():return p.stdout.strip()
    try:
        p=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',
                         capture_output=True,text=True,timeout=20,env=dict(os.environ,GIT_TERMINAL_PROMPT='0'))
        values=dict(line.split('=',1) for line in p.stdout.splitlines() if '=' in line)
        if values.get('password'):return values['password']
    except subprocess.TimeoutExpired:pass
    raise RuntimeError('No accessible GitHub login. Run from your authenticated VS Code terminal, or install GitHub CLI and run gh auth login first. Do not paste tokens into chat.')

def api(path, secret, data=None):
    request=urllib.request.Request('https://api.github.com'+path,
        data=None if data is None else json.dumps(data).encode(),
        headers={'Authorization':'Bearer '+secret,'Accept':'application/vnd.github+json',
                 'X-GitHub-Api-Version':'2022-11-28','User-Agent':'robodataSim-skill-sync'})
    with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)

def stage(source,checkout):
    checkout.mkdir(parents=True,exist_ok=True)
    if not (checkout/'.git').exists():
        if any(checkout.iterdir()):raise RuntimeError('Checkout directory must be empty before initialization.')
        git(checkout,'init','-b','main')
    if git(checkout,'rev-parse','--show-toplevel')!=str(checkout):raise RuntimeError('Not an isolated skill checkout.')
    selected=files(source)
    selected['README.md']=("# robodataSim\n\nReusable robosuite / MuJoCo task-building skill. Start with [SKILL.md](SKILL.md).\n\n"
        "Includes object/mechanism design standards, task contracts, randomized reset layouts,\n"
        "controller validation and demonstration replay guidance. Simulation datasets are not included.\n\n"
        "The skill's internal identifier remains `robosuite-task-builder`.\n"
        "To synchronize from its source checkout, run `python3 scripts/sync_github.py`;\n"
        "add `--watch` to publish after saved edits remain unchanged for 10 seconds.\n"
        "The watcher must stay running and have GitHub authentication/network access.\n").encode()
    # Only remove previously tracked skill files; never sweep unrelated untracked files.
    for name in git(checkout,'ls-files').splitlines():
        if name not in selected:(checkout/name).unlink(missing_ok=True)
    for name,data in selected.items():
        p=checkout/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    git(checkout,'add','--update')
    git(checkout,'add','--',*selected)

def publish(source,checkout,prepare=False):
    stage(source,checkout)
    if prepare:
        print('Prepared skill-only checkout:',checkout);return
    secret=token();user=api('/user',secret);owner=user['login'];url=f'https://github.com/{owner}/{REPO}.git'
    try:remote=api(f'/repos/{owner}/{REPO}',secret)
    except urllib.error.HTTPError as error:
        if error.code!=404:raise
        remote=api('/user/repos',secret,dict(name=REPO,private=True,description='Robosuite / MuJoCo simulation task and dataset building skill',auto_init=False))
    if remote['owner']['login'].lower()!=owner.lower():raise RuntimeError('Repository owner does not match authenticated user.')
    current=git(checkout,'remote')
    if 'origin' in current.splitlines():
        if git(checkout,'remote','get-url','origin')!=url:raise RuntimeError('Existing origin differs from the authenticated destination.')
    else:git(checkout,'remote','add','origin',url)
    env=dict(os.environ)
    # Ephemeral auth in subprocess environment, not command arguments or git config files.
    count=int(env.get('GIT_CONFIG_COUNT','0'))
    env.update(GIT_CONFIG_COUNT=str(count+1),**{f'GIT_CONFIG_KEY_{count}':'http.https://github.com/.extraheader',
        f'GIT_CONFIG_VALUE_{count}':'Authorization: Basic '+base64.b64encode(('x-access-token:'+secret).encode()).decode()})
    git(checkout,'fetch','origin',env=env)
    refs=git(checkout,'for-each-ref','--format=%(refname)','refs/remotes/origin')
    if refs:
        try:head=git(checkout,'rev-parse','HEAD')
        except RuntimeError:raise RuntimeError('Remote repository is not empty. Clone and reconcile it before publishing.')
        remote_head=git(checkout,'rev-parse','refs/remotes/origin/main')
        git(checkout,'merge-base','--is-ancestor',remote_head,head)
    changed=git(checkout,'diff','--cached','--name-only')
    if changed:
        identity=dict(env,GIT_AUTHOR_NAME=user.get('name') or owner,GIT_COMMITTER_NAME=user.get('name') or owner,
                      GIT_AUTHOR_EMAIL=f"{user['id']}+{owner}@users.noreply.github.com",GIT_COMMITTER_EMAIL=f"{user['id']}+{owner}@users.noreply.github.com")
        git(checkout,'commit','-m','Update robot simulation skill',env=identity)
    git(checkout,'push','-u','origin','main',env=env)
    print('Synchronized:',remote['html_url'],flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--checkout',type=Path,default=Path.cwd()/'.skill-publish'/REPO)
    p.add_argument('--prepare',action='store_true');p.add_argument('--watch',action='store_true');a=p.parse_args()
    if a.prepare and a.watch:p.error('--prepare and --watch cannot be combined')
    source=a.source.resolve();checkout=a.checkout.resolve()
    if source==checkout or source in checkout.parents:raise RuntimeError('Publishing checkout must be outside the skill source.')
    publish(source,checkout,a.prepare)
    if a.watch:
        published=observed=fingerprint(source);changed_at=time.monotonic()
        print('Watching local skill changes; Ctrl+C stops automatic synchronization.',flush=True)
        while True:
            time.sleep(5);current=fingerprint(source)
            if current!=observed:observed=current;changed_at=time.monotonic()
            if current!=published and time.monotonic()-changed_at>=10:
                publish(source,checkout);published=current

if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:print('Synchronization stopped.')
    except Exception as error:
        print('Synchronization stopped:',str(error));raise SystemExit(1)
