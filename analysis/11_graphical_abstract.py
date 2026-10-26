"""Build the submission graphical abstract: python3 analysis/11_graphical_abstract.py.

Three panels: study selection, temporal modeling, research-gap clusters. Every count is
read from the committed data (screening CSVs, extraction/out, the Venn cluster table).
Output: graphical_abstract.{pdf,png}, 13 x 5 in (3900 x 1500 px), Elsevier's 13:5 format.
"""
import ast
import csv
import glob
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]

# Gap clusters and colours from the Venn script, without executing its plotting code.
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

# Study selection.
screened = sum(1 for _ in csv.DictReader(open(ROOT / 'screening/stage1_llm_decisions.csv')))
eligible = sum(1 for _ in csv.DictReader(open(ROOT / 'extraction/manifest.csv')))
rows = list(csv.DictReader(open(ROOT / 'screening/screening_double_annotation.csv')))
a = [r['rater_REG'].strip().lower() == 'include' for r in rows]
b = [r['rater_NIK'].strip().lower() == 'include' for r in rows]
n = len(rows)
po = sum(x == y for x, y in zip(a, b)) / n
pe = (sum(a) / n) * (sum(b) / n) + (1 - sum(a) / n) * (1 - sum(b) / n)
kappa = (po - pe) / (1 - pe)

# Temporal modeling.
cats = [json.load(open(f))['method'].get('temporal_category') for f in glob.glob(str(ROOT / 'extraction/out/R*.json'))]
studies = len(cats)
LEARNED = {'recurrent', 'cnn3d_video', 'transformer_ssm'}
FIXED = {'frame_aggregation', 'optical_flow_registration', 'hemodynamic_physics'}
learned = sum(c in LEARNED for c in cats)
fixed = sum(c in FIXED for c in cats)
none = sum(c == 'none' for c in cats)
other = studies - learned - fixed - none
transformer = sum(c == 'transformer_ssm' for c in cats)
assert learned + fixed + none + other == studies

INK, MUTED, RULE = '#192637', '#5B6876', '#D5DAE0'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
W, H = 13.0, 5.0
fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set(xlim=(0, W), ylim=(0, H))
ax.axis('off')

# Header.
ax.text(.35, 4.55, 'AI for angiographic sequence analysis', fontsize=19, weight='bold', color=INK, va='center')
ax.text(.35, 4.17, f'Systematic review of {studies} studies (PRISMA 2020)', fontsize=11.5, color=MUTED, va='center')
for x in (4.15, 8.45):
    ax.plot([x, x], [.35, 3.75], color=RULE, lw=1)


def heading(x, text):
    ax.text(x, 3.62, text, fontsize=12.5, weight='bold', color=INK, va='center')


# Panel 1: study selection funnel.
heading(.35, 'Study selection')
steps = [(f'{screened:,}', 'records screened'), (f'{eligible}', 'eligible'), (f'{studies}', 'included')]
widths = [3.45, 2.7, 1.95]
for i, ((num, lab), w) in enumerate(zip(steps, widths)):
    y = 2.8 - i * .82
    x0 = .35 + (3.45 - w) / 2
    ax.add_patch(FancyBboxPatch((x0, y - .27), w, .54, boxstyle='round,pad=0,rounding_size=.08',
                                facecolor=['#E8EDF3', '#D3DDE8', '#B9C9DA'][i], edgecolor='none'))
    ax.text(x0 + w / 2, y, f'{num}  {lab}', ha='center', va='center', fontsize=12, color=INK,
            weight='bold' if i == 2 else 'normal')
ax.text(2.075, .55, f'LLM screening, validated by two blinded\nhuman reviewers (Cohen\'s $\\kappa$ = {kappa:.2f})',
        ha='center', va='center', fontsize=9.5, color=MUTED, linespacing=1.35)

# Panel 2: temporal modeling bar.
heading(4.55, 'How studies model time')
ax.text(4.55, 3.12, f'{(learned + fixed) / studies:.1%}'.replace('.', '.', 1), fontsize=30, weight='bold', color=INK, va='center')
ax.text(6.05, 3.12, 'link information\nacross frames', fontsize=11, color=MUTED, va='center', linespacing=1.3)
segs = [(learned, 'Learned', '#3E6E9E'), (fixed, 'Fixed', '#9DB7D1'), (none + other, 'None or\nnot stated', '#E3E7EC')]
x, bw = 4.55, 3.55
for count, label, col in segs:
    w = bw * count / studies
    ax.add_patch(Rectangle((x, 2.0), w, .48, facecolor=col, edgecolor='white', lw=1.5))
    ax.text(x + w / 2, 2.24, str(count), ha='center', va='center', fontsize=11, weight='bold',
            color='white' if col == '#3E6E9E' else INK)
    ax.text(x + w / 2, 1.88, label, ha='center', va='top', fontsize=10, color=MUTED, linespacing=1.1)
    x += w
ax.text(4.55, 1.08, f'Of these, half rely on fixed operations such as stacking,\nregistration or curve fitting. Only {transformer / studies:.1%} use\nTransformer or state-space models, all since 2023.',
        fontsize=9.8, color=INK, va='center', linespacing=1.4)

# Panel 3: research-gap clusters.
gap_total = sum(len(c['gaps']) for c in clusters.values())
heading(8.85, f'{gap_total} research gaps in {len(clusters)} clusters')
SHORT = {'G1': 'No public benchmarks', 'G2': 'Generalizability', 'G3': 'Temporal modeling',
         'G4': '2D constraints', 'G5': 'Annotation scarcity', 'G6': 'Clinical validation',
         'G7': 'Explainability', 'G8': 'Multi-modal integration', 'G9': 'Class imbalance',
         'G10': 'Privacy-preserving', 'G11': 'Outcome prediction', 'G12': 'LLMs & reporting'}
names = {'C1': 'Data infrastructure', 'C2': 'Modeling & learning', 'C3': 'Clinical deployment', 'C4': 'Outcome & reporting'}
tile_w, tile_h = 1.93, 1.36
for i, key in enumerate(['C1', 'C2', 'C3', 'C4']):
    tx = 8.85 + (i % 2) * (tile_w + .12)
    ty = 1.88 - (i // 2) * (tile_h + .12)
    c = colours[key]
    ax.add_patch(FancyBboxPatch((tx, ty), tile_w, tile_h, boxstyle='round,pad=0,rounding_size=.07',
                                facecolor=c['fill'], edgecolor='none', alpha=.75))
    ax.text(tx + .12, ty + tile_h - .2, names[key], fontsize=10.5, weight='bold', color=c['txt'], va='center')
    for j, (code, label) in enumerate(clusters[key]['gaps']):
        short = SHORT.get(code) or ' '.join(label.replace('\n', ' ').split())
        ax.text(tx + .12, ty + tile_h - .5 - j * .23, f'{code}  {short}', fontsize=8.3, color=c['txt'], va='center')

for ext in ('pdf', 'png'):
    fig.savefig(ROOT / f'graphical_abstract.{ext}', dpi=300, facecolor='white')
plt.close(fig)
print(f'{screened} screened, {eligible} eligible, {studies} included, kappa {kappa:.3f}; '
      f'learned {learned}, fixed {fixed}, none {none}, other {other}; {gap_total} gaps')
