"""Build the submission graphical abstract: python3 analysis/11_graphical_abstract.py.

Left to right: angiographic sequences -> included studies -> how they use time (donut)
-> research-gap clusters (Venn). Counts are read from the committed data (screening CSV,
extraction/out, the cluster table in 09_venn_diagram.py).
Output: graphical_abstract.{pdf,png}, 13 x 5 in (3900 x 1500 px).
"""
import ast
import csv
import glob
import json
import math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, PathPatch, Wedge
from matplotlib.path import Path as MPath

ROOT = Path(__file__).resolve().parents[1]

ns = {}
for node in ast.parse((ROOT / 'analysis/09_venn_diagram.py').read_text()).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') in {'CLUSTERS', 'COLOURS'}:
        name = node.targets[0].id
        if name == 'COLOURS':
            ns[name] = {ast.literal_eval(k): {kw.arg: ast.literal_eval(kw.value) for kw in v.keywords}
                        for k, v in zip(node.value.keys, node.value.values)}
        else:
            ns[name] = ast.literal_eval(node.value)
clusters, colours = ns['CLUSTERS'], ns['COLOURS']

screened = sum(1 for _ in csv.DictReader(open(ROOT / 'screening/stage1_llm_decisions.csv')))
cats = [json.load(open(f))['method'].get('temporal_category') for f in glob.glob(str(ROOT / 'extraction/out/R*.json'))]
studies = len(cats)
learned = sum(c in {'recurrent', 'cnn3d_video', 'transformer_ssm'} for c in cats)
fixed = sum(c in {'frame_aggregation', 'optical_flow_registration', 'hemodynamic_physics'} for c in cats)
rest = studies - learned - fixed
gap_total = sum(len(c['gaps']) for c in clusters.values())

INK, MUTED, GREY = '#1E2A38', '#6B7785', '#9AA5B1'
LEARNED, FIXED, NONE = '#2F5D8A', '#8FB0CF', '#DDE3EA'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
fig = plt.figure(figsize=(13, 5))
ax = fig.add_axes([0, 0, 1, 1])
ax.set(xlim=(0, 13), ylim=(0, 5), aspect='equal')
ax.axis('off')

ax.text(6.5, 4.6, 'AI for angiographic sequence analysis: a systematic review',
        ha='center', va='center', fontsize=17, weight='bold', color=INK)


def arrow(x0, x1, y=2.3):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle='-|>', mutation_scale=16, color=GREY, lw=1.4))


def caption(x, text):
    ax.text(x, .52, text, ha='center', va='center', fontsize=11, color=MUTED)


# 1. An angiographic run: three offset frames, contrast filling a vessel tree.
def vessel(x0, y0, s, alpha):
    """A vessel tree: a curved trunk with three branches that start on the trunk."""
    trunk = [(.22, .06), (.40, .50), (.52, .94)]
    def on_trunk(t):
        (ax0, ay0), (ax1, ay1), (ax2, ay2) = trunk
        return ((1 - t) ** 2 * ax0 + 2 * (1 - t) * t * ax1 + t * t * ax2,
                (1 - t) ** 2 * ay0 + 2 * (1 - t) * t * ay1 + t * t * ay2)
    def draw(pts, lw):
        path = MPath([(x0 + px * s, y0 + py * s) for px, py in pts], [MPath.MOVETO, MPath.CURVE3, MPath.CURVE3])
        ax.add_patch(PathPatch(path, fill=False, edgecolor=INK, lw=lw, alpha=alpha, capstyle='round'))
    draw(trunk, 3.2)
    for t, ctrl, end, lw in [(.55, (.68, .62), (.84, .84), 2.0), (.32, (.18, .45), (.16, .74), 1.8),
                             (.42, (.62, .36), (.86, .30), 1.6)]:
        draw([on_trunk(t), ctrl, end], lw)


S = 1.5
for i, alpha in enumerate([.2, .5, .9]):
    x0, y0 = .5 + i * .3, 1.75 - i * .25
    ax.add_patch(FancyBboxPatch((x0, y0), S, S, boxstyle='round,pad=0,rounding_size=.05',
                                facecolor='#F3F5F8', edgecolor='#B8C2CD', lw=1))
    vessel(x0, y0, S, alpha)
caption(1.55, 'angiographic sequences')
arrow(2.85, 3.35)

# 2. Included studies.
ax.text(4.2, 2.5, f'{studies}', ha='center', va='center', fontsize=36, weight='bold', color=INK)
ax.text(4.2, 1.9, 'studies', ha='center', va='center', fontsize=12, color=MUTED)
caption(4.2, f'of {screened:,} screened')
arrow(5.05, 5.55)

# 3. How studies use time.
cx, cy, R = 6.95, 2.4, 1.25
start = 90
for count, col in [(learned, LEARNED), (fixed, FIXED), (rest, NONE)]:
    sweep = 360 * count / studies
    ax.add_patch(Wedge((cx, cy), R, start - sweep, start, width=.4, facecolor=col, edgecolor='white', lw=2))
    mid = math.radians(start - sweep / 2)
    ax.text(cx + (R - .2) * math.cos(mid), cy + (R - .2) * math.sin(mid), str(count), ha='center', va='center',
            fontsize=10, weight='bold', color='white' if col == LEARNED else INK)
    start -= sweep
ax.text(cx, cy + .1, f'{(learned + fixed) / studies:.1%}', ha='center', va='center', fontsize=20, weight='bold', color=INK)
ax.text(cx, cy - .3, 'use time', ha='center', va='center', fontsize=10.5, color=MUTED)
for (label, col), xx in zip([('learned', LEARNED), ('fixed', FIXED), ('none', NONE)], (cx - 1.25, cx - .2, cx + .6)):
    ax.add_patch(Circle((xx, .52), .08, facecolor=col, edgecolor='#B8C2CD' if col == NONE else col, lw=.8))
    ax.text(xx + .14, .52, label, va='center', fontsize=10.5, color=INK)
arrow(8.4, 8.9)

# 4. Research-gap clusters.
names = {'C1': 'Data\ninfrastructure', 'C2': 'Modeling &\nlearning', 'C3': 'Clinical\ndeployment', 'C4': 'Outcome &\nreporting'}
r, d, vx, vy = .95, .64, 10.45, 2.4
centres = {'C1': (vx - d, vy + d), 'C2': (vx + d, vy + d), 'C3': (vx - d, vy - d), 'C4': (vx + d, vy - d)}
for k, (x, y) in centres.items():
    c = colours[k]
    ax.add_patch(Circle((x, y), r, facecolor=c['fill'], edgecolor=c['edge'], alpha=.55, lw=1.2))
push = {'C1': (-1, 1), 'C2': (1, 1), 'C3': (-1, -1), 'C4': (1, -1)}
for k, (x, y) in centres.items():
    c = colours[k]
    sx, sy = push[k]
    tx, ty = x + .3 * sx, y + .3 * sy
    ax.text(tx, ty + .13, names[k], ha='center', va='center', fontsize=9.8, weight='bold', color=c['txt'], linespacing=1.05)
    ax.text(tx, ty - .27, ' '.join(g[0] for g in clusters[k]['gaps']), ha='center', va='center', fontsize=8.5, color=c['txt'])
caption(vx, f'{gap_total} research gaps')

for ext in ('pdf', 'png'):
    fig.savefig(ROOT / f'graphical_abstract.{ext}', dpi=300, facecolor='white')
plt.close(fig)
print(f'{screened} screened, {studies} studies; learned {learned}, fixed {fixed}, none/not stated {rest}; {gap_total} gaps')
