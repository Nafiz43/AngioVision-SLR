"""Build the submission graphical abstract: python3 analysis/11_graphical_abstract.py.

Read counts and colours from the full Venn figure without executing its plotting
code. Circle overlap is schematic, not a quantitative set intersection.
"""
import ast
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

ROOT = Path(__file__).resolve().parents[1]
source = ast.parse((ROOT / 'analysis/09_venn_diagram.py').read_text())
namespace = {}
for node in source.body:
    if isinstance(node, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id in {'CLUSTERS', 'STRATEGIES', 'COLOURS'}
        for t in node.targets
    ):
        if node.targets[0].id == 'COLOURS':
            namespace['COLOURS'] = {ast.literal_eval(k): {kw.arg: ast.literal_eval(kw.value) for kw in v.keywords} for k, v in zip(node.value.keys, node.value.values)}
        else:
            namespace[node.targets[0].id] = ast.literal_eval(node.value)
clusters, strategies, colours = (namespace[k] for k in ('CLUSTERS', 'STRATEGIES', 'COLOURS'))
gap_count = sum(len(c['gaps']) for c in clusters.values())
assert len({g[0] for c in clusters.values() for g in c['gaps']}) == gap_count
assert len({s[0] for s in strategies}) == len(strategies)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
fig, ax = plt.subplots(figsize=(7.5, 4.5))
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
ax.set(xlim=(0, 7.5), ylim=(0, 4.5), aspect='equal')
ax.axis('off')
ax.text(.35, 4.12, 'AI for angiographic sequence analysis', fontsize=17, weight='bold', color='#192637')
ax.text(.35, 3.78, 'A systematic literature review', fontsize=11, color='#526170')
for y, number, label in [(2.94, '120', 'included studies'), (1.98, str(gap_count), 'research gaps'), (1.02, str(len(strategies)), 'mitigation strategies')]:
    ax.text(.40, y, number, fontsize=30, weight='bold', color='#192637')
    ax.text(.42, y-.29, label, fontsize=11, color='#526170')
positions = {'C1': (4.10, 2.55), 'C2': (5.55, 2.55), 'C3': (4.10, 1.10), 'C4': (5.55, 1.10)}
names = {'C1': 'Data\ninfrastructure', 'C2': 'Modeling &\nlearning', 'C3': 'Clinical\ndeployment', 'C4': 'Outcome &\nreporting'}
for key, (x, y) in positions.items():
    c = colours[key]
    ax.add_patch(Circle((x, y), 1.04, facecolor=c['fill'], edgecolor=c['edge'], alpha=.60, lw=1.5))
for key, (x, y) in positions.items():
    c = colours[key]
    ax.text(x, y+.16, names[key], ha='center', va='center', fontsize=12, weight='bold', color=c['txt'], linespacing=1.2)
    ax.text(x, y-.32, f"{len(clusters[key]['gaps'])} gaps", ha='center', va='center', fontsize=13, color=c['txt'])
ax.text(4.825, 1.825, '4 clusters', ha='center', va='center', fontsize=11, weight='bold', color='#192637', bbox=dict(boxstyle='round,pad=.4', facecolor='white', edgecolor='none'))
# Separate submission artifact; retain the detailed Venn figure in the article.
for ext in ('pdf', 'png'):
    fig.savefig(ROOT / f'graphical_abstract.{ext}', dpi=300, facecolor='white')
plt.close(fig)
print(f'{gap_count} research gaps; {len(strategies)} mitigation strategies; 2250 x 1350 px PNG')
