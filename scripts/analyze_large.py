"""Validate original-solver M4 large-grid records and derive reproducible statistics."""
import argparse
from collections import defaultdict
import csv
import json
import math
from pathlib import Path
import random
import statistics

from benchmark import parse_summary, require
from benchmark_large import configurations, mpi_bindings, validate_summary, SEED, REPEATS


def speedup_interval(serial, parallel):
    require(len(serial) == len(parallel) == REPEATS, 'ten matching rounds required')
    require(all(math.isfinite(v) and v > 0 for v in serial+parallel), 'invalid bootstrap time')
    rng = random.Random(SEED)
    draws = []
    for _ in range(10000):
        indices = rng.choices(range(REPEATS), k=REPEATS)
        draws.append(statistics.median(serial[i] for i in indices)/
                     statistics.median(parallel[i] for i in indices))
    draws.sort()
    return draws[249], draws[9749]


def validate_records(manifest, records):
    require(manifest['schema'] == 'm4-large-v1' and manifest['complete'], 'incomplete/wrong experiment')
    require(manifest['matrix'] == configurations() and manifest['seed'] == SEED and
            manifest['repeats'] == REPEATS and manifest['warmups'] == 1, 'protocol mismatch')
    require(manifest['source_and_binary_unchanged'], 'sampling identity changed')
    require((manifest['invocations'], manifest['measured'], manifest['warmup_invocations']) == (484, 440, 44),
            'manifest counts mismatch')
    attempts = [r for r in records if r['type'] == 'attempt']
    samples = [r for r in records if r['type'] == 'sample']
    require(len(attempts) == len(samples) == 484 and len(records) == 968, 'attempt/sample counts mismatch')
    require([r['id'] for r in samples] == list(range(484)), 'invocation identity/order mismatch')
    for a, b in zip(attempts, samples):
        require(a['id'] == b['id'] and all(a[k] == b[k] for k in a if k != 'type'), 'attempt/sample mismatch')
    require(all(records[2*i]['type'] == 'attempt' and records[2*i+1]['type'] == 'sample'
                for i in range(484)), 'journal order mismatch')
    for a, b in zip(samples, samples[1:]):
        require(a['mono_end_ns'] <= b['mono_start_ns'], 'overlapping invocations')
    expected = configurations()
    require([r['config'] for r in samples[:44]] == expected and all(r['warmup'] for r in samples[:44]),
            'warmup order mismatch')
    rng = random.Random(SEED)
    for rep in range(1, 11):
        order = list(expected)
        rng.shuffle(order)
        block = samples[44+(rep-1)*44:44+rep*44]
        require([r['config'] for r in block] == order and
                all(r['repetition'] == rep and not r['warmup'] for r in block), 'seeded round mismatch')
    groups = defaultdict(dict)
    for row in samples:
        c, d = row['config'], row['summary']
        require(c in expected and row['revision'] == manifest['revision'], 'config/revision mismatch')
        require(row['returncode'] == 0 and not row['timed_out'], 'failed invocation')
        require(row['mono_start_ns'] <= row['mono_end_ns'], 'reversed time')
        require(row['binding'] is None or row['mono_start_ns'] <= row['binding']['mono_ns'] <= row['mono_end_ns'],
                'affinity snapshot outside invocation')
        require(parse_summary(row['stderr']) == d, 'raw/parsed summary mismatch')
        validate_summary(c, d)
        if c['kind'] == 'mpi':
            require(mpi_bindings(row['stderr'], c['cpus']) ==
                    {int(k): v for k, v in row['mpi_bindings'].items()}, 'recorded MPI bindings mismatch')
        else:
            require(row['binding'] is not None and sorted(row['binding']['affinity']) == [[x] for x in c['cpus']] and
                    len(row['binding']['tids']) == c['p'], 'missing/wrong actual task binding')
        require(row['tuning']['OMP_THREAD_LIMIT'] == '16' and row['tuning']['OMP_WAIT_POLICY'] == 'ACTIVE' and
                row['tuning']['OMP_DYNAMIC'] == 'FALSE' and row['tuning']['OMP_PROC_BIND'] == 'close' and
                row['tuning']['OMP_PLACES'] == ','.join('{%d}' % x for x in c['cpus']), 'tuning mismatch')
        require(row['tuning']['OMP_DISPLAY_AFFINITY'] ==
                ('TRUE' if row['warmup'] and c['kind'] == 'openmp' else 'FALSE'), 'affinity output policy mismatch')
        rep = row['repetition']
        require(rep not in groups[c['id']] and row['warmup'] == (rep == 0), 'duplicate sample')
        groups[c['id']][rep] = row
    for c in expected:
        group = groups[c['id']]
        require(set(group) == set(range(11)), 'missing repetition')
        warm = group[0]
        v = warm['validation']
        gain = 1-8*warm['summary']['r']*math.sin(math.pi/(2*c['N']))**2
        bound = abs(gain**c['M']-math.exp(-2*c['alpha']*math.pi**2*c['T']))+2e-11
        require(v['nodes'] == (c['N']+1)**2 and v['D_inf'] <= 1e-12 and v['mode_diff'] < 2e-11 and
                v['E_inf'] <= v['truncation_bound'] and abs(v['truncation_bound']-bound) < 1e-15 and
                abs(v['E_inf']-warm['summary']['E_inf']) < 1e-14,
                'full field validation mismatch')
        for row in group.values():
            require(abs(row['summary']['E_inf']-v['E_inf']) < 1e-14, 'sample/warmup error differs')
            require(row['warmup'] or row['stdout_bytes'] == 0, 'unexpected timed stdout')
    return groups


