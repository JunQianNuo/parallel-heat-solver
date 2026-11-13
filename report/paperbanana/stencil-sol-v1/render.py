#!/usr/bin/env python3
"""Author the editable SVG and render PNG/PDF. No model or network calls."""
import argparse, os, re
from pathlib import Path
from html import escape
p=argparse.ArgumentParser(); p.add_argument('--fontconfig'); p.add_argument('--font',type=Path,default=Path('/mnt/c/Windows/Fonts/simhei.ttf'),help='Installed Chinese TrueType font for superscript text measurement'); a=p.parse_args()
if a.fontconfig: os.environ['FONTCONFIG_FILE']=str(Path(a.fontconfig).resolve())
import cairosvg
from PIL import ImageFont
FONT=ImageFont.truetype(str(a.font),100)
D=Path(__file__).resolve().parent
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1080" viewBox="0 0 1800 1080" role="img" aria-labelledby="title desc">', '<title id="title">二维五点显式更新与双缓冲时间推进</title><desc id="desc">旧层五个轴向点加权求和，写入独立新层。整层完成后交换缓冲并累计步数，恰好推进M步。</desc>', '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#115EA2"/></marker></defs>', '<rect width="1800" height="1080" fill="white"/>']
blue='#115EA2'; dark='#092F51'; grid='#C9D7E3'
def path(d,stroke=blue,w=4,arrow=False,dash=False): s.append(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"'+(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="10 9"' if dash else '')+'/>')
def txt(x,y,t,size=36,fill='#111111',anchor='middle',weight='normal'):
 if '^' in t:
  parts=re.split(r'\^([0-9M])',t); spans=[]
  for k,part in enumerate(parts):
   fs=size*(.7 if k%2 else 1); width=FONT.getlength(part)*fs/100
   spans.append((part,fs,-size*.38 if k%2 else 0,width))
  width=sum(v[3] for v in spans); cursor=x-width/2 if anchor=='middle' else x
  s.append('<g aria-label="'+escape(t)+'">')
  for part,fs,dy,w in spans:
   s.append(f'<text x="{cursor}" y="{y+dy}" font-family="SimHei, Arial, sans-serif" font-size="{fs}" fill="{fill}">{escape(part)}</text>');cursor+=w
  s.append('</g>');return
 content=escape(t)
 s.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="SimHei, Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}">{content}</text>')

def box(x,y,w,h,fill='white',stroke=grid,r=20):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')
def circle(x,y,r,fill,stroke=blue):s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="4"/>')
# Zones: clearly separate memory buffers and arithmetic.
box(42,30,670,530,'#F8FBFE');box(1202,30,556,530,'#F8FBFE')
txt(377,75,'旧层 old · n',44,dark,weight='bold');txt(1480,75,'新层 next · n+1',44,dark,weight='bold')
# Local grid, not the physical domain boundary.
s.append('<g id="old-layer" data-layer="n" data-access="read">')
for x in [115,245,375,505,635]:path(f'M{x} 138V482',grid,2)
for y in [160,300,440]:path(f'M95 {y}H655',grid,2)
for x,y,label,weight in [(375,160,'(i-1, j)','r'),(245,300,'(i, j-1)','r'),(505,300,'(i, j+1)','r'),(375,440,'(i+1, j)','r')]:
 circle(x,y,31,'white');s[-1]=s[-1].replace('/>',f' data-site="{ { (375,160):"north",(245,300):"west",(505,300):"east",(375,440):"south" }[(x,y)]}" data-weight="r" data-layer="n"/>');txt(x,y+12,weight,38,blue)
 # labels sit outside their circles without sharing the center weight zone
 if y==160:txt(x,y-43,label,30)
 elif y==440:txt(x,y+65,label,30)
 elif x==245:txt(150,365,label,32)
 else:txt(590,365,label,32)
circle(375,300,48,blue);s[-1]=s[-1].replace('/>',' data-site="center" data-weight="1-4r" data-layer="n"/>');txt(375,311,'1-4r',32,'white');txt(375,377,'(i, j)',33)
txt(375,539,'局部示意 · old 只读',34,dark)
s.append('</g><g id="weighted-sum">')
# Five contributions are indicated by the aggregate connector; weights live on exactly five nodes.
path('M728 300H814',arrow=True)
circle(915,300,76,'#EAF2F8');txt(915,314,'Σ',74,blue)
txt(915,178,'五点加权',40,dark,weight='bold');txt(915,440,'中心 × (1-4r)',34);txt(915,485,'四邻点各 × r',34)
path('M1004 300H1265',arrow=True);txt(1115,269,'写入',36,blue)
s.append('</g><g id="next-layer" data-layer="n+1" data-access="write">')
for x in [1290,1385,1480,1575,1670]:path(f'M{x} 160V440',grid,2)
for y in [160,230,300,370,440]:path(f'M1290 {y}H1670',grid,2)
circle(1480,300,43,blue);txt(1480,312,'U',40,'white');txt(1480,494,'同一坐标 (i, j)',38,dark)
txt(1480,539,'独立缓冲 · next 只写',34,dark)
s.append('</g>')
# Concise numerical constraints and global boundary statement.
txt(900,610,'r = αΔt/h^2 ≤ 1/4     ·     时间一阶 / 空间二阶',38,dark)
path('M44 647H1756',grid,2)
mechanism_elements=list(s)
# Time loop strip.
s.append('<g id="time-loop">')
box(42,689,292,174,'#F8FBFE');txt(188,739,'初始化',40,dark,weight='bold');txt(188,790,'old = U^0',36);txt(188,837,'next = 0, n = 0',32)
box(390,689,366,174,'#EAF2F8',blue);txt(573,741,'更新全部内部点',38,dark,weight='bold');txt(573,790,'old → next',36,blue);txt(573,836,'全局四条物理边界 = 0',30)
path('M341 776H380',arrow=True)
box(812,689,252,174,'#F8FBFE');txt(938,757,'整层完成',40,dark,weight='bold');txt(938,813,'再交换',34,dark)
path('M765 776H802',arrow=True)
box(1120,689,270,174,'#EAF2F8',blue);txt(1255,742,'交换 old / next',32,dark,weight='bold');txt(1255,798,'n ← n+1',38,blue);txt(1255,841,'新层成为旧层',30,dark)
path('M1072 776H1110',arrow=True)
s.append('<path d="M1537 692L1642 776L1537 860L1432 776Z" fill="white" stroke="#115EA2" stroke-width="3"/>');txt(1537,788,'n < M?',35,dark)
path('M1399 776H1422',arrow=True)
# Continue branch returns to update, not initialization. The next step reads newly swapped old.
path('M1537 869V946H573V874',arrow=True);txt(1020,934,'是：用交换后的 old 继续下一步',34,blue)
path('M1650 776H1720V1018H1585',arrow=True);txt(1667,910,'否',38,blue)
box(1115,984,470,68,'#F8FBFE');txt(1350,1030,'n = M：取 old = U^M，结束',32,dark)
txt(400,1032,'M ≥ 1；共推进 M 步，每层只交换一次',32,dark)

def export(name,items,height):
 items=list(items);items[0]=items[0].replace('height="1080"','height="'+str(height)+'"').replace('1800 1080','1800 '+str(height))
 if name=='mechanism-wide': items[1]='<title id="title">五点显式单点更新机理</title><desc id="desc">从旧层n的中心和四个轴向邻点读取，中心权重1-4r，邻点各r，加权写入独立新层n+1的同坐标。</desc>'
 if name=='time-loop-wide': items[1]='<title id="title">双缓冲整层推进控制流程</title><desc id="desc">初始化后更新全部内部点，保持物理零边界，整层完成后交换并累计步数；n小于M继续，否则从old取最终解。</desc>'
 svg='\n'.join(items+['</svg>']);(D/(name+'.svg')).write_text(svg,encoding='utf-8')
 cairosvg.svg2png(bytestring=svg.encode(),write_to=str(D/(name+'.png')),output_width=3600,output_height=height*2)
 cairosvg.svg2pdf(bytestring=svg.encode(),write_to=str(D/(name+'.pdf')))
s.append('</g>')
export('diagram',s,1080)
# Wide variants fit a 1200×520 slide content region without height scaling.
mechanism_elements=[v.replace('font-size="30"','font-size="36"').replace('font-size="32"','font-size="36"').replace('font-size="33"','font-size="36"').replace('font-size="34"','font-size="38"') for v in mechanism_elements]
export('mechanism-wide',mechanism_elements,650)
s=s[:4]
s.append('<g id="time-loop">')
box(35,40,300,188,'#F8FBFE');txt(185,93,'初始化',44,dark,weight='bold');txt(185,151,'old = U^0',42);txt(185,204,'next = 0, n = 0',36)
box(390,40,400,188,'#EAF2F8',blue);txt(590,94,'更新全部内部点',44,dark,weight='bold');txt(590,151,'old → next',44,blue);txt(590,204,'全局四条物理边界 = 0',34)
path('M343 134H380',arrow=True)
box(845,40,270,188,'#F8FBFE');txt(980,117,'整层完成',44,dark,weight='bold');txt(980,179,'再交换',42,dark)
path('M798 134H835',arrow=True)
box(1170,40,300,188,'#EAF2F8',blue);txt(1320,100,'交换 old / next',36,dark,weight='bold');txt(1320,160,'n ← n+1',44,blue);txt(1320,208,'新层成为旧层',36,dark)
path('M1123 134H1160',arrow=True)
s.append('<path d="M1630 43L1750 134L1630 225L1510 134Z" fill="white" stroke="#115EA2" stroke-width="3"/>');txt(1630,149,'n < M?',42,dark)
path('M1478 134H1500',arrow=True)
path('M1630 235V330H590V238',arrow=True);txt(1075,310,'是：读取交换后的 old，继续下一步',40,blue)
box(900,414,720,100,'#F8FBFE');txt(1260,477,'n = M：取 old = U^M，结束',42,dark)
path('M1760 134H1780V464H1620',arrow=True);txt(1724,374,'否',42,blue)
txt(440,473,'M ≥ 1；每层只交换一次',40,dark)
s.append('</g>')
export('time-loop-wide',s,550)
print('Wrote overview and two wide SVG / PNG / PDF variants')
