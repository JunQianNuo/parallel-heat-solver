<!-- ppt-master-schema: design-spec/v1 -->
# Heat Solver Defense - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | heat-defense_ppt169_20261112 |
| Canvas Format | ppt169, 1280 × 720 |
| Page Count | 12 |
| Primary Language | zh-CN |
| Target Audience | 并行与分布式计算课程教师 |
| Communication Intent | 在5分钟内解释算法与并行实现，以真实验证和性能证据说明完成情况，披露AI与核查 |
| Desired Audience Outcome | 教师能理解数据归属、时间层同步、基线与计时，判断结论的证据及限制 |
| Core Message / Ask / Action | 正确性有证据，并行收益有条件 |
| Delivery Context | 本人现场主讲；8页正文280秒，20秒机动；4页备份用于提问 |
| Artifact Afterlife | 备注、来源与生成源支持会后审阅和复核 |
| Reading Mode | presentation |
| Content Strategy | 内容为讲述精简重组，数字与结论保留原证据口径 |
| Design Style | 自由设计；算法讲解＋计算流程＋证据陈述组合 |
| AI Image Acquisition Path | not applicable |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | enabled — explicit user confirmation |
| Custom Animations | disabled — explicit user confirmation, all-motion scope |
| Narration Audio | disabled — explicit user confirmation |
| Created Date | 2026-11-12 |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280 × 720 |
| viewBox | `0 0 1280 720` |
| Margins | 56 px |
| Content Area | x=56..1224, y=140..640 |

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Mode References**: instructional
- **Mode Behavior**: 先定义五点更新，再对照解释MPI与OpenMP的归属/同步，随后给出正确性与性能证据，每页一个可复核判断。
- **Visual style**: custom
- **Visual Style References**: swiss-minimal
- **Visual Style Behavior**: 参考本地两份PPT模板：深蓝底封面/结束页、白底正文、浅蓝分区、铜金强调；清晰左对齐标题和大留白；算法示意承担页面主体，结果页用曲线和大数字形成焦点，灰/模板蓝/铜金持续标识串行/MPI/OpenMP；备份原图保持已验收原色，细线建立层级。
- **Theme**: 五点网格与旧层/新层作为算法页连续线索，结果页以数值和比较承担视觉重量。
- **Tone**: 清晰、审慎、可解释。

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #FFFFFF | 正文页面背景；封面/结束页采用Primary深蓝 |
| Secondary background | #EDF3FA | 算法区背景 |
| Primary | #124C8D | 模板深蓝：标题、封面和结束页 |
| Accent | #C38749 | OpenMP |
| Secondary accent | #477CB3 | MPI |
| Body text | #273848 | 正文 |
| Secondary text | #627487 | 串行/注释 |
| Divider | #CCD8E7 | 网格/分隔 |
| On-blue accent | #EDC188 | 模板深底上的浅金强调 |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | 明确的无衬线粗体 | Microsoft YaHei | Arial | sans-serif |
| Body | 投影可读无衬线 | Microsoft YaHei | Arial | sans-serif |

- **Title stack**: Microsoft YaHei, Arial
- **Body stack**: Microsoft YaHei, Arial

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 32 |
| Title | 46 |
| Cover | 64 |
| Hero | 72 |
| Subtitle | 36 |
| Lead | 34 |
| Annotation | 24 |
| Footnote | 16 |

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: 标题给判断，中央示意/数据给依据，下方保留解释边界。
- **Composition tendency**: 算法页用主图与短说明；结果页用主图与右侧关键数字；备份整幅原图。
- **Cross-page continuity**: 五点网格从封面延续到更新与分工示意；灰/模板蓝/铜金保持实现语义。
- **Spacing posture**: 正文疏朗，备份图信息密集，结束页降低负荷。
- **Spacing anchors**: page margin=56; block gap=28; column gutter=40; corner radius=0; body leading=46.

## VI. Icon Usage Specification

- **Primary bundled library**: none

| Icon Path | Suitable Scenarios |
| --- | --- |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 02-speedup.png | 2080 × 1440 | 13:9 | 完整四组强扩展 | Chart | 全幅保留所有面板与脚注，旁列读取说明 | no-crop | user | Existing | results/figures/large-02-r1-viz-01/02-speedup.png | embedded | local |
| 05-grid-speedup.png | 2560 × 1600 | 8:5 | 固定人数跨网格比较 | Chart | 全幅保留坐标与区间，在侧边给出非单调提醒 | no-crop | user | Existing | results/figures/large-02-r1-viz-01/05-grid-speedup.png | embedded | local |

