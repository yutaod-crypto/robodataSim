"""Build an offline reset-layout gallery from a task-independent JSON manifest."""
import argparse
import html
import json
import math
from pathlib import Path
from urllib.parse import urlparse


def build(manifest, output):
    bounds = manifest['bounds_xy']
    if len(bounds) != 4 or not all(math.isfinite(v) for v in bounds):
        raise ValueError('bounds_xy must be finite [xmin, xmax, ymin, ymax]')
    xmin, xmax, ymin, ymax = bounds
    if xmin >= xmax or ymin >= ymax:
        raise ValueError('Bounds must have positive area')
    episodes = manifest['episodes']
    if not episodes:
        raise ValueError('At least one episode is required')
    scale = min(260/(xmax-xmin), 260/(ymax-ymin))
    colors = manifest['object_colors']
    def polygon(item, color):
        vertices = item['polygon_xy']
        if len(vertices) < 3 or any(len(p)!=2 or not all(math.isfinite(v) for v in p) for p in vertices):
            raise ValueError('Footprints require at least three finite XY vertices')
        points = ' '.join(f'{20+(x-xmin)*scale:.3f},{20+(ymax-y)*scale:.3f}' for x,y in vertices)
        return f'<polygon points="{points}" fill="{html.escape(color, quote=True)}" stroke="#223" stroke-width="1"><title>{html.escape(item["name"])}</title></polygon>'
    cards = []
    for episode in episodes:
        names = [o['name'] for o in episode['objects']]
        if len(names)!=len(set(names)):
            raise ValueError('Duplicate object identities in an episode')
        shapes = ''.join(polygon(o, '#65717b') for o in manifest.get('fixtures', []))
        shapes += ''.join(polygon(o, colors[o['name']]) for o in episode['objects'])
        title = f"{episode['id']} · seed {episode.get('seed', 'unspecified')}"
        drawing = f'<svg viewBox="0 0 310 310" role="img" aria-label="{html.escape(title,quote=True)}"><rect width="310" height="310" fill="#f1f1ea"/>{shapes}<text x="20" y="302" fill="#223" font-size="12">World XY · +X right · +Y up</text></svg>'
        video = episode.get('video')
        if video:
            # Local relative paths keep the gallery portable beside its videos.
            if urlparse(video).scheme or video.startswith(('/', '\\')):
                raise ValueError('video must be a relative local path')
            movie = f'<video controls preload="none" src="{html.escape(video,quote=True)}"></video>'
        else:
            movie = '<p>Reset-layout sample; no video attached.</p>'
        cards.append(f'<article><h2>{html.escape(title)}</h2>{drawing}{movie}</article>')
    legend = ' · '.join(f'<span style="color:{html.escape(c,quote=True)}">■</span> {html.escape(n)}' for n,c in colors.items())
    title = html.escape(manifest['title'])
    population = html.escape(manifest['population'])
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>body{{font:16px system-ui;background:#171d24;color:#eef;margin:24px}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}article{{background:#26313e;padding:12px;border-radius:8px}}h2{{font-size:17px}}svg,video{{width:100%}}p{{line-height:1.5}}</style>
<h1>{title}</h1><p>Population: {population}. {len(episodes)} layouts. All plots use the same world bounds and metric scale.</p><p>{legend}</p><main>{''.join(cards)}</main></html>'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    build(json.loads(a.manifest.read_text()),a.output)


if __name__=='__main__':main()
