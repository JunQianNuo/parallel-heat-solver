"""M4 diagnostic statistics. Paired ratios are baseline/variant; exploratory only."""
import argparse
from collections import defaultdict
import csv
import json
import math
from pathlib import Path
from benchmark import parse_summary
import random
import statistics


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def paired(a, b):
    require(len(a) == len(b) == 10, 'ten complete pairs required')
    require(all(math.isfinite(x) and x > 0 for x in a+b), 'invalid paired time')
    ratios = [x/y for x, y in zip(a, b)]
    rng = random.Random(20261110)
    boot = sorted(statistics.median(rng.choices(ratios, k=10)) for _ in range(10000))
    median = statistics.median(ratios)
    low, high = boot[249], boot[9749]
    direction = max(sum(x > 1 for x in ratios), sum(x < 1 for x in ratios))
    effect = (median >= 1.05 or median <= 1/1.05) and direction >= 8 and (low > 1 or high < 1)
    return dict(ratio=median, low=low, high=high, direction=direction, repeatable=bool(effect),
                median_A=statistics.median(a), median_B=statistics.median(b))


def summarize(records):
    configs, pairs = defaultdict(list), defaultdict(dict)
    for row in records:
        if row.get('type') != 'sample':
            continue
        require(row['returncode'] == 0, 'unsuccessful recorded invocation')
        require(row['mono_end_ns'] >= row['mono_start_ns'], 'monotonic timestamps reversed')
        if row['warmup']:
            require(row['validation']['D_inf'] <= 1e-12, 'invalid full field')
            continue
        t = row['summary']['loop_seconds']
        require(math.isfinite(t) and t > 0, 'invalid time')
        key = json.dumps(row['config'], sort_keys=True)
        configs[(row['stage'], row.get('pair',''), key)].append(row)
        if row.get('pair'):
            pkey = (row['stage'], row['pair'], row['repetition'])
            require(row['side'] not in pairs[pkey], 'duplicate paired side')
            pairs[pkey][row['side']] = row
    results = []
    for (stage, name, key), group in configs.items():
        require(len(group) == 10 and {r['repetition'] for r in group} == set(range(1, 11)), 'incomplete config '+stage)
        times = [r['summary']['loop_seconds'] for r in group]
        results.append(dict(stage=stage, pair=name, config=json.loads(key), median=statistics.median(times),
                            minimum=min(times), maximum=max(times), count=len(times)))
    groups = defaultdict(dict)
    for (stage, name, rep), sides in pairs.items():
        require(set(sides) == {'A', 'B'}, 'incomplete pair')
        groups[stage, name][rep] = sides
    effects = []
    for (stage, name), repetitions in groups.items():
        require(set(repetitions) == set(range(1, 11)), 'missing paired repetition')
        ordered = [repetitions[i] for i in range(1, 11)]
        effects.append(dict(stage=stage, pair=name, **paired(
            [p['A']['summary']['loop_seconds'] for p in ordered],
            [p['B']['summary']['loop_seconds'] for p in ordered])))
    indexed={r['id']:r for r in records if r.get('type')=='sample'}
    for entry in records:
        if entry.get('type')=='comparison' and entry.get('stage')=='cpu':
            require(len(entry['a'])==len(entry['b'])==10, 'incomplete CPU comparison')
            A=[indexed[i] for i in entry['a']];B=[indexed[i] for i in entry['b']]
            require(all(r['stage']=='cpu' for r in A+B), 'wrong CPU comparison source')
            effects.append(dict(stage='cpu',pair=entry['pair'], **paired(
                [r['summary']['loop_seconds'] for r in A],
                [r['summary']['loop_seconds'] for r in B])))
    return results, effects


