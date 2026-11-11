"""Replot the completed 44-configuration M4 experiment without resampling.

Example: python3 scripts/plot_results.py --output results/figures/large-02-r1-viz-01
Requires Matplotlib and an existing Chinese font; no installation or font copying.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import platform
import random
import subprocess
from datetime import datetime, timezone

from analyze_large import summarize
from benchmark import require

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREFIX = ROOT/'results/performance/large-02-r1/m4-diagnostic-02-r1'
COLORS = {'serial': '#737373', 'mpi': '#2166ac', 'openmp': '#d66a16'}
NAMES = {'serial': '串行（1 CPU）', 'mpi': 'MPI', 'openmp': 'OpenMP'}
MARKERS = {'serial': 'D', 'mpi': 'o', 'openmp': 's'}
WORKERS = [1, 2, 4, 8, 16]
FOOTER = ('固定单位区域，T=0.01，α=1；N增大时M=N²/16也增大，跨N比较不是弱扩展。\n'
          '16个执行单元使用14个WSL可见core上的16逻辑CPU，含共享硬件线程；非16个独立物理核心。\n'
          '单机非独占WSL2；UTC有回退、存在轮次趋势；保留全部慢样本，未独立校准外部物理时钟。')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(prefix):
    manifest = json.loads(Path(str(prefix)+'.json').read_text())
    records = [json.loads(line) for line in Path(str(prefix)+'.jsonl').read_text().splitlines()]
    rows, groups = summarize(manifest, records)
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    require(buffer.getvalue().encode() == Path(str(prefix)+'.csv').read_bytes(), 'archived statistics differ')
    require(len(rows) == 44 and sum(len(g)-1 for g in groups.values()) == 440, 'coverage mismatch')
    return manifest, rows, groups


def configure_font(font):
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import font_manager
    from matplotlib.ft2font import FT2Font
    require(font.is_file(), 'Chinese font not found; specify --font')
    face = FT2Font(str(font))
    required = set(FOOTER+'串行网格划分数耗时中位数最小最大加速比效率吞吐量每秒内点更新原始样本逐轮归一化参考实际探索性区间人数')
    require(all(ord(ch) in face.get_charmap() for ch in required if not ch.isspace()), 'font lacks required glyphs')
    font_manager.fontManager.addfont(str(font))
    matplotlib.rcParams.update({'font.family': face.family_name, 'font.size': 11,
        'axes.titlesize': 12, 'axes.labelsize': 11, 'legend.fontsize': 9,
        'svg.fonttype': 'path', 'svg.hashsalt': 'm4-large-viz-01', 'axes.unicode_minus': False})
    return matplotlib, face.family_name


def generate(prefix, output, font):
    require(not output.exists(), 'output directory already exists; refusing overwrite')
    manifest, rows, groups = load(prefix)
    matplotlib, family = configure_font(font)
    import matplotlib.pyplot as plt
    from matplotlib.ticker import ScalarFormatter, PercentFormatter
    ns = sorted({r['N'] for r in rows})
    charts = []

    def panel_grid(title, shape=(2, 2), size=(13, 9)):
        fig, axes = plt.subplots(*shape, figsize=size, squeeze=False)
        fig.subplots_adjust(left=.085, right=.97, top=.85, bottom=.20, hspace=.62, wspace=.29)
        fig.suptitle(title, fontsize=17, y=.97)
        fig.text(.5, .025, FOOTER, ha='center', va='bottom', fontsize=9, color='#555555', linespacing=1.6)
        return fig, list(axes.flat)

    def finish(fig, filename, covered, note):
        fig.text(.5, .91, note, ha='center', fontsize=10)
        for suffix in ('.svg', '.png'):
            fig.savefig(output/(filename+suffix), dpi=160, metadata={'Creator': 'scripts/plot_results.py'}
                        if suffix == '.svg' else {'Software': 'scripts/plot_results.py'})
            if suffix == '.svg':
                path = output/(filename+suffix)
                path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
        plt.close(fig)
        charts.append(dict(name=filename, configurations=[r['id'] for r in covered], note=note))

    def series(ax, group, xkey, metric, low=None, high=None, scale=1., label=None, color=None):
        kind = group[0]['kind']
        x = [r[xkey] for r in group]
        c = color or COLORS[kind]
        ax.plot(x, [r[metric]*scale for r in group], color=c, marker=MARKERS[kind],
                label=label or NAMES[kind], linewidth=1.8, markersize=5)
        if low:
            # Percentile intervals need not contain the point estimate.
            ax.vlines(x, [r[low]*scale for r in group], [r[high]*scale for r in group], color=c, alpha=.8)
            ax.plot(x, [r[low]*scale for r in group], '_', color=c)
            ax.plot(x, [r[high]*scale for r in group], '_', color=c)

    def decorate(ax):
        ax.grid(alpha=.22)
        ax.set_axisbelow(True)
        ax.legend(loc='best')

    output.mkdir(parents=True, exist_ok=False)
    for filename, title, metric, low, high, ylabel in [
        ('01-time', '固定网格：三种求解器的推进耗时', 'median_seconds', 'minimum_seconds', 'maximum_seconds', '推进耗时（秒）'),
        ('02-speedup', '固定网格：相对独立串行的加速比', 'speedup_serial', 'speedup_low', 'speedup_high', '加速比 S = 串行中位数 / 并行中位数'),
        ('03-efficiency', '固定网格：MPI与OpenMP的并行效率', 'efficiency', 'efficiency_low', 'efficiency_high', '效率 E = S / 实际P或Q')]:
        fig, axes = panel_grid(title)
        for ax, n in zip(axes, ns):
            sub = [r for r in rows if r['N'] == n]
            serial = next(r for r in sub if r['kind'] == 'serial')
            for kind in ('mpi', 'openmp'):
                series(ax, [r for r in sub if r['kind'] == kind], 'actual', metric, low, high)
            if metric == 'median_seconds':
                series(ax, [serial], 'actual', metric, low, high)
                ax.axhline(serial[metric], color=COLORS['serial'], linestyle=':', label='串行1CPU中位数参考')
            else:
                ax.scatter([1], [1], marker='D', color=COLORS['serial'], label='串行真实1CPU基准')
                ax.axhline(1, color=COLORS['serial'], linestyle=':', label='基准1' if metric == 'speedup_serial' else '100%理想参考')
            ax.set(title=f'N={n}，M={serial["M"]}', xlabel='实际P / Q（对数间距）', ylabel=ylabel,
                   xscale='log', xticks=WORKERS)
            ax.xaxis.set_major_formatter(ScalarFormatter())
            if metric == 'efficiency':
                ax.yaxis.set_major_formatter(PercentFormatter(1))
            ax.set_ylim(bottom=0)
            decorate(ax)
        finish(fig, filename, rows, '每配置10次；点为中位数，竖线为min/max范围' if metric == 'median_seconds' else
               '每配置10次；点为中位数之比，竖线为同轮bootstrap探索性95%区间；未作多重比较校正')

    for filename, metric, low, high, title, ylabel in [
        ('04-grid-time', 'median_seconds', 'minimum_seconds', 'maximum_seconds', '固定人数：推进耗时随网格数量变化', '推进耗时（秒，对数坐标）'),
        ('05-grid-speedup', 'speedup_serial', 'speedup_low', 'speedup_high', '固定人数：加速比随网格数量变化', '相对同网格独立串行的加速比'),
        ('06-grid-throughput', 'updates_per_second', None, None, '固定人数：三种求解器的更新吞吐', '内点更新量（十亿次/秒）')]:
        fig, axes = panel_grid(title, (2, 3), (16, 10))
        for ax, p in zip(axes, WORKERS):
            for kind in ('serial', 'mpi', 'openmp'):
                selected = [r for r in rows if r['kind'] == kind and (kind == 'serial' or r['actual'] == p)]
                label = '串行1CPU（固定参考）' if kind == 'serial' and p > 1 else NAMES[kind]
                series(ax, selected, 'N', metric, low, high, 1e-9 if metric == 'updates_per_second' else 1., label)
                if metric == 'updates_per_second':
                    ax.vlines(ns, [r['updates']/r['maximum_seconds']*1e-9 for r in selected],
                              [r['updates']/r['minimum_seconds']*1e-9 for r in selected], color=COLORS[kind], alpha=.7)
            ax.set(title=f'MPI P={p} / OpenMP Q={p}'+('（含共享硬件线程）' if p == 16 else ''),
                   xlabel='每边划分数N；M=N²/16', ylabel=ylabel, xticks=ns)
            if metric == 'median_seconds':
                ax.set_yscale('log')
            else:
                ax.set_ylim(bottom=0)
            decorate(ax)
        note_ax = axes[5]
        note_ax.axis('off')
        note_ax.text(.05, .9, '串行始终只用1 CPU。\n多人数面板重复同网格串行参考，\n不是新增串行样本。\n\nW=M(N−1)²；吞吐=W/推进时间。\nN与M联合增加，不能把差异\n单独归因于每步网格大小。', va='top', fontsize=12, linespacing=1.8)
        finish(fig, filename, rows, '竖线为同轮bootstrap探索性95%区间；无多重比较校正' if metric == 'speedup_serial' else
               '每配置10次；竖线由实际min/max耗时计算，全部慢样本保留')

    fig, axes = panel_grid('全部440个正式样本：原始推进耗时与中位数', size=(16, 10))
    jitter = random.Random(20261110)
    raw_points = 0
    for ax, n in zip(axes, ns):
        sub = [r for r in rows if r['N'] == n]
        for index, row in enumerate(sub):
            times = [groups[row['id']][rep]['summary']['loop_seconds'] for rep in range(1, 11)]
            ax.scatter([index+jitter.uniform(-.16, .16) for _ in times], times,
                       color=COLORS[row['kind']], alpha=.65, s=20)
            ax.plot([index-.28, index+.28], [row['median_seconds']]*2, color=COLORS[row['kind']], linewidth=2.5)
            raw_points += len(times)
        labels = ['串行1']+[f'{NAMES[k]}{p}' for k in ('mpi', 'openmp') for p in WORKERS]
        ax.set(title=f'N={n}', xlabel='实现与实际P/Q（串行恒为1）', ylabel='原始推进耗时（秒）', xticks=range(11), xticklabels=labels)
        ax.tick_params(axis='x', labelrotation=45, labelsize=9)
        ax.grid(axis='y', alpha=.2)
        ax.set_ylim(bottom=0)
    require(raw_points == 440, 'raw plot must include every sample')
    finish(fig, '07-samples', rows, '每个点代表一次新进程正式样本；短横线为配置中位数；仅横向确定性抖动，未改变耗时')
    charts[-1]['raw_sample_points'] = raw_points

    for kind, filename in [('mpi', '08-rounds-mpi'), ('openmp', '09-rounds-openmp')]:
        fig, axes = panel_grid(NAMES[kind]+'与串行参考：逐轮波动', size=(14, 10))
        selected = [r for r in rows if r['kind'] in ('serial', kind)]
        shades = plt.get_cmap('Blues' if kind == 'mpi' else 'Oranges')
        for ax, n in zip(axes, ns):
            for row in [r for r in selected if r['N'] == n]:
                serial = row['kind'] == 'serial'
                color = COLORS['serial'] if serial else shades(.4+.55*WORKERS.index(row['actual'])/4)
                times = [groups[row['id']][rep]['summary']['loop_seconds']/row['median_seconds'] for rep in range(1, 11)]
                ax.plot(range(1, 11), times, marker='D' if serial else ['o','s','^','v','X'][WORKERS.index(row['actual'])],
                        color=color, label=NAMES['serial'] if serial else NAMES[kind]+f' {row["actual"]}', linewidth=1.3, markersize=4)
            ax.axhline(1, color='#aaaaaa', linestyle=':', linewidth=1)
            ax.set(title=f'N={n}', xlabel='打乱配置顺序的采样轮次', ylabel='本次耗时 / 该配置10次中位数', xticks=range(1, 11))
            decorate(ax)
        finish(fig, filename, selected, '每条线以自身中位数归一化，只反映轮次变化；不能用曲线高低比较求解器绝对速度')
        charts[-1]['raw_sample_points'] = 240

    # Copy frozen statistics, without rewriting their floating-point representation.
    (output/'statistics.csv').write_bytes(Path(str(prefix)+'.csv').read_bytes())
    inputs = {str(Path(str(prefix)+suffix).relative_to(ROOT)): sha(Path(str(prefix)+suffix))
              for suffix in ('.json', '.jsonl', '.csv')}
    generation = dict(schema=1, generated_utc=datetime.now(timezone.utc).isoformat(),
        generation_revision=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        sampling_revision=manifest['revision'], inputs=inputs,
        script_sha256={str(p.relative_to(ROOT)): sha(p) for p in
                       [Path(__file__).resolve(), ROOT/'scripts/analyze_large.py', ROOT/'scripts/benchmark_large.py', ROOT/'scripts/benchmark.py']},
        font=dict(path=str(font.resolve()), family=family, sha256=sha(font), svg_fonttype='path'),
        versions=dict(python=platform.python_version(), matplotlib=matplotlib.__version__),
        configuration_count=44, measured_samples=440, seed=20261110,
        statistics='Unchanged archived CSV; ratio of medians; 10000 common-round bootstrap draws, indices249/9749',
        charts=charts, limitations=FOOTER)
    (output/'generation.json').write_text(json.dumps(generation, indent=2, ensure_ascii=False)+'\n')
    files = sorted(p for p in output.iterdir() if p.is_file())
    (output/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files))
    print(f'Generated {len(charts)} SVG/PNG pairs, 44 configurations, {raw_points} raw samples in {output}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, default=DEFAULT_PREFIX)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--font', type=Path, default=Path('/mnt/c/Windows/Fonts/msyh.ttc'))
    args = parser.parse_args()
    generate(args.prefix.resolve(), args.output, args.font)


if __name__ == '__main__':
    main()
