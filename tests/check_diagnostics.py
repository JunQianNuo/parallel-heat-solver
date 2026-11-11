"""Real-field checks for isolated diagnostic variants; no performance thresholds."""
import argparse
import csv
import io
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from analyze_diagnostics import paired, require, summarize


def run(command, env, timeout=15):
    p=subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                       text=True,start_new_session=True)
    try: out,err=p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid,signal.SIGKILL);p.communicate();raise
    return subprocess.CompletedProcess(command,p.returncode,out,err)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--max-procs',type=int,default=4)
    parser.add_argument('--max-threads',type=int,default=4)
    parser.add_argument('--mpiexec',default='mpiexec')
    a=parser.parse_args();build=a.build.resolve()
    env={k:v for k,v in os.environ.items() if not k.startswith(('OMP_','GOMP_'))}
    env.update(OMP_PROC_BIND='FALSE',OMP_THREAD_LIMIT=str(a.max_threads))
    variants={'serial':['baseline','replica','common'],
              'mpi':['baseline','replica','no-null','common'],
              'openmp':['baseline','replica','block','private','block-private','padded','block-padded']}
    for kind in variants:
        ps=range(1,(a.max_procs if kind=='mpi' else a.max_threads if kind=='openmp' else 1)+1)
        for p in ps:
            command=([a.mpiexec,'-n',str(p)] if kind=='mpi' else [])+[str(build/f'heat_{kind}_diag')]
            if kind=='openmp':command+=['--threads',str(p)]
            for variant in variants[kind]:
                if variant=='no-null' and p>1:continue
                for prof in ([False] if variant=='baseline' else [False,True]):
                    # N=7 covers uneven rows; N=P+1 covers one row/rank;
                    # N=2 with Q>1 covers idle threads and odd/even final roles.
                    for n,m,t in [(7,7,.001),(7,8,.001),
                                  (p+1 if kind=='mpi' else 2,3,.001)]:
                        args=['--N',str(n),'--M',str(m),'--T',str(t),'--alpha','1']
                        ref=run([str(build/'heat_serial'),*args],env)
                        extra=['--variant',variant]+(['--profile'] if prof else [])
                        r=run(command+args+extra,env)
                        require(r.returncode==ref.returncode==0,(kind,p,variant,r.stderr))
                        field=list(csv.DictReader(io.StringIO(r.stdout)))
                        original=list(csv.DictReader(io.StringIO(ref.stdout)))
                        require(len(field)==(n+1)**2,'field size')
                        gain=1-8*(t*n*n/m)*math.sin(math.pi/(2*n))**2
                        for k,(x,y) in enumerate(zip(field,original)):
                            i,j=divmod(k,n+1);v=float(x['u_numeric'])
                            require(int(x['i'])==i and int(x['j'])==j,'ordering')
                            require(math.isfinite(v) and abs(v-float(y['u_numeric']))<=1e-12,'serial difference')
                            initial=0 if i in (0,n) or j in (0,n) else math.sin(math.pi*i/n)*math.sin(math.pi*j/n)
                            require(abs(v-initial*gain**m)<2e-11,'discrete mode')
                            exact=initial*math.exp(-2*math.pi**2*t)
                            require(abs(float(x['u_exact'])-exact)<1e-14,'continuous analytic')
                            if initial==0:require(v==0,'nonzero physical boundary')
                        data={}
                        for line in r.stderr.splitlines():
                            if line.startswith(('N=','loop_seconds=','P_actual=','Q_requested=','variant=')):
                                data.update(item.split('=',1) for item in line.split())
                        require(float(data['loop_seconds'])>0,'invalid loop timer')
                        if kind=='mpi':require(int(data['P_actual'])==p,'P actual')
                        if kind=='openmp':require(int(data['Q_actual'])==p,'Q actual')
                        workers=[json.loads(line[7:]) for line in r.stderr.splitlines() if line.startswith('WORKER ')]
                        require(len(workers)==(0 if variant=='baseline' else p),'worker count')
                        if workers:
                            require(sum(w['rows'] for w in workers)==n-1,'row ownership')
                            require(all(w['total']>0 for w in workers),'worker timer')
                            for w in workers:
                                require(all(math.isfinite(w[k]) and w[k]>=0 for k in ('boundary','communication','update','sync','exchange')),'stage values')
                                if prof:require(sum(w[k] for k in ('boundary','communication','update','sync','exchange'))<=w['total']+1e-8,'stage sum')
                r=run(command+['--variant',variant,'--summary-only'],env)
                require(r.returncode==0 and not r.stdout,'summary-only')
                print(f'DIAG kind={kind} requested={p} actual={p} variant={variant} full fields/profile/odd/even/ownership checked',flush=True)
            bad=[['--variant','unknown'],['--variant'],['--variant','baseline','--profile'],
                 ['--profile','--profile'],['--variant','replica','--variant','replica'],
                 ['--N','1'],['--N','4','--M','1','--T','1']]
            if kind=='mpi' and p>1:bad+=[['--variant','no-null']]
            for args in bad:
                r=run(command+args,env)
                require(r.returncode==2 and not r.stdout,('illegal combination',args,r.returncode,r.stderr))
    # Explicit limited team: requested 4 / actual 2; raw ownership must use actual.
    if a.max_threads>=2:
        env['OMP_THREAD_LIMIT']='2'
        for v in variants['openmp']:
            r=run([str(build/'heat_openmp_diag'),'--threads','4','--variant',v,'--summary-only'],env)
            require(r.returncode==0 and 'Q_requested=4 Q_actual=2' in r.stderr,'limited team')
    # Synthetic values below test method only, never used as performance evidence.
    require(paired([2.0]*10,[1.0]*10)['repeatable'],'detect effect')
    require(not paired([1.0]*10,[1.0]*10)['repeatable'],'identical times')
    require(paired([1.0]*10,[2.0]*10)['repeatable'],'detect regression')
    for a_times,b_times in [([1.0]*9,[1.0]*9),([float('nan')]*10,[1.0]*10),([0.0]*10,[1.0]*10)]:
        try:paired(a_times,b_times)
        except RuntimeError:pass
        else:raise RuntimeError('invalid synthetic input accepted')
    try:summarize([dict(type='sample',returncode=0,mono_start_ns=0,mono_end_ns=1,warmup=False,
                        summary={'loop_seconds':1},config={},stage='synthetic',repetition=1)])
    except RuntimeError:pass
    else:raise RuntimeError('missing samples accepted')
    synthetic=[]
    for pair_name in ('left','right'):
        for rep in range(1,11):
            for side,value in [('A',2.0),('B',1.0)]:
                synthetic.append(dict(type='sample',id=len(synthetic),returncode=0,mono_start_ns=0,
                    mono_end_ns=1,warmup=False,summary={'loop_seconds':value},config={'side':side},
                    stage='synthetic',pair=pair_name,side=side,repetition=rep))
    groups,effects=summarize(synthetic)
    require(len(groups)==4 and len(effects)==2 and all(e['ratio']==2 for e in effects),'independent pair groups')
    for broken in (synthetic[:-1],synthetic+[synthetic[-1]], [dict(synthetic[0],returncode=1)]+synthetic[1:]):
        try:summarize(broken)
        except RuntimeError:pass
        else:raise RuntimeError('damaged paired records accepted')
    print('DIAG statistics synthetic effect/no-effect/regression/invalid/missing-sample checks passed')


if __name__=='__main__':main()
