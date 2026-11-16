<!-- ppt-master-schema: design-spec/v1 -->
# Heat Solver Defense - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | heat-defense_ppt169_20261112 |
| Canvas Format | ppt169, 1280 × 720 |
| Page Count | 14 |
| Primary Language | zh-CN |
| Target Audience | 并行与分布式计算课程教师 |
| Communication Intent | 按用户2026-11-16指定顺序汇报：模型与条件→均匀空间/时间网格→五点显式差分机理→串行推进→MPI与OpenMP的分工、通信/同步→正确性和主要性能结果；最后披露AI使用及修正实例 |
| Desired Audience Outcome | 教师能沿图和证据追问：为什么必须分开新旧层、halo/屏障为何在该位置、E∞和D∞各检验什么、加速比/效率如何计算，以及Amdahl/Gustafson哪些前提未被实验满足；这是讲述目标，不预先宣称使用者已掌握 |
| Core Message / Ask / Action | 正确性有证据，并行收益有条件 |
| Delivery Context | 本人现场主讲，280秒并预留20秒；用户已确认10页正文＋4页备份。首页兼题名和模型，不另设纯封面或目录页 |
| Artifact Afterlife | 备注、来源与生成源支持会后审阅和复核 |
| Reading Mode | presentation |
| Content Strategy | 以用户最新保存的FINAL_REPORT.md为内容主稿，按计算过程组织大图、短句与关键结果；不按函数名或工程记录开篇，不在投影正文展示仓库路径/Fact IDs，数字与结论保留原统计口径 |
| Design Style | 按用户指定《单幅图像去雾-第二组》参考重做页眉、疏密、推进、黑体/楷体及字号字色 |
| AI Image Acquisition Path | not applicable |
| Generation Mode | continuous |
| Spec Refinement | enabled — 沿用用户逐步确认与refine-spec要求；2026-11-14批准只覆盖v4。2026-11-16用户回复“审阅完备”，批准本次内容重排并补充面向非实现者的要求，进入Gate 2 |
| Speaker Notes | enabled — explicit user confirmation |
| Custom Animations | disabled — explicit user confirmation, all-motion scope |
| Narration Audio | disabled — explicit user confirmation |
| Created Date | 2026-11-12 |
| Revised Date | 2026-11-16 |
| Review Status | 本轮已批准：正文10页＋备份4页、280秒；按最新报告和非实现者阅读条件制作v5，保留既定视觉设置。旧v4-r1成品作为历史保存 |

### Evidence Ledger

本轮只读复核教师任务书第1、3页文字、最新报告和三种求解器。任务书要求5分钟介绍算法、实现、主要测试结果及AI使用与修正。下表只供制作与备注核对，不作为面向教师的页内引用栏；数据均为归档事实，不新增实验或假设样本。