## IX. Content Outline

### Part 1: Main Talk

#### Slide 01 - 从五点更新到真实并行收益

- **Audience move**: 尚不清楚项目→了解三程序及证据主线
- **Relationships**: membership: 三实现属于同一模型
- **Title**: 从五点更新到真实并行收益
- **Core message**: 串行、MPI、OpenMP属于同一数学模型；正确性证据先于性能判断
- **Content**: 完整课题名；独立串行/MPI/OpenMP；正确性有证据，并行收益有条件；姓名学号待填写；封面五点网格仅结构示意
- **Cover impact**: 五点更新→三种程序→真实收益；五点结构示意结合大标题。

#### Slide 02 - 五点更新只读旧层，整层完成再交换

- **Audience move**: 知道题目→理解旧层依赖及稳定性
- **Relationships**: order: 旧层读→新层写→交换；link: 中心与四邻居
- **Title**: 五点更新只读旧层，整层完成再交换
- **Core message**: 模型：单位区域、零边界、正弦初值；h=1/N、dt=T/M；r≤1/4；双缓冲M次更新；时间一阶/空间二阶
- **Content**: 五点网格示意；旧层→新层；稳定性与双缓冲；解析解只用于核验
- **Mathematical content**: U_{ij}^{n+1}=(1-4r)U_{ij}^{n}+r(U_{i-1,j}^{n}+U_{i+1,j}^{n}+U_{i,j-1}^{n}+U_{i,j+1}^{n})

#### Slide 03 - MPI分连续行，先换halo再更新

- **Audience move**: 知道五点依赖→理解进程分块和邻居行
- **Relationships**: membership: 内部行归rank；link: 邻rank旧行交换；order: 通信→更新→交换
- **Title**: MPI分连续行，先换halo再更新
- **Core message**: 独立串行是主基线；N=8/P=3分3/2/2行；每步两次旧层Sendrecv；PROC_NULL不自动清零；P≤N−1为本实现约束
- **Content**: 拥有行与halo；全局行1–3/4–5/6–7；通信→更新→交换；实际P来自Comm_size

#### Slide 04 - OpenMP分整行，两道屏障守住时间层

- **Audience move**: 知道MPI→理解共享双缓冲与线程同步
- **Relationships**: membership: 行属于线程；order: 更新完成→交换→进入下一层
- **Title**: OpenMP分整行，两道屏障守住时间层
- **Core message**: static,1循环分行；old/next共享，循环变量私有；for屏障→single交换→single屏障；Q>N−1合法；请求/实际团队分开
- **Content**: N7/Q4行归属{1,5}/{2,6}/{3}/{4}；实际Q在推进团队读取；每点一线程写

#### Slide 05 - 精度与并行一致性分别验证

- **Audience move**: 知道实现→理解三层验证和联合加密
- **Relationships**: contrast: 解析精度与串并行一致性；order: 三档联合加密
- **Title**: 精度与并行一致性分别验证
- **Core message**: 连续E、离散模态、串行D三层检查；N20/40/80且M400/1600/6400，E=1.1262e-4/2.8181e-5/7.0470e-6；误差约缩小4倍；小规模D≤1e-13
- **Content**: 联合二阶不是时间二阶；边界/奇偶步/不均匀分块/线程多于行/稳定性端点；历史M3 Debug/Release各19/19

#### Slide 06 - N=1024：MPI16加速3.35倍，OpenMP8为1.80倍

- **Audience move**: 知道正确→理解正式计时、基线与有限收益
- **Relationships**: contrast: 同规模独立串行与并行；order: 并行度增加
- **Title**: N=1024：MPI16加速3.35倍，OpenMP8为1.80倍
- **Core message**: N1024/M65536/T0.01/alpha1；Ts35.3892秒；MPI16 10.5662秒/S3.3493；OpenMP8 19.6692秒/S1.7992；OpenMP16 21.4382秒；44配置×10正式/44预热；推进计时；同网格独立串行中位数比
- **Content**: P/Q1/2/4/8/16曲线与探索性95%区间；时间min/max不是区间；16逻辑CPU/14WSL可见core，含兄弟线程
- **Visualization**: n1024-speedup — 同网格S与探索性不对称区间的数值坐标图；no-template-match。
- **Native-ready**: n1024-speedup=no
- **Composition**: 左侧主曲线保留不对称bootstrap误差线，右侧大数字；闭合原生chart payload不支持这组自定义不对称区间，保留可编辑矢量图元。