def analyze(prefix, output=None, plots=True):
    manifest = json.loads(Path(str(prefix)+'.json').read_text())
    require(manifest.get('complete'), 'sampling not complete')
    records = [json.loads(line) for line in Path(str(prefix)+'.jsonl').read_text().splitlines()]
    samples = [r for r in records if r.get('type') == 'sample']
    require(all(r['revision'] == manifest['revision'] for r in samples), 'revision mismatch')
    require(len({r['id'] for r in samples})==len(samples), 'duplicate invocation ID')
    for r in samples:
        c=r['config'];d=r['summary']
        require('variant='+c['variant']+' profile='+str(int(c['profile'])) in r['stderr'], 'variant/profile mismatch')
        require(parse_summary(r['stderr'])==d, 'raw/parsed summary mismatch')
        require(all(c[k]==d[k] for k in ('N','M','T','alpha')), 'parameter mismatch')
        require(int(d.get('P_actual',d.get('Q_actual',1)))==c['p'], 'actual team mismatch')
        require(0<d['r']<=.25 and math.isfinite(d['E_inf']), 'invalid stability/error')
    require(len(samples) == manifest['invocations'], 'invocation count mismatch')
    warmed={}
    for r in samples:
        key=json.dumps(r['config'],sort_keys=True)
        if r['warmup']:
            require(key not in warmed, 'duplicate configuration warmup')
            require(r['validation']['mode_diff']<2e-11 and
                    abs(r['validation']['E_inf']-r['summary']['E_inf'])<1e-14, 'invalid warmup validation')
            warmed[key]=r['summary']['E_inf']
        else:
            require(key in warmed and abs(r['summary']['E_inf']-warmed[key])<1e-14, 'missing/mismatched full-field warmup')
    for previous, following in zip(samples, samples[1:]):
        require(previous['mono_end_ns'] <= following['mono_start_ns'], 'overlapping recorded invocations')
    result, effects = summarize(records)
    out = output or prefix
    rows = []
    for r in result:
        c = r['config']
        rows.append(dict(type='configuration', stage=r['stage'], name=json.dumps(c, sort_keys=True),
                        median_A=r['median'], median_B='', minimum=r['minimum'], maximum=r['maximum'],
                        ratio='', low='', high='', direction='', repeatable=''))
    for e in effects:
        rows.append(dict(type='pair', stage=e['stage'], name=e['pair'], minimum='', maximum='',
                         **{k:e[k] for k in ('median_A','median_B','ratio','low','high','direction','repeatable')}))
    with Path(str(out)+'.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    worker_groups=defaultdict(list)
    for r in samples:
        if r['warmup']:continue
        for worker in r['workers']:
            key=(r['stage'],r.get('pair',''),r.get('side',''),json.dumps(r['config'],sort_keys=True),worker['id'])
            worker_groups[key].append(worker)
    with Path(str(out)+'-workers.csv').open('w',newline='') as f:
        keys=['stage','pair','side','config','worker','rows','cpu','median_total','minimum_total','maximum_total',
              'median_boundary','median_communication','median_update','median_sync','median_exchange']
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
        for (stage,name,side,c,worker),group in worker_groups.items():
            require(len(group)==10, 'missing worker samples')
            writer.writerow(dict(stage=stage,pair=name,side=side,config=c,worker=worker,
                rows=group[0]['rows'],cpu=group[0]['cpu'],
                minimum_total=min(w['total'] for w in group),maximum_total=max(w['total'] for w in group),
                **{'median_'+key:statistics.median(w[key] for w in group)
                   for key in ('total','boundary','communication','update','sync','exchange')}))
    if plots:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.rcParams['svg.fonttype'] = 'none'
        fig, ax = plt.subplots(figsize=(12, max(5, len(effects)*.24)), constrained_layout=True)
        for i, e in enumerate(effects):
            ax.errorbar(e['ratio'], i, xerr=[[e['ratio']-e['low']], [e['high']-e['ratio']]],
                        fmt='o', color='tab:blue' if e['repeatable'] else 'grey', capsize=2)
        ax.axvline(1, color='black', linestyle='--')
        ax.set(yticks=list(range(len(effects))), yticklabels=[e['stage']+': '+e['pair'] for e in effects],
               xlabel='Paired baseline/variant median, bootstrap 95% interval (exploratory)',
               title='Isolated diagnostic effects; blue meets predefined repeatability rule')
        ax.grid(axis='x', alpha=.2)
        fig.savefig(str(out)+'.svg');fig.savefig(str(out)+'.png', dpi=140);plt.close(fig)
    return result, effects


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prefix',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--no-plots',action='store_true')
    args=parser.parse_args()
    result,effects=analyze(args.prefix,args.output,not args.no_plots)
    print(f'Validated {len(result)} measured configurations and {len(effects)} complete paired comparisons')
