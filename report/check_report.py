#!/usr/bin/env python3
"""Check the written report against archived evidence without opening a PPTX."""
import argparse, csv, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent

def require(ok,message):
    if not ok:raise ValueError(message)

def table_rows(source,headers):
    lines=source.splitlines()
    normalized_headers=[re.sub(r'\s+','',v) for v in headers]
    for i,line in enumerate(lines):
        if line.startswith('|') and [re.sub(r'\s+','',v) for v in line.strip().strip('|').split('|')]==normalized_headers:
            rows=[]
            for line in lines[i+1:]:
                if not line.startswith('|'):break
                cells=[v.strip() for v in line.strip().strip('|').split('|')]
                if all(re.fullmatch(r':?-+:?',v) for v in cells):continue
                require(len(cells)==len(headers),'inconsistent table columns')
                rows.append(cells)
            return rows
    raise ValueError(f'missing table: {headers}')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--course-baseline',type=Path)
    ap.add_argument('--output',type=Path,default=ROOT/'records/report_checks.json')
    args=ap.parse_args()
    report=ROOT/'FINAL_REPORT.md';source=report.read_text()
    require(source.count('```')%2==0,'unclosed code fence')
    require(source.count('$$')%2==0,'unclosed display formula')
    require(all(re.search(rf'^## {i}\. ',source,re.M) for i in range(1,9)),'missing numbered report section')
    links=0
    for target in re.findall(r'\]\(([^)]+)\)',source):
        if re.match(r'https?://|#',target):continue
        require((ROOT/target.split('#')[0]).exists(),f'missing report link: {target}');links+=1
    rows=list(csv.DictReader((REPO/'results/performance/large-02-r1/m4-diagnostic-02-r1.csv').open(newline='')))
    selected={(int(r['N']),r['kind'],int(r['actual'])):r for r in rows}
    fixed=table_rows(source,['并行度 $p$','MPI 耗时 (s)','MPI 加速比','OpenMP 耗时 (s)','OpenMP 加速比'])
    expected=[]
    for k in [1,2,4,8,16]:
        cells=[str(k)]
        for kind in ['mpi','openmp']:
            r=selected[1024,kind,k]
            cells.extend([f"{float(r['median_seconds']):.4f}",f"{float(r['speedup_serial']):.4f}"])
        expected.append(cells)
    require(fixed==expected,'fixed-size table differs from archived statistics')
    require(f"{float(selected[1024,'serial',1]['median_seconds']):.4f}" in source,'missing independent serial baseline')
    grid=table_rows(source,['网格 $N$','MPI 4','MPI 8','MPI 16','OpenMP 4','OpenMP 8','OpenMP 16'])
    checked=[384,512,768,1024]
    expected=[[str(N)]+[f"{float(selected[N,kind,k]['speedup_serial']):.4f}" for kind in ['mpi','openmp'] for k in [4,8,16]] for N in checked]
    require(grid==expected,'grid table differs from archived statistics')
    baseline=list(csv.DictReader((REPO/'results/performance/baseline/derived/summary.csv').open(newline='')))
    scaled={(r['kind'],int(r['p'])):r for r in baseline if r['suite']=='scaled'}
    configs=table_rows(source,['目标并行度 $p$','网格 $N$','时间步数 $M$','相对工作量 $W/W_1$'])
    expected=[]
    for k in [1,2,4]:
        r=scaled['mpi',k];expected.append([str(k),r['N'],r['M'],f"{float(r['work_ratio']):.4f}"])
    require(configs==expected,'scaled configuration table differs from archived statistics')
    throughput=table_rows(source,['实现','并行度 $p$','耗时 (s)','吞吐增长 $R_p$','$R_p/p$'])
    expected=[]
    for kind,label in [('mpi','MPI'),('openmp','OpenMP')]:
        for k in [1,2,4]:
            r=scaled[kind,k];expected.append([label,str(k),f"{float(r['median_seconds']):.4f}",f"{float(r['throughput_ratio_own_p1']):.4f}",f"{float(r['normalized_scaled_efficiency'])*100:.2f}%"])
    require(throughput==expected,'scaled throughput table differs from archived statistics')
    diagnostic=table_rows(source,['诊断对象','修改内容','耗时比 $K$','实验发现'])
    pairs=list(csv.DictReader((REPO/'results/performance/diagnostic-01/m4-diagnostic-01.csv').open(newline='')))
    ratios=[]
    for stage,name in [('common','mpi1'),('factor','384-q4-replica/block')]:
        r=next(r for r in pairs if r['type']=='pair' and r['stage']==stage and r['name']==name)
        ratios.append(f"{float(r['ratio']):.4f}")
    require([r[2] for r in diagnostic]==ratios,'diagnostic paired ratios differ from archived statistics')
    m3=list(csv.DictReader((REPO/'results/validation/m3-errors.csv').open()))
    for r in m3:
        if r['build']=='debug' and r['suite']=='default' and r['solver']=='serial' and r['ratio']:
            require(f"{float(r['ratio']):.6f}" in source,'M3 error ratio mismatch')
            require(f"{float(r['order']):.6f}" in source,'M3 observed order mismatch')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    pdf=ROOT/'FINAL_REPORT.pdf';require(pdf.read_bytes().startswith(b'%PDF'),'invalid PDF header')
    pdf_check={'page_analysis':'未运行：缺少PyMuPDF'}
    try:import pymupdf
    except ImportError:pass
    else:
        doc=pymupdf.open(pdf);outside=[]
        for i,page in enumerate(doc,1):
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line['spans']:
                        x0,y0,x1,y1=span['bbox']
                        if x0<-.5 or y0<-.5 or x1>page.rect.width+.5 or y1>page.rect.height+.5:outside.append({'page':i,'text':span['text']})
        require(not outside,'PDF text crosses page boundary')
        pdf_check={'pages':len(doc),'text_outside_page':outside,'page_analysis':'读取现有PDF；未重新生成或渲染'}
    course='未运行：未提供本轮前置快照'
    if args.course_baseline:
        before=json.loads(args.course_baseline.read_text());base=REPO/'docs/sources'
        after={str(p.relative_to(base)):sha(p) for p in sorted(base.rglob('*')) if p.is_file()}
        require(before==after,'read-only course material changed');course=f'{len(after)} files: paths/content unchanged'
    result={'scope':'书面报告；未调用PPT工具、求解器、构建、数值回归或性能采样','report_links_checked':links,'numbered_sections':8,'performance_table_N':checked,'M3_error_ratios_orders':'对照归档CSV通过','report_markdown_sha256':sha(report),'report_pdf_sha256':sha(pdf),'pdf':pdf_check,'course_protection':course,'human_review':'未验收；姓名学号待填写，内容/排版待用户审阅'}
    result['performance_tables']={'fixed_size_N':1024,'MPI_actual_P':[1,2,4,8,16],'OpenMP_actual_Q':[1,2,4,8,16],'fixed_size_rows_checked':len(fixed),'grid_rows_checked':len(grid),'scaled_configuration_rows_checked':len(configs),'scaled_throughput_rows_checked':len(throughput),'diagnostic_rows_checked':len(diagnostic),'numeric_cells_checked':73,'method':'五表逐行逐格对照归档CSV；耗时/S/工作量比四位、效率百分数两位；诊断仅使用原配对比率中位数'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