| Fact ID | 依据 | 用途 |
| --- | --- | --- |
| F-COURSE | 本地只读`docs/sources/final.pdf`第1、3页；[SPEC](../../SPEC.md) | 教师要求、模型、稳定性、性能方法与AI披露 |
| F-MODEL | [DESIGN第1节](../../docs/DESIGN.md) | 网格/时间、格式、稳定性与双数组 |
| F-SERIAL | [heat.cpp](../../src/heat.cpp) | 独立串行、边界、step/swap、计时 |
| F-MPI | [heat_mpi.cpp](../../src/heat_mpi.cpp) | 连续行分块、两次Sendrecv、halo、MPI计时 |
| F-OMP | [heat_openmp.cpp](../../src/heat_openmp.cpp) | static,1、共享/私有、两道屏障、请求/实际Q |
| F-VALID | [M3误差CSV](../../results/validation/m3-errors.csv)、[报告第4节](../FINAL_REPORT.md) | E∞/D∞、默认联合网格加密及两类参考，不恢复用户已删除的第三类参考 |
| F-BASE | [原M4协议](../../results/performance/baseline/README.md)、[统一结果](../../results/RESULTS.md) | 原23配置/115正式、扩大工作量与独立基线 |
| F-DIAG | [统一结果的诊断01](../../results/RESULTS.md#补充诊断运行01)、[报告第6.5节](../FINAL_REPORT.md) | 215预热/2560正式调用、隔离变体与支持程度 |
| F-LARGE | [02-r1统计CSV](../../results/performance/large-02-r1/m4-diagnostic-02-r1.csv)、[统一结果](../../results/RESULTS.md) | 44配置/44预热/440正式、时间/S/E、资源和趋势 |
| F-LAWS | [报告第6.3—6.4节](../FINAL_REPORT.md) | 两个定律、吞吐增长及其推断边界；旧答辩问答是待同步派生材料 |
| F-REPORT | [最新书面报告Markdown](../FINAL_REPORT.md) | 讲述措辞和章节事实的主稿；报告PDF尚未同步用户最新修改；PPT报告副本已同步，仅归一化相对链接 |
| F-AI | [AI使用记录](../../docs/AI_USAGE.md) | 实际辅助环节、失败修正与用户角色，未发生的人工核查不补写 |
| F-FIG | [五点机理图说明](../paperbanana/stencil-sol-v1/README.md) | 已有原生SVG图源及完整时间循环，供重排参考 |

### Audience Self-Containment Requirements

用户2026-11-16补充：PPT面向非实现者；听众只接触PPT和最终报告，无法阅读仓库或实验专属报告。投影正文及备份页均不出现内部批次代号、文件路径、提交哈希、Fact IDs，或“参见实验报告/日志/协议”等阅读前提。必要模型、参数、行归属、通信/同步顺序、比较对象、硬件及计时含义、样本数和统计限定在PPT/最终报告内解释完整。制作台账仍保留来源，讲稿不能用内部链接代替解释。相应表述调整属于本次已确认要求，不再重开设计选择。

### Four Understanding Requirements

- **懂算法**：不止读出公式，要解释五点依赖为什么都来自n层、双数组为何防止本步污染、交换后哪份是最终层；通过二维权重说明r≤1/4，而不是沿用一维1/2。
- **懂代码**：能沿“归属→拿到依赖→更新→换层”解释MPI；沿“循环分行→唯一写者→for屏障→single换层→single屏障”解释OpenMP，并区分请求值与实际值。
- **懂验证**：连续误差E∞与实现差D∞是两种问题；加密同时调整M，观测约二阶属于Δt∝h²的联合加密，不把并行一致或一次正常退出当作精度证明。
- **懂性能**：独立串行为主基线，推进所需操作都计时；明确S和E及实际P/Q，能用两个理想模型讨论前提和限制；跨N/M的现有实验不称为弱扩展。

这四项约束§IX及讲述内容。规范审阅阶段未更新旧锁或制作；用户回复“审阅完备”后已同步锁、14页源、讲稿与成品。没有新增实验或修改求解器；旧v4-r1成品及其检查保持历史语境，新稿以v5独立检查为准。

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280 × 720 |
| viewBox | `0 0 1280 720` |
| Margins | 40 px minimum |
| Content Area | x=40..1240, y=130..650 |

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Mode References**: instructional
- **Mode Behavior**: 研究问题与路线→数值原理→MPI/OpenMP实现→正确性与性能证据→结论与评价边界。
- **Visual style**: custom
- **Visual Style Behavior**: 仿照指定PDF的深色章节导航、蓝色通栏标题、白底黑字、蓝字强调、双条页脚；页面用少量文字和单幅图解释一个问题，不用宣传式大数字/口号或反复的说明框。
- **Theme**: 参考本地只读docs/sources/PPT模板/单幅图像去雾-第二组.pdf，不复制原页、姓名、校徽或图片。参考为4:3，本交付沿用已确认16:9；竖向比例按720/272.13缩放，导航与标题横向铺满。
- **Tone**: 简洁、学术答辩、先解释再举证。

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #FFFFFF | 白底正文 |
| Primary | #115EA2 | 通栏标题、重点蓝字、MPI |
| Navigation | #092F51 | 深色章节导航 |
| Footer lower | #0B3D69 | 深蓝页脚下条 |
| Inactive | #8497A8 | 未激活导航和串行参照 |
| Body text | #000000 | 正文与OpenMP图线 |
| Divider | #C9D7E3 | 图线与细分隔 |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | 参考FandolHei黑体 | SimHei | Arial | sans-serif |
| Cover | 参考黑体封面 | SimHei | Arial | sans-serif |
| Body | 参考FandolKai楷体 | KaiTi | Arial | serif |
| Lead | 参考蓝色黑体强调 | SimHei | Arial | sans-serif |
| Navigation | 参考黑体导航 | SimHei | Arial | sans-serif |
| Footnote | 参考黑体双条页脚 | SimHei | Arial | sans-serif |
| Data | 清晰的拉丁数字 | Arial | Arial | sans-serif |

- **Title stack**: SimHei, Arial
- **Cover stack**: SimHei, Arial
- **Body stack**: KaiTi, Arial
- **Lead stack**: SimHei, Arial
- **Navigation stack**: SimHei, Arial
- **Footnote stack**: SimHei, Arial
- **Data stack**: Arial
- **Role rationale**: PDF为FandolHei/FandolKai；Windows PowerPoint使用本机已有黑体/楷体对应字形，数学仍为Cambria Math。不是沿用前版微软雅黑。

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 40 |
| Title | 44 |
| Cover | 58 |
| Lead | 40 |
| Annotation | 30 |
| Navigation | 20 |
| Footnote | 20 |
| Data | 30 |
| Diagram / formula | 36 |
| Compact lead | 34 |
| Math script | 22 |

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: 顶部三段导航标记阶段，蓝条白字标题提出本页主题，白底正文给一个解释或证据，蓝色短句收束。
- **Composition tendency**: 图文并置或公式→变量说明→结论；简单段落/编号，减少卡片。
- **Cross-page continuity**: 问题与路线／数值与并行方法／结果与讨论三级章节导航，全页一致；导航圆点指示本节位置；上下双色页脚。
- **Spacing posture**: 主讲页每页一个主题，2–4个主要信息单元，正文40px；细节与限定放入备份/备注。
- **Spacing anchors**: minimum page margin=40（与§II及v3一致）; block gap=28; column gutter=40; corner radius=0; body leading=48.

## VI. Icon Usage Specification

- **Primary bundled library**: none

| Icon Path | Suitable Scenarios |
| --- | --- |

## VII. Visualization Reference List

| Page | Family | Template | Usage |
| --- | --- | --- | --- |
| P07 | table | record_table | 三组联合加密的N、M与最大解析误差 |
| P08 | chart | line_chart | 最大网格下MPI/OpenMP随实际并行度变化的加速比 |
| P09 | table | metric_table | 扩大工作量后MPI与OpenMP的吞吐增长 |
| P11 | table | comparison_matrix | 三种实现的计时范围与环境配置 |
| P12 | chart | line_chart | 四个固定网格的完整加速比曲线 |
| P13 | chart | line_chart | 固定并行度时跨网格的加速比 |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 02-speedup.png | 1980 × 1260 | 11:7 | 四组固定网格的完整结果 | Chart | 保留全部面板与坐标，统计含义由配文说明 | no-crop | user | Existing | results/figures/large-02-r1-viz-01/02-speedup.png | embedded | local |
| 05-grid-speedup.png | 2520 × 1350 | 28:15 | 固定并行度跨网格比较 | Chart | 全幅展示，配文指出N和M共同变化 | no-crop | user | Existing | results/figures/large-02-r1-viz-01/05-grid-speedup.png | embedded | local |

### Existing Vector References

已有[五点读写宽图](../paperbanana/stencil-sol-v1/mechanism-wide.svg)与[时间循环宽图](../paperbanana/stencil-sol-v1/time-loop-wide.svg)，供P03的旧层五点读取和P04的完整时间循环使用。它们用于科学关系与构图参考；正式页面按既定大字号重排，不能把整张复杂图缩成截图。网格、五点、串行、MPI、OpenMP图保留可编辑关系，不发起新的图像API调用。

两幅统计图采用当前results中的版本。它们在报告修订期间已经重绘，旧PPT的images副本不再代表当前图；已同步工作区副本并逐字节核对两图及PPT包内图像，不覆盖results原件。图注保留bootstrap探索性区间含义，不能因原图取消脚注就省略统计说明。

## IX. Content Outline

### Part 1: From the physical model to the measured results

用户已确认P01–P10为正文、P11–P14为备份。正文25/20/40/20/35/30/25/40/30/15秒，共280秒，另留20秒机动。首页兼题目与模型，不单列纯封面或目录。相比旧版，网格和串行推进各有独立页；性能拆成固定规模与扩大工作量两页。

内容面向课程教师，不复述课程中已有的基本概念定义。每页先给图和短句，讲稿说明因果；不以函数名、工程编号或仓库路径开场。主图不依赖配音、动画或自动翻页。三段页眉导航仍为“问题与模型／数值与并行方法／结果与讨论”，对应P01–P02／P03–P06／P07–P10；旧页脚与页码在获准制作时统一更新。

P02–P06复用同一个示意网格N=8：每方向9个节点、7条内部行。MPI与OpenMP示意均用3个执行单元，让连续分块与交错行分配的差别可见。示意参数仅解释结构，不冒充新增运行结果；性能采用归档实际配置。每页Rhythm是正文密度判断，不要求为制造变化插入无内容页面。

#### Slide 01 - 模型与条件

- **File**: 01_model.svg
- **Timing**: 25秒，累计0:25。
- **Rhythm**: anchor
- **Audience move**: 只知项目题名→知道薄板上的求解区域、初边值与目标输出。
- **Relationships**: membership: 单位薄板、零温四边和正弦初值共同定义问题；order: 初始温度分布→推进至T→终温场。
- **Title**: 二维热传导方程的串行与并行数值求解
- **Core message**: 计算四边恒为零温的单位薄板在时刻T的温度场。
- **Content**: 题名、姓名学号待填写。展示热方程、单位区域、四边零温、正弦初值；用薄板示意表达中心较热。短句“同一问题：独立串行／MPI／OpenMP”。α为正的热扩散率。输出是逐步求得的温度场，不以解析式直接生成数值结果。
- **Mathematical content**: u_t=\alpha(u_{xx}+u_{yy}),\quad (x,y)\in(0,1)^2,\quad 0<t\le T;\quad u|_{\partial\Omega}=0;\quad u(x,y,0)=\sin(\pi x)\sin(\pi y)
- **Speaking focus**: 从薄板温度演化进入，再指出三种实现共同完成这个问题；解析解留到验证页，避免在模型页堆两套公式。
- **Composition**: 题名兼开场，薄板示意与模型条件构成一个清楚的视觉主体；不另占一页目录。
- **Cover impact**: 绑定“从已知初温求终温场”的具体问题，完整技术题名保留；构图服从已确认页眉和大字号。
- **Fact IDs**: F-COURSE, F-MODEL, F-REPORT。

#### Slide 02 - 均匀网格

- **File**: 02_grid.svg
- **Timing**: 20秒，累计0:45。
- **Rhythm**: breathing
- **Audience move**: 理解连续薄板→能辨认网格节点、内部点、边界和时间层。
- **Relationships**: membership: 边界节点与内部节点组成同一空间网格；order: 每方向N等分→节点取值；order: 0到T分成M步→逐层推进。
- **Title**: 均匀网格
- **Core message**: 空间用等距节点表示，时间按固定步长逐层推进。
- **Content**: N=8示意每方向8个区间、9个节点，突出一格宽h、一个内部点及四边零值；内部为7×7个更新点。旁列h=1/N及Δt=T/M；下方时间轴显示0、Δt、…、T及M步。明确N是区间数，不能画成每方向只有N个节点。行i对应x方向，列j对应y方向；后续页沿用这一约定。
- **Mathematical content**: h=1/N,\quad x_i=ih,\quad y_j=jh;\quad \Delta t=T/M,\quad t_n=n\Delta t;\quad (N+1)^2\ \text{节点},\quad (N-1)^2\ \text{内点}
- **Speaking focus**: 只讲划分与需要更新的区域，不在本页推导差分；下一页将这个网格中的一个内部点放大。
- **Composition**: 一个大网格与一条时间轴构成主图，边界和内点有清楚区别；短公式贴近对应对象。
- **Motion suggestion**: 沿用P01薄板轮廓，增加等距网格后成为本页主体；无动画时保持静态可读。
- **Fact IDs**: F-COURSE, F-MODEL, F-REPORT。

#### Slide 03 - 五点显式差分

- **File**: 03_stencil.svg
- **Timing**: 40秒，累计1:25。
- **Rhythm**: dense
- **Audience move**: 看到网格点→能沿读写方向解释一个内点如何由旧层算到新层。
- **Relationships**: link: 旧层中心与四个轴向邻点→加权求和→新层同坐标；contrast: 旧层只读与新层只写。
- **Title**: 五点显式差分
- **Core message**: 五个输入全部来自旧时间层，结果写入另一数组的同一位置。
- **Content**: 从P02的一个内点放大五点模板，中心权重1−4r，四邻点各r，不含对角点；明确标出时间层n与n+1、读入和写入。用“时间向前差分＋空间中心差分→五点更新式”交代来源。给出r=αΔt/h²≤1/4；五个权重非负且和为1。旧层old与新层next分开，防止本步读到已更新的邻点。
- **Mathematical content**: U_{ij}^{n+1}=(1-4r)U_{ij}^{n}+r\left(U_{i-1,j}^{n}+U_{i+1,j}^{n}+U_{i,j-1}^{n}+U_{i,j+1}^{n}\right);\quad r=\alpha\Delta t/h^2\le1/4
- **Speaking focus**: 沿五个旧值读入、求和、写新中心的方向讲机理，再说明稳定性和分开数组的原因。时间一阶、空间二阶；下一页解释从一次点更新到完整求解的循环。
- **Composition**: 大幅五点读写机理图为主体，公式、权重与坐标一一对应；整层循环移到P04，给公式和五点标注足够空间。
- **Motion suggestion**: P02选中的网格点成为本页中心，邻点位置关系延续；无需动画才能理解箭头。
- **Fact IDs**: F-COURSE, F-MODEL, F-SERIAL, F-FIG。

#### Slide 04 - 串行推进

- **File**: 04_serial.svg
- **Timing**: 20秒，累计1:45。
- **Rhythm**: breathing
- **Audience move**: 理解一次点更新→能解释完整温度场如何经过M步得到终值。
- **Relationships**: order: 初始化→遍历全部内部行列→完成整层→交换数组角色→重复至M步→输出；link: P03局部更新是遍历中的计算单元。
- **Title**: 串行推进
- **Core message**: 一个执行流程算完整层后换层，重复M次得到终温场。
- **Content**: old按初值初始化、next清零；每步清零新层四边，按行逐点完成全部内部计算；整层后交换old/next角色，不逐点复制全场；推进M次后从old取最终场，计算误差并输出。图中明确“还有时间步”回路和“已完成M步”出口。独立串行的推进时间Ts用于正式基线。
- **Speaking focus**: 交换发生在整层完成后；奇偶M都输出实际最终层。初始化和输出在计时外，M次推进在计时内；串行遍历无需线程屏障或邻居通信。不能用MPI1/OpenMP1代替这个独立基线。
- **Composition**: 完整求解循环为主图，五点模板缩成其中的计算单元；双数组角色交换清晰可见。
- **Motion suggestion**: P03的“读旧写新”成为本页遍历模块；图中保留同一old/next身份，显出本页新增的整层与循环层次。
- **Fact IDs**: F-SERIAL, F-MODEL, F-FIG。

#### Slide 05 - MPI行分块

- **File**: 05_mpi.svg
- **Timing**: 35秒，累计2:20。
- **Rhythm**: dense
- **Audience move**: 理解串行全场循环→能定位MPI进程的负责行、邻接数据和通信时机。
- **Relationships**: membership: 内部行连续分给各rank；link: 邻居的旧层拥有行提供本地halo；order: 交换旧层边界行→更新本地内点→本地换层。
- **Title**: MPI行分块
- **Core message**: 每个进程负责连续几行，每步先取邻居旧层数据，再计算自己的行。
- **Content**: 同一N=8网格的7条内部行分给3进程，rank0/1/2负责1–3/4–5/6–7行。各进程有局部双数组，上下各额外一行halo，保存邻进程旧层数据，物理端部为零。两次Sendrecv完成两个方向的数据交换，之后更新本地内点并换层。最终只收集负责行，拼回完整场；halo不是新增求解行。
- **Speaking focus**: 余数优先分给前面的rank，初值按全局坐标构造。发送首拥有行给上邻居并从下邻居接收；再发送末拥有行给下邻居并从上邻居接收。物理端halo自行置零。每步没有全局Barrier；开始计时前的一次全局同步和结束后的收集均在推进计时外。本实现1≤P≤N−1，请求和实际进程数分开记录。
- **Composition**: 全场分块与一个局部块的halo相互对应，两向通信箭头标明旧层来源；单步顺序沿串行流程展开。
- **Motion suggestion**: P04整层计算改为多个局部层；保留更新与换层次序，新增跨块依赖。
- **Fact IDs**: F-MPI, F-MODEL, F-REPORT。

#### Slide 06 - OpenMP行分配

- **File**: 06_openmp.svg
- **Timing**: 30秒，累计2:50。
- **Rhythm**: dense
- **Audience move**: 理解进程局部数据→能对照线程共享数组、交错行分配和两次同步。
- **Relationships**: contrast: MPI局部数组与OpenMP共享双数组；membership: static,1交错分配内部行；order: 并行更新→所有线程同步→单线程换层→所有线程同步→下一步。
- **Title**: OpenMP行分配
- **Core message**: 线程共享旧新数组，每点唯一写入，整层完成和换层后各同步一次。
- **Content**: 同一N=8网格用实际3线程示意，线程0/1/2负责{1,4,7}/{2,5}/{3,6}，明确是交错整行分配而非连续块。一个持续线程团队完成M步，旧层共同读取，新层每个内点只有一个线程写入。图上单列两处同步：全部新值写完后由一个线程交换数组；换层发布后所有线程才进入下一步。不需要halo通信。
- **Mathematical content**: \text{行}\ i\ \text{归线程}\ (i-1)\bmod Q_{\mathrm{actual}}
- **Speaking focus**: 对应schedule(static,1)、for末隐式屏障、single交换及single末隐式屏障。循环索引私有，old/next共享，N/M/步长系数为只读副本；两数组物理边界始终零。请求Q与实际Q区分；线程多于内部行合法，空闲线程仍参加同步，不套MPI进程数上限。
- **Composition**: 与P05相同网格作可比对照，行归属改为交错；共享双数组和两处同步比长代码更突出。
- **Motion suggestion**: 延续P05行编号和更新方向，改变数据归属与依赖获取方式；静态图必须独立表达差别。
- **Fact IDs**: F-OMP, F-MODEL, F-REPORT。

#### Slide 07 - 正确性检验

- **File**: 07_validation.svg
- **Timing**: 25秒，累计3:15。
- **Rhythm**: dense
- **Audience move**: 知道三种实现→看到连续误差和串并行差各自的检验结果。
- **Relationships**: contrast: 数值场对解析解与并行场对同输入串行场；order: N加倍且M四倍→误差约降至四分之一。
- **Title**: 正确性检验
- **Core message**: 两类比较分别检查数值精度与并行一致性，联合加密呈约二阶趋势。
- **Content**: 给出解析解作为测试数据构造依据；E∞比较连续解析解，D∞比较相同N/M/T/α的独立串行全场。默认T=0.1/α=1/r=0.1的三行表：20/400/1.1262×10⁻⁴，40/1600/2.8181×10⁻⁵，80/6400/7.0470×10⁻⁶；观测阶约2。已测归档组D∞=0，仍按容差检查，不能外推任意输入逐位相等。
- **Mathematical content**: u(x,y,t)=e^{-2\alpha\pi^2t}\sin(\pi x)\sin(\pi y);\quad E_\infty=\max_{i,j}|U_{ij}^{M}-u(x_i,y_j,T)|;\quad D_\infty=\max_{i,j}|U_{ij,\mathrm{parallel}}^{M}-U_{ij,\mathrm{serial}}^{M}|
- **Speaking focus**: 解析场按每个网格点同一终止时刻计算，串并行比较使用相同输入和精度要求。时间一阶、空间二阶；这里N加倍同时M四倍，是Δt随h²减小的联合二阶，不能称时间二阶。边界、奇偶步、不均分块及线程多于行均有历史验证，本轮不复跑。
- **Visualization**: refinement-errors — N、M、E∞三列三行的归档数值表；误差比3.996299/3.999078及观测阶1.998664/1.999667在备注。
- **Native-ready**: refinement-errors=yes
- **Composition**: 两个比较对象明确分开，一张三行表显示加密效果；不堆测试日志或加入已删除的第三类参考。
- **Fact IDs**: F-VALID, F-MODEL, F-REPORT。

#### Slide 08 - 固定规模性能

- **File**: 08_performance.svg
- **Timing**: 40秒，累计3:55。
- **Rhythm**: dense
- **Audience move**: 看到并行度→能用独立串行基线读出S/E及更多线程反而变慢的事实。
- **Relationships**: contrast: 同一N/M/T/α的独立串行与并行耗时；link: 并行度、加速比与效率。
- **Title**: 固定规模性能
- **Core message**: 最大网格MPI16加速3.3493倍，OpenMP8加速1.7992倍，16线程反而变慢。
- **Content**: N=1024/M=65536/T=0.01/α=1，独立Ts=35.3892s。测试并行度为1、2、4、8、16，每配置10次正式采样。MPI的S依次0.7325/1.2039/1.9107/2.6397/3.3493；OpenMP依次0.9978/1.2517/1.4358/1.7992/1.6508。突出MPI16的10.5662s与20.93%效率，OpenMP8的19.6692s与22.49%效率；OpenMP16为21.4382s、10.32%。画面保留推进计时、非独占WSL和16逻辑CPU/14可见core的简短限定。
- **Mathematical content**: S_p=\frac{\operatorname{median}(T_s)}{\operatorname{median}(T_p)},\qquad E_p=\frac{S_p}{p},\quad p=P_{\mathrm{actual}}\ \text{或}\ Q_{\mathrm{actual}}
- **Speaking focus**: 初始化完成后计M次推进，含MPI通信等待和OpenMP同步/团队进出；验证、收集和输出在外。计算S时以独立串行耗时为基线，不用MPI1或OpenMP1替代。通信与同步以及实现和环境成本使理想Amdahl曲线无法直接等同实测；不反推真实源码串行占比。硬件、编译选项及完整计时在P11；不把16逻辑CPU称16独立物理核心。
- **Visualization**: n1024-speedup — 同一归档CSV的MPI/OpenMP各5点及原不对称探索性95%区间，基线S=1；保留全部正式样本。区间不按原图几何估读。
- **Native-ready**: n1024-speedup=no
- **Composition**: 一张清楚的双系列图配两组代表耗时/S/E，避免重复放完整五行耗时表；公式和环境限定保留可读位置。若原生数据图不能表达不对称区间，使用可编辑图元保留准确几何。
- **Fact IDs**: F-LARGE, F-SERIAL, F-MPI, F-OMP, F-LAWS。

#### Slide 09 - 工作量与扩展表现

- **File**: 09_scalability.svg
- **Timing**: 30秒，累计4:25。
- **Rhythm**: dense
- **Audience move**: 只看最大网格单点→能区分跨网格加速变化与扩大工作量的吞吐收益。
- **Relationships**: contrast: 跨网格同规模基线加速比与各实现自身基准吞吐增长；contrast: 固定规模限制与扩大工作量潜力。
- **Title**: 工作量与扩展表现
- **Core message**: 扩大工作量后MPI吞吐增长，OpenMP未获增长；更细网格并不保证更高加速比。
- **Content**: 两组实验分别标注，不能拼成同一条趋势。跨网格N=384/512/768/1024同时增加M，MPI16的S为3.4885/2.8183/2.9596/3.3493，非单调。扩大工作量实验从p=1到4，W增至4.0078倍：MPI的吞吐增长R₄=2.2053、R₄/4=55.13%；OpenMP为0.8037、20.09%。表下注明R以各实现自身基础配置为参照，不是相对独立串行的S。Amdahl用于解释固定规模的加速限制；Gustafson提供扩大工作量的比较视角，实测未达恒定耗时和线性吞吐。
- **Mathematical content**: W=M(N-1)^2;\quad R_p=\frac{W_p/T_p}{W_1/T_1}
- **Speaking focus**: 跨网格组是空间与时间联合加密；扩大工作量组p=1/2/4，对应N=256/304/362、M=4096/5776/8191，每配置5次，不能与前页10次组混算。σ未单独测量，R/p不是Gustafson效率；两组均不称标准弱扩展。P13给完整网格曲线，P14给两定律和诊断边界。
- **Visualization**: scaled-throughput — MPI/OpenMP两行、吞吐增长R₄及R₄/4两指标的短表。跨网格的四个数用带N标签的短序列表达，不混入吞吐表。
- **Native-ready**: scaled-throughput=yes
- **Composition**: 上方跨网格短序列，下方扩大工作量的两行结果；每组附一句结论，模型公式放备份，保留正文分析而非只报数字。
- **Fact IDs**: F-LARGE, F-BASE, F-LAWS, F-REPORT。

#### Slide 10 - 总结与AI使用

- **File**: 10_conclusion.svg
- **Timing**: 15秒，累计4:40。
- **Rhythm**: anchor
- **Audience move**: 看完实现和结果→记住项目结论及AI参与与修正责任。
- **Relationships**: order: 三种实现→两类验证→有条件的并行收益；contrast: AI执行辅助与使用者管理审核/答辩责任。
- **Title**: 总结与AI使用
- **Core message**: 三种实现完成同一问题，并行收益有条件；AI参与和输出修正如实披露。
- **Content**: 大字结论“同一算法，结果一致；并行收益有条件”，一致性限定为已测配置。AI辅助算法/代码/测试/统计与材料；使用者负责范围选择、管理、审核与答辩。可见实例：“输出失败测试构造不当→修正重定向位置→回归通过”，不伪称由本人手工执行核查。
- **Speaking focus**: 15秒只收束结论并讲一个真实AI修正例；不再复述所有数字。补充诊断提示实现与分工影响，未确定具体硬件根因；不将变体当正式优化成果。
- **Composition**: 一条结论主句配简短AI角色及修正链，避免空白致谢页或小字合规尾注。
- **Closing impact**: 绑定“正确性有验证，并行收益依实现和环境而变”；AI实例与职责清楚，可接现场提问。
- **Fact IDs**: F-VALID, F-LARGE, F-DIAG, F-AI, F-REPORT。

### Part 2: Appendix for questions

#### Slide 11 - 备份：环境与计时

- **File**: 11_timing.svg
- **Timing**: 问答备用，不计入280秒。
- **Rhythm**: dense
- **Audience move**: 追问比较条件→能逐项对照平台、编译、并行资源和计时合同。
- **Relationships**: contrast: 三程序计时内外边界；contrast: 三批采样数量和统计对象。
- **Title**: 备份：环境与计时
- **Core message**: 正式性能以独立串行中位数为基线，所需通信同步纳入推进计时。
- **Content**: i7-14700HX、WSL2/Ubuntu24.04、GNU13.3/C++17、OpenMPI4.1.6/libgomp、Release（-O3 -DNDEBUG）；WSL可见28逻辑CPU/约7.6GiB，最大并行配置实际用14可见core的16逻辑CPU。三行计时表：串行检查/边界/内点/swap；MPI物理halo/两次通信等待/内点/swap、取本地耗时最大；OpenMP一次团队进出/查询实际Q/更新/两次同步/换层。三者初始化、验证和输出在外，MPI启动、开始屏障、归约/收集在外。
- **Speaking focus**: 基础23配置每组5次，共115正式，23预热；补充诊断215预热、2560正式调用，10对对照以配对比率中位数统计；扩大44配置各10次，共440正式、44预热。同一p用同一CPU集合，请求/实际分开。停止的扩大运行在预热终止、0正式；不进入完成数据。耗时min/max非置信区间，bootstrap仅探索性，慢样本全部保留。
- **Visualization**: timer-scope — 三种程序与计时内/外两列交叉说明；平台配置在表外说明，采样记录放备注，避免把所有统计细节压成一页小字。
- **Native-ready**: timer-scope=yes
- **Fact IDs**: F-BASE, F-DIAG, F-LARGE, F-SERIAL, F-MPI, F-OMP。

#### Slide 12 - 备份：完整固定规模结果

- **File**: 12_full_scaling.svg
- **Timing**: 问答备用，不计入280秒。
- **Rhythm**: dense
- **Audience move**: 只见最大N结果→可查看四组固定网格的所有并行度。
- **Relationships**: contrast: 每个固定N/M面板内MPI与OpenMP的加速表现。
- **Title**: 备份：完整固定规模结果
- **Core message**: 四组网格使用各自的独立串行基线，16线程不保证优于8线程。
- **Content**: 当前02-speedup原PNG完整展示，N与M标识、坐标和图例都保留；并行度1、2、4、8、16。误差线为bootstrap探索性95%区间，不能按极值解释或据微小差异断言普遍优势。
- **Speaking focus**: 16执行单元不是16独立物理核心；非独占WSL，存在样本轮次趋势，曲线不能直接识别唯一硬件机制。
- **Visualization**: full-grid-speedup — 四个固定网格面板的全部归档点及不对称区间。
- **Native-ready**: full-grid-speedup=no
- **Images**: 02-speedup.png，制作时同步当前原件的字节副本，不裁切。
- **Fact IDs**: F-LARGE。

#### Slide 13 - 备份：跨网格与工作量

- **File**: 13_grid.svg
- **Timing**: 问答备用，不计入280秒。
- **Rhythm**: dense
- **Audience move**: 混淆加密与扩大任务→能解释实际变化的N/M和累计更新量。
- **Relationships**: link: 单位物理域中N增加同时M增加；contrast: 同规模串行加速S与自身基础吞吐增长R。
- **Title**: 备份：跨网格与工作量
- **Core message**: 联合加密与扩大累计工作量要分别解释，不把它们写成弱扩展。
- **Content**: 当前05-grid-speedup原PNG完整展示。四网格N=384/512/768/1024、M=9216/16384/36864/65536，T=0.01/α=1/r=0.16。另有基础批次扩大工作量组：p=1/2/4，N=256/304/362，M=4096/5776/8191，W/W₁为1/1.991004/4.007846；这些参数在备注解释，不与四网格曲线混画。
- **Mathematical content**: W=M(N-1)^2,\quad M=N^2/16,\quad W\sim N^4/16;\quad R_p=\frac{W_p}{W_1}\frac{T_1}{T_p}
- **Speaking focus**: 扩大工作量组p=4时MPI耗时0.2788s、R=2.2053，同规模独立串行S=1.3387；OpenMP耗时0.4244s、R=0.8037，同规模S=0.8795。R和S的基线不同，不用W比例推算未测串行时间。N/M共同变化，不能将跨网格变化仅归因于每步内点数。
- **Visualization**: across-grid-speedup — 原图各固定并行度曲线及探索性区间。
- **Native-ready**: across-grid-speedup=no
- **Images**: 05-grid-speedup.png，制作时同步当前原件的字节副本，不裁切。
- **Fact IDs**: F-BASE, F-LARGE, F-LAWS。

#### Slide 14 - 备份：模型与诊断边界

- **File**: 14_interpretation.svg
- **Timing**: 问答备用，不计入280秒。
- **Rhythm**: dense
- **Audience move**: 试图用理想模型直接归因→能区分已测数据、模型假设与待确定机制。
- **Relationships**: contrast: 固定规模Amdahl与扩大工作量Gustafson；contrast: 隔离诊断支持的实现因素与未测硬件机制。
- **Title**: 备份：模型与诊断边界
- **Core message**: 定律用于限定解释，诊断变体用于分析因素，都不代替正式性能结果。
- **Content**: Amdahl的f是假设的串行时间比例，实测反算f_eff不是源码串行占比，不能据此外推无限核心上限。Gustafson的σ在本项目未单测，扩大工作量组也未保持相近并行时间，不能代入虚构参数或把R/p称模型效率。短注“诊断：内核上下文／行划分有影响；具体缓存与带宽机制未确定”。
- **Mathematical content**: S_A(p)=\frac{1}{f+(1-f)/p};\quad f_{\mathrm{eff}}=\frac{p/S_p-1}{p-1}\ (p>1);\quad S_G(p)=p-\sigma(p-1)
- **Speaking focus**: 独立诊断的MPI1共用行内核耗时配对比率中位数1.5832，OpenMP4连续块对交错行2.7626；它们不是正式S，变体未进入正式程序，缓存未命中/带宽未直接测量。44组中34组有前后三次中位数超过10%的趋势，UTC起点11处回退；单调计时保留，外部物理时间未独立校准。非独占WSL和共享硬件线程影响适用范围，不把低效率简单归因于任务太小。
- **Composition**: 两种模型及其适用条件为主体，诊断与运行限制用短句；详细数字和历史异常保留备注供问答。
- **Fact IDs**: F-LAWS, F-BASE, F-LARGE, F-DIAG。

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under `notes/`
- **Content**: 按已批准规范及最终页面更新notes/total.md、分页面备注、presentation/SPEAKER_NOTES.md和DEFENSE_QA.md。以最新报告为主稿，解释图中的输入、输出、依赖与顺序，不照读所有标签；正文不显示仓库路径/实验批次代号，完整来源与统计限定留在备注。AI实例和执行者如实说明，不补写人工核查。讲稿及14页备注已同步v5，旧版估算不挪用。
- **Total duration**: P01–P10为25/20/40/20/35/30/25/40/30/15秒，合计280秒，另留20秒机动；P11–P14不计入主讲。v5正文956个中英文/数字字符，按280字符/分钟加20秒停顿估算224.9秒；14页PPT已实际渲染。估算不冒充实讲，人工计时演练待验证；旧版248.2秒估算不挪用。
- **Notes style**: 面向课程教师的中文口语讲解，减少术语定义，突出本项目的实现和结果。
- **Presentation purpose**: 按模型、网格、差分、串行与并行实现、主要测试结果的顺序说明完成情况，并如实披露AI使用。

## Revision v3 — 2026-11-13

用户要求整体增字、减少中央留白、修复P03公式并补全五点计算流程机理。正文40px、标题44px；密集数据注释30px，导航页脚20px，公式36px。所有页重新排版而非缩放文本硬挤。历史v3的P03公式用aligned两行，显式显示旧层n的五点坐标/权重、计算写入next中心、遍历全部内点/零边界、整层完成后交换、n<M回路；并行同步细节由P04/P05展开。两幅原图保持字节，按可用宽度放大；原始数据不变。


## Revision refine-spec — 2026-11-14 (approved)

用户本轮显式要求按“懂算法/懂代码/懂验证/懂性能”细化。已在同一§IX逐页补入完整解释、来源、主讲/备份分工和时间预算；未改变已确认视觉方向、总页数、总时长或真实数值。现有SVG/PPT/讲稿未更新。旧执行锁是待同步的历史派生状态，本轮不读取其内容、不更新/使用/验证；仅在用户明确批准本规范后进入Gate 2及后续制作。


审批接续：用户2026-11-14明确“批准”，此前待审文字保留为审阅阶段语境。现允许同步执行锁及继续制作；不将规范批准误记为成品或M5验收。


### 2026-11-14 Approved execution — v4

用户聊天明确“批准”后同步锁并执行12页与讲稿；上一节批准前状态是历史。P03保留五点公式与双数组完整循环，P07增加S/E，P08/P12说明两定律边界。共含5个原生Office Math公式，总计8正文/4备份，280秒预算不变。预览另有待应用批注，尚未获明确应用指令；本轮不将其标为已处理或用户验收。实际检查记录见[REVIEW](../records/REVIEW.md)。


### 2026-11-14 Annotation revision — authorized

用户明确“一并应用批注”，26处批注归并为短标题、公式排版、标注避让和结果收束四类。正文/备份均用主题短标题；P03单行44px原生公式，普通SVG路径提供精确数学预览；P08以实现、验证和数值收益作总结。原始图表/数据、两定律的前提和资源/统计/时钟限制继续保留。前述待应用状态属于历史，处理台账见[annotation_application](validation/annotation_application.json)。交付v4-r1，不覆盖v4文件。


## Revision report-to-PPT — 2026-11-16 (pending review)

用户声明最新报告已可用于PPT，并指定模型与条件→均匀网格→显式差分→串行与并行实现→主要测试结果的顺序。本轮以同一规范增设独立网格/串行页，将固定规模与扩大工作量结果分开；提议10正文＋4备份、首页兼题名和模型，主讲仍280秒。此页数及新版逐页安排尚待用户审阅，不把旧批准视为本轮批准。此前8正文/4备份及已渲染事实均属于v4-r1历史。

沿用《单幅图像去雾-第二组》页眉、黑体/楷体、大字号、蓝白配色与无动画配音；同一N=8网格贯穿空间划分、五点与MPI/OpenMP分工。明确两类正确性参考、联合二阶及独立串行基线；更新两幅原图尺寸和来源，旧图片副本/归档报告待制作时同步。原报告、旧锁、SVG、讲稿与成品本轮不改；本稿经内容/数字/时长预算核对后进入审阅，不导出新版或宣称渲染通过。


## Revision v5 — 2026-11-16 (approved and executed)

用户回复“审阅完备”，并明确听众为无法访问项目、只接触PPT和最终报告的非实现者。按本规范完成10正文＋4备份：模型、网格、五点、串行、MPI、OpenMP、验证、固定规模、扩大工作量、总结与AI。正文与备份不含内部批次代号、仓库路径或另读实验报告的要求，备注亦直接解释条件。

已同步执行锁、页面、素材、讲稿及问答，交付v5。源门0错误/5项文本框组织建议；14页/14备注/4原生公式/298可编辑文本run，无动画。LibreOffice实际打开导出14页PDF，逐页渲染及AI审图，数值/图像字节/页界核对通过。原始数据、求解器、课程资料与用户报告字节保持；报告PDF本轮不重新生成。个人信息、PowerPoint人工显示编辑、真实实讲和M5验收仍待用户，不将规范确认视作材料验收。