#### Slide 07 - 规模、实施因素与环境共同限制收益

- **Audience move**: 看到收益→理解扩大工作量与因果边界
- **Relationships**: contrast: 支持的实施因素与未确定机制
- **Title**: 规模、实施因素与环境共同限制收益
- **Core message**: 跨N时M增加，W=M(N−1)²，不称弱扩展；原扩大W约随p增长但时间不恒定；Amdahl不反推真实f，Gustafson未测sigma；诊断支持计算上下文/行划分，未进入正式实现
- **Content**: MPI收益不随N单调；OpenMP16不保证优于8；非独占WSL、轮次趋势、UTC回退、未外部物理校准；硬件根因未定

#### Slide 08 - AI辅助实现，真实核查支撑结论

- **Audience move**: 了解结果→理解实际分工与核查责任
- **Relationships**: order: AI输出→真实检查→修正/采纳
- **Title**: AI辅助实现，真实核查支撑结论
- **Core message**: Codex辅助实现/测试/实验/分析/材料；本人负责范围/管理/审核/答辩；MPI启动器重定向错误留证，改rank内验证后通过；不虚构人工复测
- **Content**: 正确性有证据，并行收益有条件；阶段验收不替代本材料审核；个人信息和人工演练待本人完成
- **Closing impact**: 正确性有证据，并行收益有条件；用一条核查实例与明确分工收束。

#### Slide 09 - 备份：计时边界与三个统计口径

- **Audience move**: 需要追问→可区分基线、计时与统计
- **Relationships**: contrast: 三种实现计时；contrast: 三批统计对象
- **Title**: 备份：计时边界与三个统计口径
- **Core message**: serial含step检查/边界/更新/swap；MPI含halo与等待取rank最大，归约/收集在外；OpenMP含团队进出与逐层同步；初始化验证输出在外
- **Content**: 原M4 23配置/115正式，中位数比/min-max；诊断01 215预热/2560正式，配对比率中位数；02-r1 44预热/440正式，同轮bootstrap；停止02 0正式

#### Slide 10 - 备份：四组固定N/M的完整强扩展

- **Audience move**: 需要完整矩阵→读取四网格全部资源结果
- **Relationships**: contrast: 四个固定问题的强扩展
- **Title**: 备份：四组固定N/M的完整强扩展
- **Core message**: 原图02-speedup；4组N384/512/768/1024；每点同网格串行；区间为探索性95%；16逻辑CPU覆盖14core
- **Content**: 保留全部原图坐标/区间/脚注；MPI16 S3.4885/2.8183/2.9596/3.3493；OpenMP16非总优于8
- **Images**: 02-speedup.png，完整原图保留不裁切；旁列口径提醒。

#### Slide 11 - 备份：跨网格比较不能称弱扩展

- **Audience move**: 需要扩展解释→区分N/M共同变化
- **Relationships**: contrast: 同人数跨网格；link: N增加同时M增加
- **Title**: 备份：跨网格比较不能称弱扩展
- **Core message**: 原图05-grid-speedup；T0.01/alpha1/r0.16；M=N²/16；W约N⁴；各点使用各自串行基线
- **Content**: MPI收益随N非单调；OpenMP16不保证优于8；跨N不单独分离每步粒度效应
- **Images**: 05-grid-speedup.png，完整原图保留不裁切；旁列口径提醒。

#### Slide 12 - 备份：定律、时钟与归因的适用边界

- **Audience move**: 需要机制追问→理解未被数据证明的部分
- **Relationships**: contrast: 理想模型与实际测量；contrast: 支持与未确定
- **Title**: 备份：定律、时钟与归因的适用边界
- **Core message**: Amdahl常数f假设不足，f_eff不是代码占比；Gustafson相近并行时间未满足且sigma未测；34/44趋势；11处UTC回退；单调计时但未外部物理校准
- **Content**: 诊断MPI公共内核和OpenMP连续划分支持实施因素；未证明唯一缓存/带宽/伪共享或宿主机制；全部慢样本保留

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under `notes/`
- **Content**: 基于最终SVG，前8页沿用已整理讲稿并校准图示，备份页给出答辩解释；来源路径保留于页面页脚，未发生的人工核查不补写。
- **Total duration**: 正文280秒预算＋20秒机动；备份不纳入5分钟；字数估算不是人工实讲。
- **Notes style**: 中文口语化解释。
- **Presentation purpose**: 解释算法/实现/验证与真实收益及限制，披露AI使用与修正。