def summarize(manifest, records):
    groups = validate_records(manifest, records)
    serial = {c['N']: [groups[c['id']][i]['summary']['loop_seconds'] for i in range(1, 11)]
              for c in manifest['matrix'] if c['kind'] == 'serial'}
    result = []
    for c in manifest['matrix']:
        times = [groups[c['id']][i]['summary']['loop_seconds'] for i in range(1, 11)]
        median = statistics.median(times)
        speedup = statistics.median(serial[c['N']])/median
        low, high = (1., 1.) if c['kind'] == 'serial' else speedup_interval(serial[c['N']], times)
        work = c['M']*(c['N']-1)**2
        result.append(dict(id=c['id'], kind=c['kind'], requested=c['p'], actual=c['p'], N=c['N'], M=c['M'],
                           T=c['T'], alpha=c['alpha'], r=c['alpha']*c['T']*c['N']**2/c['M'],
                           cpus=','.join(map(str, c['cpus'])), visible_cores=len({x//2 for x in c['cpus']}),
                           uses_sibling_threads=c['p'] == 16, repeats=10, updates=work,
                           average_worker_updates=work/c['p'],
                           minimum_worker_updates=c['M']*(c['N']-1)*((c['N']-1)//c['p']),
                           maximum_worker_updates=c['M']*(c['N']-1)*((c['N']-2)//c['p']+1),
                           median_seconds=median, minimum_seconds=min(times), maximum_seconds=max(times),
                           speedup_serial=speedup, speedup_low=low, speedup_high=high,
                           efficiency=speedup/c['p'], efficiency_low=low/c['p'], efficiency_high=high/c['p'],
                           updates_per_second=work/median,
                           first_three_over_last_three=statistics.median(times[:3])/statistics.median(times[-3:])))
    return result, groups


def plots(rows, groups, prefix):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'svg.fonttype': 'none', 'font.size': 9})
    ns = sorted({r['N'] for r in rows})
    fig, axes = plt.subplots(4, 3, figsize=(14, 12), constrained_layout=True)
    for i, n in enumerate(ns):
        sub = [r for r in rows if r['N'] == n]
        baseline = next(r for r in sub if r['kind'] == 'serial')
        for kind, marker in [('mpi', 'o'), ('openmp', 's')]:
            group = [r for r in sub if r['kind'] == kind]
            p = [r['actual'] for r in group]
            axes[i, 0].errorbar(p, [r['median_seconds'] for r in group],
                yerr=[[r['median_seconds']-r['minimum_seconds'] for r in group],
                      [r['maximum_seconds']-r['median_seconds'] for r in group]], marker=marker, capsize=2, label=kind)
            for col, key, low, high in [(1, 'speedup_serial', 'speedup_low', 'speedup_high'),
                                        (2, 'efficiency', 'efficiency_low', 'efficiency_high')]:
                # Bootstrap percentile intervals need not contain the point estimate.
                line, = axes[i, col].plot(p, [r[key] for r in group], marker=marker, label=kind)
                axes[i, col].vlines(p, [r[low] for r in group], [r[high] for r in group], color=line.get_color())
        axes[i, 0].axhline(baseline['median_seconds'], color='grey', linestyle=':', label='serial')
        axes[i, 1].plot([1, 2, 4, 8, 16], [1, 2, 4, 8, 16], '--', color='grey', label='ideal worker scaling')
        axes[i, 2].axhline(1, color='grey', linestyle='--')
        for ax, label in zip(axes[i], ['Loop seconds: median [min,max]', 'Speedup: exploratory 95% interval', 'Efficiency: exploratory 95% interval']):
            ax.set(xlabel='Actual P / Q (16 includes sibling threads)', ylabel=label,
                   title=f'N={n}, M={baseline["M"]}', xscale='log', xticks=[1, 2, 4, 8, 16], xticklabels=[1, 2, 4, 8, 16])
            ax.grid(alpha=.2)
            ax.legend()
    fig.suptitle('Original solvers; 16 workers use 16 logical CPUs across 14 WSL-visible cores')
    save(fig, prefix, '-strong', plt)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
    for ax, kind in zip(axes, ('mpi', 'openmp')):
        for p in (1, 2, 4, 8, 16):
            group = [r for r in rows if r['kind'] == kind and r['actual'] == p]
            ax.plot([r['N'] for r in group], [r['speedup_serial'] for r in group], marker='o', label=f'{p} workers')
        ax.axhline(1, color='grey', linestyle='--')
        ax.set(title=kind, xlabel='N (M=N^2/16, T=0.01)', ylabel='Speedup vs same-grid independent serial', xticks=ns)
        ax.grid(alpha=.2)
        ax.legend()
    fig.suptitle('Grid refinement at fixed worker count; 16 includes sibling threads')
    save(fig, prefix, '-grid', plt)
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), constrained_layout=True)
    for ax, n in zip(axes.flat, ns):
        for r in [r for r in rows if r['N'] == n]:
            times = [groups[r['id']][i]['summary']['loop_seconds']/r['median_seconds'] for i in range(1, 11)]
            ax.plot(range(1, 11), times, marker='.', linewidth=.8, label=f'{r["kind"]}{r["actual"]}')
        ax.set(title=f'N={n}', xlabel='Shuffled round', ylabel='Time / configuration median', xticks=range(1, 11))
        ax.grid(alpha=.2)
        ax.legend(ncol=3, fontsize=7)
    fig.suptitle('All measured rounds retained; 16 includes sibling threads')
    save(fig, prefix, '-rounds', plt)


