"""Validate M4 evidence, recompute statistics and export Matplotlib figures.

Standard library suffices for --no-plots. Plotting requires Matplotlib.
Error bars are observed minimum/maximum, not confidence intervals.
"""
import argparse
from collections import defaultdict
import csv
import json
import math
from pathlib import Path
import statistics

from benchmark import configurations, parse_summary, require


def analyze(directory):
    metadata = json.loads((directory / 'metadata.json').read_text())
    protocol = metadata['protocol']
    complete = json.loads((directory / 'complete.json').read_text())
    expected = configurations(protocol)
    require(json.loads((directory / 'matrix.json').read_text()) == expected, 'matrix mismatch')
    rows = [json.loads(line) for line in (directory / 'samples.jsonl').read_text().splitlines()]
    groups, validations, errors = defaultdict(dict), {}, defaultdict(list)
    for row in rows:
        if 'validation' in row:
            key = row['validation']
            require(key not in validations, 'duplicate validation')
            require(row['D_inf'] <= 1e-12 and row['discrete_mode_diff'] < 2e-11 and
                    row['E_inf'] <= 2e-5, 'failed numerical validation')
            validations[key] = row
            continue
        config = row['config']
        key, rep = config['id'], row['repetition']
        require(0 <= key < len(expected) and config == expected[key], 'unexpected config')
        require(rep not in groups[key] and row['warmup'] == (rep == 0), 'duplicate sample')
        require(row['returncode'] == 0 and row['revision'] == metadata['revision'], 'invalid run')
        d = parse_summary(row['stderr'])
        require(all(d[k] == config[k] for k in ('N', 'M', 'T', 'alpha')), 'parameter mismatch')
        require(0 < d['r'] <= .25 and math.isfinite(d['E_inf']) and d['E_inf'] <= 2e-5, 'invalid error/r')
        actual = int(d.get('P_actual', d.get('Q_actual', 1)))
        require(actual == config['p'] and int(d.get('Q_requested', actual)) == actual, 'team mismatch')
        require(math.isfinite(d['loop_seconds']) and d['loop_seconds'] > 0, 'invalid time')
        groups[key][rep] = d['loop_seconds']
        errors[key].append(d['E_inf'])
    count = protocol['repetitions']
    require(len(groups) == len(validations) == len(expected), 'missing configurations/validations')
    require(complete['measured_samples'] == len(expected)*count and
            complete['source_and_binary_hashes_unchanged'], 'incomplete run')
    result = []
    for config in expected:
        require(all(abs(error-validations[config['id']]['E_inf']) < 1e-14
                    for error in errors[config['id']]), 'sample/warmup error mismatch')
        samples = groups[config['id']]
        require(set(samples) == set(range(count+1)), 'missing repetition')
        times = [samples[i] for i in range(1, count+1)]
        w = config['M']*(config['N']-1)**2
        result.append(dict(**config, requested=config['p'], actual=config['p'],
                           r=config['alpha']*config['T']*config['N']**2/config['M'], updates=w,
                           updates_per_worker=w/config['p'],
                           min_worker_updates=config['M']*(config['N']-1)*((config['N']-1)//config['p']),
                           max_worker_updates=config['M']*(config['N']-1)*((config['N']-2)//config['p']+1),
                           repeats=count,
                           median_seconds=statistics.median(times), min_seconds=min(times),
                           max_seconds=max(times)))
    serial = {(r['suite'], r['N'], r['M']): r for r in result if r['kind'] == 'serial'}
    for r in result:
        ts = serial[r['suite'], r['N'], r['M']]['median_seconds']
        r['speedup_serial'] = ts/r['median_seconds']
        r['efficiency_serial'] = r['speedup_serial']/r['actual']
        r['updates_per_second'] = r['updates']/r['median_seconds']
        r['amdahl_effective_fraction'] = ((r['actual']/r['speedup_serial']-1)/(r['actual']-1)
                                          if r['suite'] == 'strong' and r['actual'] > 1 else '')
        r['work_ratio'] = r['throughput_ratio_own_p1'] = r['normalized_scaled_efficiency'] = ''
        if r['suite'] == 'scaled':
            base = next(b for b in result if b['suite'] == 'scaled' and b['kind'] == r['kind']
                        and b['target_p'] == 1)
            r['work_ratio'] = r['updates']/base['updates']
            r['throughput_ratio_own_p1'] = r['work_ratio']*base['median_seconds']/r['median_seconds']
            r['normalized_scaled_efficiency'] = r['throughput_ratio_own_p1']/r['target_p']
    return result


def plot(rows, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'svg.fonttype': 'none', 'font.size': 10})
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), constrained_layout=True)
    for index, n in enumerate(sorted({r['N'] for r in rows if r['suite'] == 'strong'})):
        selected = [r for r in rows if r['suite'] == 'strong' and r['N'] == n]
        baseline = next(r for r in selected if r['kind'] == 'serial')
        for kind, marker in [('mpi', 'o'), ('openmp', 's')]:
            group = sorted((r for r in selected if r['kind'] == kind), key=lambda r: r['actual'])
            p = [r['actual'] for r in group]
            med = [r['median_seconds'] for r in group]
            axes[index, 0].errorbar(p, med, yerr=[[r['median_seconds']-r['min_seconds'] for r in group],
                                                [r['max_seconds']-r['median_seconds'] for r in group]],
                                   marker=marker, capsize=3, label=kind)
            for col, key in [(1, 'speedup_serial'), (2, 'efficiency_serial')]:
                axes[index, col].plot(p, [r[key] for r in group], marker=marker, label=kind)
        axes[index, 0].axhline(baseline['median_seconds'], color='grey', linestyle=':', label='serial')
        axes[index, 1].plot([1, 2, 4], [1, 2, 4], '--', color='grey', label='ideal')
        axes[index, 2].axhline(1, color='grey', linestyle='--', label='ideal')
        for ax, ylabel in zip(axes[index], ['Loop wall time (s), median [min,max]', 'Speedup vs independent serial', 'Efficiency vs independent serial']):
            ax.set(title=f'N={n}, M={baseline["M"]}', xlabel='Actual P / Q', ylabel=ylabel, xticks=[1, 2, 4])
            ax.grid(alpha=.25); ax.legend()
    fig.savefig(output / 'strong.svg'); fig.savefig(output / 'strong.png', dpi=160); plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.7), constrained_layout=True)
    for kind, marker in [('serial', '^'), ('mpi', 'o'), ('openmp', 's')]:
        group = sorted((r for r in rows if r['suite'] == 'scaled' and r['kind'] == kind), key=lambda r: r['target_p'])
        p = [r['target_p'] for r in group]
        axes[0].errorbar(p, [r['median_seconds'] for r in group],
                         yerr=[[r['median_seconds']-r['min_seconds'] for r in group],
                               [r['max_seconds']-r['median_seconds'] for r in group]], marker=marker, capsize=3, label=kind)
        for ax, key in zip(axes[1:], ['throughput_ratio_own_p1', 'normalized_scaled_efficiency']):
            ax.plot(p, [r[key] for r in group], marker=marker, label=kind)
    axes[1].plot([1, 2, 4], [1, 2, 4], '--', color='grey', label='ideal proportional work')
    axes[2].axhline(1, color='grey', linestyle='--')
    for ax, ylabel in zip(axes, ['Loop wall time (s), median [min,max]', 'Throughput / own base-grid throughput', 'Throughput ratio / target parallelism']):
        ax.set(xlabel='Target P / Q (serial always uses 1 CPU)', ylabel=ylabel, xticks=[1, 2, 4])
        ax.grid(alpha=.25); ax.legend()
    fig.savefig(output / 'scaled.svg'); fig.savefig(output / 'scaled.png', dpi=160); plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--no-plots', action='store_true')
    a = parser.parse_args()
    rows = analyze(a.directory)
    a.output.mkdir(parents=True, exist_ok=True)
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with (a.output / 'summary.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader(); writer.writerows(rows)
    if not a.no_plots:
        plot(rows, a.output)
    print(f'Validated {len(rows)} configurations; summary written to {a.output}')


if __name__ == '__main__':
    main()
