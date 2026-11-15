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
    for i,line in enumerate(lines):
        if line.startswith('|') and [v.strip() for v in line.strip().strip('|').split('|')]==headers:
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
    fixed=table_rows(source,['执行方式','实际执行单元数','推进耗时中位数（秒）','相对独立串行的加速比'])
    expected=[]
    configurations=[('serial',1)]+[(kind,k) for kind in ['mpi','openmp'] for k in [1,2,4,8,16]]
    for kind,k in configurations:
        r=selected[1024,kind,k]
        label={'serial':'独立串行','mpi':'MPI','openmp':'OpenMP'}[kind]
        unit=str(k)+{'serial':'','mpi':'进程','openmp':'线程'}[kind]
        expected.append([label,unit,f"{float(r['median_seconds']):.9f}",f"{float(r['speedup_serial']):.4f}"])
    require(fixed==expected,'fixed-size table differs from archived statistics')
    grid_header='串行耗时Ts（秒）' if '串行耗时Ts（秒）' in source else '串行耗时Ts'
    grid=table_rows(source,['N',grid_header,'MPI16 S','MPI16 E','OpenMP16 S','OpenMP16 E'])
    checked=[]
    expected=[]
    for N in [384,512,768,1024]:
        cells=[str(N),f"{float(selected[N,'serial',1]['median_seconds']):.9f}"]
        for kind in ['mpi','openmp']:
            r=selected[N,kind,16]
            cells.extend([f"{float(r['speedup_serial']):.4f}",f"{float(r['efficiency'])*100:.2f}%"])
        expected.append(cells)
        checked.append(N)
    require(grid==expected,'grid table differs from archived statistics')
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
    result['performance_tables']={'fixed_size_N':1024,'MPI_actual_P':[1,2,4,8,16],'OpenMP_actual_Q':[1,2,4,8,16],'fixed_size_rows_checked':len(fixed),'grid_metrics':['串行耗时Ts（秒）','MPI16 S','MPI16 E','OpenMP16 S','OpenMP16 E'],'grid_total_columns':6,'grid_rows_checked':len(grid),'method':'逐行逐单元格对照归档CSV；耗时9位、S四位、效率百分数两位'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