def save(fig, prefix, suffix, plt):
    fig.savefig(str(prefix)+suffix+'.svg')
    fig.savefig(str(prefix)+suffix+'.png', dpi=150)
    plt.close(fig)


def analyze(prefix, output=None, make_plots=True):
    manifest = json.loads(Path(str(prefix)+'.json').read_text())
    records = [json.loads(line) for line in Path(str(prefix)+'.jsonl').read_text().splitlines()]
    rows, groups = summarize(manifest, records)
    output = output or prefix
    with Path(str(output)+'.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with Path(str(output)+'-rounds.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['config_id', 'kind', 'N', 'M', 'actual', 'round', 'seconds', 'over_median'])
        writer.writeheader()
        for r in rows:
            for rep in range(1, 11):
                value = groups[r['id']][rep]['summary']['loop_seconds']
                writer.writerow(dict(config_id=r['id'], kind=r['kind'], N=r['N'], M=r['M'], actual=r['actual'],
                                     round=rep, seconds=value, over_median=value/r['median_seconds']))
    if make_plots:
        plots(rows, groups, output)
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prefix', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--no-plots', action='store_true')
    args = parser.parse_args()
    result = analyze(args.prefix, args.output, not args.no_plots)
    print(f'Validated {len(result)} configurations, 44 warmups, 440 measured samples')
