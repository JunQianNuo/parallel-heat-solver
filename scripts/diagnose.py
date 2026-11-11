"""Sequential adaptive M4 diagnostics. Frozen choices are embedded in the manifest.

New run IDs only. All raw invocations, validation and decisions are retained.
"""
import argparse
import copy
from datetime import datetime,timezone
import hashlib
import io
import csv
import json
import math
import os
from pathlib import Path
import random
import signal
import statistics
import subprocess
import time

from benchmark import configurations,parse_summary
from analyze_diagnostics import paired,require

SEED=20261110
REPEATS=10


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def utc():return datetime.now(timezone.utc).isoformat()


def execute(command,env,timeout=120):
    start=time.monotonic_ns();stamp=utc()
    p=subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
    try:out,err=p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid,signal.SIGKILL);out,err=p.communicate();err+='\nTIMEOUT'
        return -1,out,err,start,time.monotonic_ns(),stamp,utc()
    return p.returncode,out,err,start,time.monotonic_ns(),stamp,utc()


def config(kind,p=1,N=384,M=9216,T=.01,variant='baseline',profile=False,cpus=None,wait='ACTIVE',wrapper=False):
    return dict(kind=kind,p=p,N=N,M=M,T=T,alpha=1.0,variant=variant,profile=profile,
                cpus=cpus or [0,2,4,6],wait=wait,wrapper=wrapper)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--run-id',required=True)
    a=parser.parse_args()
    require(a.run_id.replace('-','').isalnum(),'run id must be alphanumeric/hyphens')
    directory=Path('results/performance')/('diagnostic-'+a.run_id)
    require(not directory.exists(),'run directory already exists; do not overwrite evidence')
    prefix=directory/('m4-diagnostic-'+a.run_id)
    source_paths=[Path('CMakeLists.txt')]+[p for d in ('src','tests','scripts') for p in sorted(Path(d).glob('*')) if p.is_file()]
    require(not subprocess.check_output(['git','status','--porcelain','--','CMakeLists.txt','src','tests','scripts'],text=True),'commit diagnostic source before sampling')
    cache=(a.build/'CMakeCache.txt').read_text()
    require('CMAKE_BUILD_TYPE:STRING=Release\n' in cache and 'HEAT_BUILD_DIAGNOSTICS:BOOL=ON\n' in cache,'Release diagnostics required')
    require({0,2,4,6}<=os.sched_getaffinity(0),'baseline CPUs unavailable')
    compile_commands=json.loads((a.build/'compile_commands.json').read_text())
    require(all('-O3' in x['command'] and '-DNDEBUG' in x['command'] and not any(f in x['command'] for f in ['-ffast-math','-march=','-flto']) for x in compile_commands),'non-frozen compiler options')
    binaries={k:str((a.build/f'heat_{k}_diag').resolve()) for k in ('serial','mpi','openmp')}
    original=json.loads(Path('results/performance/baseline/protocol.json').read_text())
    manifest=dict(schema=1,revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  started_utc=utc(),complete=False,seed=SEED,repeats=REPEATS,warmups=1,
                  environment_defaults=dict(OMP_DYNAMIC='FALSE',OMP_THREAD_LIMIT='4',OMP_PROC_BIND='close',OMP_WAIT_POLICY='ACTIVE',OMP_PLACES='{0},{2},{4},{6}',LC_ALL='C'),
                  source_sha256={str(p):digest(p) for p in source_paths},
                  binary_sha256={k:digest(v) for k,v in binaries.items()},compile_commands=compile_commands,
                  original_protocol=original,protocol=dict(profile_overhead=.05,repeatability_ratio=1.05,
                  directional_pairs=8,bootstrap_draws=10000,early_slow_ratio=1.1,sync_fraction=.2,
                  fixed_steps=dict(N=[128,256,384,512],M=9216,T=.005),fixed_grid=dict(N=384,M=[1024,4096,16384],T=.001),
                  granularity_variants='baseline and at most one largest repeatable direct replica contrast per solver'))
    directory.mkdir(parents=True,exist_ok=False)
    Path(str(prefix)+'.json').write_text(json.dumps(manifest,indent=2)+'\n')
    base_env={k:v for k,v in os.environ.items() if not k.startswith(('OMP_','GOMP_','KMP_','OMPI_','PMI_','PMIX_'))}
    base_env['LC_ALL']='C'
    envlog=Path(str(prefix)+'.log').open('w',buffering=1)
    envlog.write('M4 diagnostic run; raw samples stored separately; no original M4 artifacts overwritten.\n')
    commands=[['uname','-a'],['lscpu'],['lscpu','-e=CPU,CORE,SOCKET,NODE'],['free','-h'],['c++','--version'],
              ['cmake','--version'],['mpiexec','--version'],['dpkg-query','-W','libgomp1'],['ompi_info','--parsable']]
    for name in binaries:commands.append(['ldd',binaries[name]])
    # Compiler evidence: exact source/context, including both original and diagnostic kernels.
    for file,compiler,extra in [('heat.cpp','c++',[]),('heat_mpi.cpp','mpicxx',[]),('heat_openmp.cpp','c++',['-fopenmp']),
                               ('diagnostic_kernel.cpp','c++',[]),('diagnostic_serial.cpp','c++',[]),('diagnostic_mpi.cpp','mpicxx',[]),('diagnostic_openmp.cpp','c++',['-fopenmp'])]:
        commands.append([compiler,'-O3','-DNDEBUG','-std=c++17','-I','src',*extra,'-fopt-info-vec-optimized','-fopt-info-vec-missed','-S','src/'+file,'-o','/dev/null'])
    for cmd in commands:
        code,out,err,*_=execute(cmd,base_env,30)
        envlog.write('$ '+' '.join(cmd)+'\n'+out+err+f'\nexit={code}\n')
        require(code==0,'environment/compiler probe failed; preserved in log')
    for binary, needle in [('heat_serial','4step'),('heat_mpi','9solve_mpi'),
                            ('heat_openmp','_omp_fn.0'),('heat_serial_diag','4diag4rows'),
                            ('heat_mpi_diag','4diag4rows')]:
        binary_path=str((a.build/binary).resolve())
        symbols=subprocess.check_output(['nm','-S','--defined-only',binary_path],text=True)
        matches=[line.split()[-1] for line in symbols.splitlines() if needle in line and '.cold' not in line]
        require(matches, 'expected compiled function symbol missing: '+binary)
        for symbol in matches:
            cmd=['objdump','-d','--disassemble='+symbol,binary_path]
            code,out,err,*_=execute(cmd,base_env,30)
            envlog.write('$ '+' '.join(cmd)+'\n'+out+err+f'\nexit={code}\n')
            require(code==0 and '>:' in out,'assembly probe missing function body')
    for path in ('/proc/self/cgroup','/proc/self/limits','/proc/meminfo','/proc/loadavg','/sys/fs/cgroup/init.scope/cpu.max','/sys/fs/cgroup/init.scope/memory.max'):
        envlog.write('\n'+path+'\n'+(Path(path).read_text() if Path(path).exists() else 'absent\n'))
    samples=[];decisions=[];warm_cache={};references={};counter=0
    log=Path(str(prefix)+'.jsonl').open('w',buffering=1)
    rng=random.Random(SEED)

    def invoke(c,stage,rep,warm=False,pair_name='',side=''):
        nonlocal counter
        kind=c['kind'];p=c['p'];command=[binaries[kind]]
        if kind=='mpi':
            if c['wrapper']:
                code='import os,sys; cpus='+repr(c['cpus'])+'; os.sched_setaffinity(0,{cpus[int(os.environ["OMPI_COMM_WORLD_RANK"])]}); os.execv(sys.argv[1],sys.argv[1:])'
                command=['mpiexec','--map-by','core','--bind-to','none','-n',str(p),'python3','-c',code,*command]
            else:command=['mpiexec','-n',str(p),'--map-by','core','--bind-to','hwthread','--report-bindings',*command]
        elif kind=='openmp':command+=['--threads',str(p)]
        else:command=['taskset','-c',str(c['cpus'][0]),*command]
        command+=['--N',str(c['N']),'--M',str(c['M']),'--T',str(c['T']),'--alpha',str(c['alpha']),'--variant',c['variant']]
        if c['profile']:command+=['--profile']
        if not warm:command+=['--summary-only']
        env=dict(base_env,OMP_DYNAMIC='FALSE',OMP_THREAD_LIMIT='4',OMP_PROC_BIND='close',OMP_WAIT_POLICY=c['wait'],
                 OMP_PLACES=','.join('{%d}'%x for x in c['cpus']),OMP_DISPLAY_AFFINITY='TRUE' if warm and kind=='openmp' else 'FALSE')
        code,out,err,start,end,stamp,finish=execute(command,env)
        row=dict(type='sample',id=counter,stage=stage,config=c,repetition=rep,warmup=warm,pair=pair_name,side=side,
                 revision=manifest['revision'],command=command,returncode=code,utc_start=stamp,utc_end=finish,
                 mono_start_ns=start,mono_end_ns=end,stderr=err,stdout_sha256=hashlib.sha256(out.encode()).hexdigest())
        counter+=1
        log.write(json.dumps(dict(row,type='attempt'))+'\n')
        if code:
            log.write(json.dumps(row)+'\n');raise RuntimeError('diagnostic invocation failed; raw result preserved')
        require('variant='+c['variant']+' profile='+str(int(c['profile'])) in err,'variant/profile summary mismatch')
        d=parse_summary(err)
        require(all(d[k]==c[k] for k in ('N','M','T','alpha')),'parameter mismatch')
        require(int(d.get('P_actual',d.get('Q_actual',1)))==p and int(d.get('Q_requested',p))==p,'actual team mismatch')
        require(math.isfinite(d['loop_seconds']) and d['loop_seconds']>0 and 0<d['r']<=.25,'invalid time/r')
        workers=[json.loads(x[7:]) for x in err.splitlines() if x.startswith('WORKER ')]
        row.update(summary=d,workers=workers)
        if c['variant']!='baseline':
            require(len(workers)==p and sum(w['rows'] for w in workers)==c['N']-1,'worker ownership')
            require(all(w['cpu']==c['cpus'][w['id']] for w in workers),'unexpected worker affinity')
        if warm:
            n,m=c['N'],c['M'];values=list(csv.DictReader(io.StringIO(out)));field=[]
            require(len(values)==(n+1)**2,'wrong field size')
            gain=1-8*d['r']*math.sin(math.pi/(2*n))**2;mode=0.0;error=0.0
            for k,x in enumerate(values):
                i,j=divmod(k,n+1);v=float(x['u_numeric'])
                require(int(x['i'])==i and int(x['j'])==j and math.isfinite(v),'field ordering/value')
                boundary=i in (0,n) or j in (0,n)
                initial=0 if boundary else math.sin(math.pi*i/n)*math.sin(math.pi*j/n)
                require(not boundary or v==0,'nonzero boundary')
                mode=max(mode,abs(v-initial*gain**m));error=max(error,abs(v-initial*math.exp(-2*c['alpha']*math.pi**2*c['T'])))
                field.append(v)
            key=(n,m,c['T'],c['alpha'])
            if kind=='serial' and c['variant']=='baseline':references[key]=field
            require(key in references,'serial reference missing')
            difference=max(abs(x-y) for x,y in zip(field,references[key]))
            # Bound discrete-continuous mode difference independently for new matrices.
            truncation=abs(gain**m-math.exp(-2*c['alpha']*math.pi**2*c['T']))
            require(mode<2e-11 and difference<=1e-12 and abs(error-d['E_inf'])<1e-14 and error<=truncation+2e-11,'numerical validation failed')
            row['validation']=dict(D_inf=difference,E_inf=error,mode_diff=mode,truncation_bound=truncation+2e-11)
        else:
            require(not out,'unexpected summary stdout')
            reference=warm_cache[json.dumps(c,sort_keys=True)]
            require(abs(d['E_inf']-reference['summary']['E_inf'])<1e-14,'sample/warmup error differs')
        log.write(json.dumps(row)+'\n');samples.append(row)
        print(f"{stage} {pair_name} {side} rep={rep} {kind} p={p} N={c['N']} v={c['variant']} profile={c['profile']} t={d['loop_seconds']:.7g}",flush=True)
        return row

    def warmup(c):
        key=json.dumps(c,sort_keys=True)
        if key in warm_cache:return
        ref=config('serial',N=c['N'],M=c['M'],T=c['T'],cpus=c['cpus'])
        rk=json.dumps(ref,sort_keys=True)
        if rk!=key and rk not in warm_cache:warmup(ref)
        warm_cache[key]=invoke(c,'validation',0,True)

    def compare(stage,label,A,B):
        warmup(A);warmup(B);ar=[];br=[];ids_a=[];ids_b=[]
        order=[False]*5+[True]*5;rng.shuffle(order)
        for rep,reverse in enumerate(order,1):
            observations={}
            for side,c in ([('B',B),('A',A)] if reverse else [('A',A),('B',B)]):
                observations[side]=invoke(c,stage,rep,False,label,side)
            ar.append(observations['A']['summary']['loop_seconds']);br.append(observations['B']['summary']['loop_seconds'])
            ids_a.append(observations['A']['id']);ids_b.append(observations['B']['id'])
        result=dict(stage=stage,pair=label,**paired(ar,br));decisions.append(result)
        log.write(json.dumps(dict(type='comparison',**result,a=ids_a,b=ids_b))+'\n')
        return result

    def skip(stage,reason):
        entry=dict(type='decision',stage=stage,action='not-run',reason=reason);log.write(json.dumps(entry)+'\n');decisions.append(entry)

    original_configs=[config(c['kind'],c['p'],c['N'],c['M'],c['T']) for c in configurations(original)]
    for c in original_configs:warmup(c)
    reproduction=[]
    for rep in range(1,11):
        order=original_configs.copy();rng.shuffle(order)
        reproduction.extend(invoke(c,'reproduce',rep) for c in order)
    med=lambda kind,p,n=384:statistics.median(r['summary']['loop_seconds'] for r in reproduction if r['config']['kind']==kind and r['config']['p']==p and r['config']['N']==n)
    core=[config(k,p) for k in ('serial','mpi','openmp') for p in ([1] if k=='serial' else [1,2,4])]
    profiles={};copy_calibration={}
    for c in core:
        label=c['kind']+str(c['p']);rep=dict(c,variant='replica')
        copy_calibration[label]=compare('copy',label,c,rep)
        profiles[label]=compare('profile',label,rep,dict(rep,profile=True))
    candidates={'serial':[],'mpi':[],'openmp':[]}
    if med('mpi',1)>1.05*med('serial',1):
        e=compare('null','mpi1',config('mpi',variant='replica'),config('mpi',variant='no-null'))
        if e['repeatable']:candidates['mpi'].append(('no-null',abs(math.log(e['ratio']))))
        mpi_update=statistics.median(sum(w['update'] for w in r['workers']) for r in samples if r['stage']=='profile' and r['pair']=='mpi1' and r['side']=='B')
        serial_update=statistics.median(sum(w['update'] for w in r['workers']) for r in samples if r['stage']=='profile' and r['pair']=='serial1' and r['side']=='B')
        if mpi_update>1.05*serial_update:
            for k in ('serial','mpi'):
                e=compare('common',k+'1',config(k,variant='replica'),config(k,variant='common'))
                if e['repeatable']:candidates[k].append(('common',abs(math.log(e['ratio']))))
        else:skip('common','MPI update profile is not over 5% slower; profiling remains only a clue if calibration fails')
    else:skip('null/common','MPI single-process slowdown did not reproduce')
    sync_fraction=0.0
    for r in samples:
        if r['stage']=='profile' and r['side']=='B' and r['config']['kind']=='openmp' and r['config']['p']>1:
            slow=max(r['workers'],key=lambda w:w['total'])
            sync_fraction=max(sync_fraction,(slow['sync']+slow['exchange'])/slow['total'])
    factor=[]
    if any(med('openmp',p)>med('serial',1) for p in (2,4)) or sync_fraction>=.2:
        for n,m in ((128,1024),(384,9216)):
            for p in (2,4):
                for av,bv in [('replica','block'),('replica','private'),('block','block-private'),('private','block-private')]:
                    e=compare('factor',f'{n}-q{p}-{av}/{bv}',config('openmp',p,n,m,variant=av),config('openmp',p,n,m,variant=bv));factor.append((av,bv,e))
                    if av=='replica' and e['repeatable']:candidates['openmp'].append((bv,abs(math.log(e['ratio']))))
    else:skip('factor','no OpenMP multithread slowdown or prominent synchronization observed')
    if any(e['repeatable'] for av,bv,e in factor if (av,bv) in [('replica','block'),('private','block-private')]):
        for p in (2,4):
            for av,bv in [('replica','padded'),('block','block-padded')]:
                e=compare('layout',f'q{p}-{av}/{bv}',config('openmp',p,variant=av),config('openmp',p,variant=bv))
                if av=='replica' and e['repeatable']:candidates['openmp'].append((bv,abs(math.log(e['ratio']))))
    else:skip('layout','row scheduling did not meet repeatability rule')
    if sync_fraction>=.2 or any(e['repeatable'] for av,bv,e in factor if bv in ('private','block-private')):
        for p in (2,4):compare('wait','q'+str(p),config('openmp',p,variant='replica'),config('openmp',p,variant='replica',wait='PASSIVE'))
    else:skip('wait','sync share below 20% and no repeatable synchronization contrast')
    # CPU selection is triggered only by a reproduced early/late trend.
    early_slow=False
    for c in original_configs:
        group=sorted((r for r in reproduction if r['config']==c),key=lambda r:r['repetition'])
        if statistics.median(r['summary']['loop_seconds'] for r in group[:3])>1.1*statistics.median(r['summary']['loop_seconds'] for r in group[-3:]):early_slow=True
    if early_slow and set(range(0,15,2))<=os.sched_getaffinity(0):
        cpu_rows={cpu:[] for cpu in range(0,15,2)}
        for cpu in cpu_rows:warmup(config('serial',cpus=[cpu]))
        for rep in range(1,11):
            cpus=list(cpu_rows);rng.shuffle(cpus)
            for cpu in cpus:cpu_rows[cpu].append(invoke(config('serial',cpus=[cpu]),'cpu',rep))
        cpu_effect=False
        for cpu in range(2,15,2):
            A=cpu_rows[0];B=cpu_rows[cpu];e=paired([r['summary']['loop_seconds'] for r in A],[r['summary']['loop_seconds'] for r in B])
            entry=dict(type='comparison',stage='cpu',pair=f'0/{cpu}',a=[r['id'] for r in A],b=[r['id'] for r in B],**e)
            log.write(json.dumps(entry)+'\n');decisions.append(entry);cpu_effect|=e['repeatable']
        if cpu_effect:
            for c in core:
                compare('cpu-group',c['kind']+str(c['p']),dict(c,wrapper=c['kind']=='mpi'),dict(c,cpus=[8,10,12,14],wrapper=c['kind']=='mpi'))
        else:skip('cpu-group','CPU contrasts did not meet repeatability rule')
    else:skip('cpu/cpu-group','no first-three/last-three median slowdown over 10%, or required CPU set unavailable')
    selected={k:max(v,key=lambda x:x[1])[0] if v else None for k,v in candidates.items()}
    log.write(json.dumps(dict(type='decision',stage='granularity',selected=selected,reason='largest absolute repeatable direct replica contrast per solver; resource legality still applies'))+'\n')
    grids=[('fixed-M',n,9216,.005) for n in (128,256,384,512)]+[('fixed-N',384,m,.001) for m in (1024,4096,16384)]
    for suite,n,m,t in grids:
        for kind in ('serial','mpi','openmp'):
            for p in ([1] if kind=='serial' else [1,2,4]):
                c=config(kind,p,n,m,t,variant='replica')
                v=selected[kind]
                if v=='no-null' and p!=1:v=None
                baseline=dict(c,variant='baseline')
                warmup(baseline)
                for rep in range(1,11):invoke(baseline,'granularity-baseline-'+suite,rep)
                if v:compare('granularity',f'{suite}-{n}-{m}-{kind}{p}',c,dict(c,variant=v))
    require(all(digest(p)==v for p,v in manifest['source_sha256'].items()),'source changed during sampling')
    require(all(digest(binaries[k])==v for k,v in manifest['binary_sha256'].items()),'binary changed during sampling')
    log.close();envlog.close()
    manifest.update(complete=True,finished_utc=utc(),invocations=len(samples),measured=sum(not r['warmup'] for r in samples),
                    warmup_invocations=sum(r['warmup'] for r in samples),decisions=decisions,
                    source_and_binary_unchanged=True,copy_calibration=copy_calibration,profile_calibration=profiles)
    Path(str(prefix)+'.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('COMPLETE',manifest['invocations'],'invocations;',manifest['measured'],'measured',flush=True)


if __name__=='__main__':main()
