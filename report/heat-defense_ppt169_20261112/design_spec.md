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
| Communication Intent | 以“懂算法→懂代码→懂验证→懂性能”解释完成情况：从五点依赖与稳定性进入划分/通信同步，再以两类误差和真实性能作证，披露AI及核查 |
| Desired Audience Outcome | 教师能沿图和证据追问：为什么必须分开新旧层、halo/屏障为何在该位置、E∞和D∞各检验什么、加速比/效率如何计算，以及Amdahl/Gustafson哪些前提未被实验满足；这是讲述目标，不预先宣称使用者已掌握 |
| Core Message / Ask / Action | 正确性有证据，并行收益有条件 |
| Delivery Context | 本人现场主讲；8页正文280秒，20秒机动；4页备份用于提问 |
| Artifact Afterlife | 备注、来源与生成源支持会后审阅和复核 |
| Reading Mode | presentation |
| Content Strategy | 内容为讲述精简重组，数字与结论保留原证据口径 |
| Design Style | 按用户指定《单幅图像去雾-第二组》参考重做页眉、疏密、推进、黑体/楷体及字号字色 |
| AI Image Acquisition Path | not applicable |
| Generation Mode | continuous |
| Spec Refinement | enabled — 2026-11-14用户显式调用refine-spec；本文件待审，尚未冻结新版执行计划 |
| Speaker Notes | enabled — explicit user confirmation |
| Custom Animations | disabled — explicit user confirmation, all-motion scope |
| Narration Audio | disabled — explicit user confirmation |
| Created Date | 2026-11-12 |
| Revised Date | 2026-11-14 |
| Review Status | Gate 1自查完成，等待用户审阅/确认；现有PPT v3和SVG仅代表此前交付，旧spec_lock不参与本轮审阅，批准后才同步 |

### Evidence Ledger

本轮只读复核教师任务书第1、3页文字，与SPEC模型及5分钟/AI说明要求一致。以下为页内Fact IDs的本地依据；数据均为归档事实，不新增实验或假设样本。

| Fact ID | 依据 | 用途 |
| --- | --- | --- |
| F-COURSE | 本地只读`docs/sources/final.pdf`第1、3页；[SPEC](../../SPEC.md) | 教师要求、模型、稳定性、性能方法与AI披露 |
| F-MODEL | [DESIGN第1节](../../docs/DESIGN.md) | 网格/时间、格式、稳定性与双数组 |
| F-SERIAL | [heat.cpp](../../src/heat.cpp) | 独立串行、边界、step/swap、计时 |
| F-MPI | [heat_mpi.cpp](../../src/heat_mpi.cpp) | 连续行分块、两次Sendrecv、halo、MPI计时 |
| F-OMP | [heat_openmp.cpp](../../src/heat_openmp.cpp) | static,1、共享/私有、两道屏障、请求/实际Q |
| F-VALID | [M3误差CSV](../../results/validation/m3-errors.csv)、[报告第4节](../FINAL_REPORT.md) | E∞/D∞、默认网格加密、容差与离散模态 |
| F-BASE | [原M4协议](../../results/performance/baseline/README.md)、[统一结果](../../results/RESULTS.md) | 原23配置/115正式、扩大工作量与独立基线 |
| F-DIAG | [统一结果的诊断01](../../results/RESULTS.md#补充诊断运行01)、[报告第6.4节](../FINAL_REPORT.md) | 215预热/2560正式调用、隔离变体与支持程度 |
| F-LARGE | [02-r1统计CSV](../../results/performance/large-02-r1/m4-diagnostic-02-r1.csv)、[统一结果](../../results/RESULTS.md) | 44配置/44预热/440正式、时间/S/E、资源和趋势 |
| F-LAWS | [报告第6.3节](../FINAL_REPORT.md)、[答辩问答](../DEFENSE_QA.md) | 两个定律的定义、推断边界与非弱扩展解释 |
| F-AI | [AI使用记录](../../docs/AI_USAGE.md) | 实际辅助环节、失败修正与用户角色，未发生的人工核查不补写 |
| F-FIG | [五点机理图说明](../paperbanana/stencil-sol-v1/README.md) | 已有原生SVG图源及完整时间循环，供重排参考 |

### Four Understanding Requirements

- **懂算法**：不止读出公式，要解释五点依赖为什么都来自n层、双数组为何防止本步污染、交换后哪份是最终层；通过二维权重说明r≤1/4，而不是沿用一维1/2。
- **懂代码**：能沿“归属→拿到依赖→更新→换层”解释MPI；沿“循环分行→唯一写者→for屏障→single换层→single屏障”解释OpenMP，并区分请求值与实际值。
- **懂验证**：连续误差E∞与实现差D∞是两种问题；加密同时调整M，观测约二阶属于Δt∝h²的联合加密，不把并行一致或一次正常退出当作精度证明。
- **懂性能**：独立串行为主基线，推进所需操作都计时；明确S和E及实际P/Q，能用两个理想模型讨论前提和限制；跨N/M的现有实验不称为弱扩展。

这四项约束§IX及讲述内容。未要求增加实验、求解器优化或改变已确认视觉风格；本轮只细化同一规范。用户审阅前不更新/使用/验证执行锁，不制作新页面或导出新版PPT。

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

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 02-speedup.png | 2080 × 1440 | 13:9 | 完整四组强扩展 | Chart | 全幅保留所有面板与脚注，旁列读取说明 | no-crop | user | Existing | results/figures/large-02-r1-viz-01/02-speedup.png | embedded | local |
| 05-grid-speedup.png | 2560 × 1600 | 8:5 | 固定人数跨网格比较 | Chart | 全幅保留坐标与区间，在侧边给出非单调提醒 | no-crop | user | Existing | results/figures/large-02-r1-viz-01/05-grid-speedup.png | embedded | local |

### Existing Vector References

已有[五点读写宽图](../paperbanana/stencil-sol-v1/mechanism-wide.svg)与[时间循环宽图](../paperbanana/stencil-sol-v1/time-loop-wide.svg)作为P03的科学内容/构图依据，原图及核查见F-FIG。它们是本地既有SVG，不发起模型或网络图像生成；批准后再处理页面中的原生重排/资源归档。

完整总览不直接缩成小图；P03保留五点权重、旧新层与换层逻辑，必要说明用可编辑文字；全循环图在答辩备注及已交独立图中可追溯。不能把两张完整宽图和长公式同时堆在一个内容区，也不能为放下内容缩小到难读字号。两幅备份性能PNG继续完整显示，不裁掉坐标/区间/脚注。

## IX. Content Outline

### Part 1: Four understanding goals in a five-minute defense

正文仅P01–P08，讲述预算见每页Timing；P09–P12用于提问。优先沿图解释，再给证据与结论。保持8页正文/4页备份，280秒预算加20秒机动；时长为计划，不冒充真实演练。

每页Content规定画面要传达的完整科学信息，可按构图重述；Speaking focus用于口述、备注和现场追问，不能把全部解释复制为小字。主讲优先核心因果与证据，逐项细节由备注/备份承接；执行发现无法在既定字号/时长内清楚表达时，应回到本规范调整，而非静默删除限定或缩字。

#### Slide 01 - 二维热传导方程：显式有限差分并行求解

- **File**: 01_cover.svg
- **Timing**: 15秒，累计0:15。
- **Audience move**: 不了解题目→知道问题和三种实现范围。
- **Relationships**: membership: 独立串行、MPI、OpenMP属于同一基准问题。
- **Title**: 二维热传导方程：显式有限差分并行求解
- **Core message**: 用同一数学模型比较三种数值实现，回答“算得对吗，并行收益有多大”。
- **Content**: 技术题名、课程期末汇报、独立串行/MPI/OpenMP；姓名学号待填写，2026年11月。蓝色标题块延续参考风格，不引用其他项目身份。
- **Speaking focus**: 以“算法→实现→验证→性能”说明本次路线；此处不堆性能数字。
- **Cover impact**: 完整题名与三实现明确，现场从实际求解的问题进入。
- **Fact IDs**: F-COURSE, F-AI。

#### Slide 02 - 同一模型、同一终点，建立公平比较

- **File**: 02_route.svg
- **Timing**: 20秒，累计0:35。
- **Audience move**: 只知程序名称→知道网格/步数和比较条件。
- **Relationships**: membership: 三程序共享模型与输入；order: 数值基线→并行实现→两层验证→计时比较。
- **Title**: 同一模型、同一终点，建立公平比较
- **Core message**: N是每方向区间数，M是推进步数；三程序在相同输入和精度条件下比较。
- **Content**: 单位正方形、四边零温、初值sin(πx)sin(πy)；h=1/N，Δt=T/M，节点共(N+1)²；同一N/M/T/α下完成到T。独立串行基线与两种并行数值程序均真实推进，不以解析公式替代计算。
- **Speaking focus**: N、M与P/Q不是同一数量；验证组与性能组可有不同参数，但同一比较组输入必须一致。
- **Composition**: 单幅域/网格示意配简短参数定义和路线，避免再用一页目录占满讲述。
- **Fact IDs**: F-COURSE, F-MODEL, F-SERIAL。

#### Slide 03 - 五点依赖、双数组与稳定推进

- **File**: 03_stencil.svg
- **Timing**: 45秒，累计1:20。
- **Audience move**: 知道离散参数→能解释每步从哪里读、向哪里写、为何不能原地更新。
- **Relationships**: link: 同一旧层中心/四邻居加权到新层同坐标；order: 初始化→全部内点更新→整层完成→交换+n增量→判断继续或取最终层。
- **Title**: 五点依赖、双数组与稳定推进
- **Core message**: 五个输入都来自n层，写入独立n+1层；完整一层后才交换。
- **Content**: 中心系数1−4r、四邻居各r，无对角点。old只读、next写入；四条物理边界保持零。初始化old=U⁰、next=0、n=0，整层后swap并n增1，n<M则继续；n=M从old取Uᴹ。r=αΔt/h²≤1/4；时间一阶、空间二阶。
- **Mathematical content**: U_{ij}^{n+1}=(1-4r)U_{ij}^{n}+r(U_{i-1,j}^{n}+U_{i+1,j}^{n}+U_{i,j-1}^{n}+U_{i,j+1}^{n})
- **Speaking focus**: 向前Euler加空间中心差分给出五点式；r≤1/4使系数非负且权重和为1，支持标准二维稳定性论证。程序严格校验此充分稳定条件，不能从短算例未发散而放宽。分开新旧层是为避免同一步读到新邻值；交换是角色切换，恰好M步到T，不按浮点时钟累加停止。
- **Composition**: 以F-FIG读写机理为主，原生重排保留清晰标注；完整公式可分行，控制逻辑用简洁流程表达。正文必须能讲清，完整循环图供备注/问答，不把多个完整图挤成缩略图。
- **Fact IDs**: F-COURSE, F-MODEL, F-SERIAL, F-FIG。

#### Slide 04 - MPI：连续行分块，先交换halo再计算

- **File**: 04_mpi.svg
- **Timing**: 35秒，累计1:55。
- **Audience move**: 知道五点依赖→能说明rank拥有行和为何要额外halo。
- **Relationships**: membership: 拥有行属于rank，halo只是邻居旧层副本；link: 两次Sendrecv取得跨块依赖；order: 端部清零→通信→本地更新→换层。
- **Title**: MPI：连续行分块，先交换halo再计算
- **Core message**: 通信对象是旧层边界行，halo不改变全局归属。
- **Content**: N=8/P=3的7条内部行分成3/2/2，rank0/1/2拥有全局1–3/4–5/6–7。每rank双缓冲，上下各一条halo。两次Sendrecv完成旧层边界获取后，更新本rank内点再swap。请求P与MPI_Comm_size实际P分别记录；本实现P≤N−1以保证每rank至少一行。
- **Speaking focus**: 余数分给前面的rank，初值使用全局坐标。第一次首拥有行发向up、从down收到下halo；第二次尾拥有行发向down、从up收到上halo。MPI_PROC_NULL接收不会自动清零；物理端部须自行清零。基线无通信计算重叠、无每步全局Barrier；Gatherv在推进结束后收集拥有行，halo不参加。错误路径需所有rank一致退出，不能让单rank返回后留下邻居等待。
- **Composition**: 用拥有行/halo示意及两向箭头解释依赖，旁边仅列通信→更新→换层；P限制标成实现约束，不写成MPI通用定理。
- **Fact IDs**: F-MPI, F-MODEL。

#### Slide 05 - OpenMP：循环分行，两次同步保护换层

- **File**: 05_openmp.svg
- **Timing**: 35秒，累计2:30。
- **Audience move**: 理解MPI独立内存→能解释共享缓冲中的唯一写者和同步先后。
- **Relationships**: membership: static,1为线程分配整行；order: for更新→for末屏障→single交换→single末屏障→下一层。
- **Title**: OpenMP：循环分行，两次同步保护换层
- **Core message**: 每点只有一个写者；写完并发布新缓冲角色后才能进入下一步。
- **Content**: 一个持续parallel团队完成M步，schedule(static,1)按整行循环分配；N=7、实际Q=4时，线程0/1/2/3对应{1,5}/{2,6}/{3}/{4}。old/next共享，循环变量私有；for屏障完成整层写入，single完成交换，single屏障发布新角色。
- **Speaking focus**: 实际Q=A时，行i归线程(i−1)%A，而不是MPI那样连续分块。N/M/w/r为firstprivate只读副本；边界在两数组初始化为零后不再写。不能删去任一必要屏障，也不能各线程独立swap。请求Q与omp_get_num_threads实际Q分开，Q大于内部行数合法，空闲线程仍同步；不把MPI的P限制套给Q。团队进入/退出不等于每步新建OS线程。
- **Composition**: 上部显示线程拥有行，下部用更新/两道屏障/single的顺序示意，不用长代码截图替代解释。
- **Fact IDs**: F-OMP。

#### Slide 06 - 正确性：连续精度与并行一致性分开验证

- **File**: 06_validation.svg
- **Timing**: 35秒，累计3:05。
- **Audience move**: 知道程序能运行→知道两类误差各自能证明什么。
- **Relationships**: contrast: 连续解析误差与串并行差；order: 固定T/α/r下联合加密→观察误差比。
- **Title**: 正确性：连续精度与并行一致性分开验证
- **Core message**: D∞小不能代替E∞检验；误差约缩小四倍来自联合加密。
- **Content**: E∞与连续解析解比较，D∞与相同输入独立串行全场比较。默认归档组T=0.1/α=1/r=0.1：N/M=20/400、40/1600、80/6400，E∞约1.1262e−4、2.8181e−5、7.0470e−6；误差比3.996299/3.999078，观测阶约2。N加倍、M四倍，Δt∝h²，不能称时间二阶。
- **Mathematical content**: E_\infty=\max_{i,j}|U_{ij}^{M}-u(x_i,y_j,T)|; D_\infty=\max_{i,j}|U_{ij,\mathrm{parallel}}^{M}-U_{ij,\mathrm{serial}}^{M}|; u(x,y,t)=e^{-2\alpha\pi^2t}\sin(\pi x)\sin(\pi y)
- **Speaking focus**: 两种程序可能共同犯错，所以串并行一致不能证明连续精度。默认Debug归档所检MPI/OpenMP行D∞观测为0，仅限已测输入，不能外推任意规模逐位一致。小规模比较容差1e−13，正式大规模验证1e−12；离散模态再检查实际终层。边界、奇偶步、不均分块及线程多于行等属于历史测试证据，本轮未复测求解器。
- **Composition**: 两个清楚的比较对象配三行数据，用加密箭头串联；不放满测试日志，也不把不同批次/参数的误差合并。
- **Fact IDs**: F-VALID, F-MODEL。

#### Slide 07 - 固定规模性能：独立串行基线、加速比与效率

- **File**: 07_performance.svg
- **Timing**: 55秒，累计4:00。
- **Audience move**: 看到时间曲线→能解释S/E的分母、计时边界与实际资源。
- **Relationships**: contrast: 同网格独立串行与并行耗时；order: 固定问题改变实际P/Q。
- **Title**: 固定规模性能：独立串行基线、加速比与效率
- **Core message**: MPI在该规模有收益，但效率远低于理想；OpenMP更多线程不保证更快。
- **Content**: 02-r1固定N=1024/M=65536/T=0.01/α=1/r=0.16；Ts为同网格独立串行的中位数，35.39s。MPI实际16进程10.57s，S=3.3493、E=20.93%；OpenMP实际8线程19.67s，S=1.7992、E=22.49%，16线程21.44s，S=1.6508、E=10.32%。保留原10个点及探索性区间。
- **Mathematical content**: S_k=\frac{\operatorname{median}(T_s)}{\operatorname{median}(T_k)},\qquad E_k=\frac{S_k}{k};\quad k=P_{\mathrm{actual}}\ \mathrm{or}\ Q_{\mathrm{actual}}
- **Speaking focus**: MPI1和OpenMP1都不替代独立串行基线，避免把各自额外开销藏入分母。计时含推进所需操作：MPI含halo通信与等待，取各rank本地耗时最大；OpenMP含一次团队进入/退出、逐层屏障与swap；初始化、收集、验证、输出在外。每组10个正式样本，预热排除。效率是S/实际执行单元数，不是CPU利用率；16执行单元是14个WSL可见core上的16逻辑CPU，含兄弟线程。区间是探索性bootstrap，min/max不是置信区间。
- **Visualization**: n1024-speedup — 同一CSV的10点与不对称探索性区间；坐标/数值不因排版美化而变。
- **Native-ready**: n1024-speedup=no
- **Composition**: 一幅清晰主图配Ts和三个代表行的S/E短表，计时边界用简短说明；完整计时合同/统计口径留P09，不把四组完整曲线全塞正文。
- **Fact IDs**: F-LARGE, F-SERIAL, F-MPI, F-OMP。

#### Slide 08 - 两个定律解释什么，结论应止于哪里

- **File**: 08_conclusion.svg
- **Timing**: 40秒，累计4:40。
- **Audience move**: 知道有加速→知道理想模型的前提与实测结论边界。
- **Relationships**: contrast: 固定工作量的Amdahl与扩大工作量的Gustafson；contrast: 已支持的结论与不能外推的机制。
- **Title**: 两个定律解释什么，结论应止于哪里
- **Core message**: 正确性有证据，并行收益有条件；扩大网格并不自动验证Gustafson或构成弱扩展。
- **Content**: Amdahl用于固定工作量：理想加速受固定串行部分限制，通信/同步/实现与环境成本使实测S偏离理想，不能从S反推源码真实串行比例。Gustafson讨论扩大可并行工作、相近并行时间下的扩展潜力；本实验时间未维持相近，σ未单测，故只讨论前提与吞吐。固定物理域、N增大时M也增加，现有跨规模实验不称弱扩展。MPI收益不随N单调，OpenMP16不保证优于8。末尾保留AI使用与本人责任说明。
- **Speaking focus**: 不把效率低简单归因为“任务太小”，也不由曲线唯一断言缓存/带宽/WSL宿主根因。保留非独占WSL、轮次趋势、UTC回退及外部物理时间未校准限制。AI披露：Codex辅助实现/实验分析/材料，使用者负责范围管理、审核和答辩；用解析解、独立串行全场、日志和统计重算核查。给出真实修正例：启动器重定向曾误当rank输出失败测试，后改rank内验证并回归，不编造个人测试经历。
- **Composition**: 两个定律各用一条“前提→本实验能说到哪里”的短句；结论/AI用简短收束，完整公式和问答留P12。
- **Closing impact**: 用可支持的完成情况、有限收益、AI核查责任收束，保留“恳请批评指正”。
- **Fact IDs**: F-LAWS, F-LARGE, F-BASE, F-DIAG, F-AI。

### Part 2: Appendix for questions

#### Slide 09 - 备份：计时合同、基线与三批统计

- **File**: 09_timing.svg
- **Timing**: 问答备用，不计入280秒。
- **Audience move**: 追问是否公平→可逐项对照范围和统计对象。
- **Relationships**: contrast: 三程序计时合同；contrast: 三批统计对象及停止02。
- **Title**: 备份：计时合同、基线与三批统计
- **Core message**: 正式S是中位数之比，诊断配对比率不能混算；时间范围不是置信区间。
- **Content**: 串行M次step内检查/边界清零/更新/swap计入；MPI物理halo清零、两次Sendrecv/等待、本地更新/swap计入，各rank本地差的最大值为样本；OpenMP一次团队进出、实际Q查询、更新/屏障/single交换计入。三者初始化/验证/输出在外；MPI生命周期、广播、开始Barrier、Reduce/Gatherv在外。原M4为23配置/115正式（各5次）；诊断01为215预热/2560正式调用，对照用配对耗时比率中位数；02-r1为44配置/44预热/440正式（各10次），同网格中位数之比及同轮共同bootstrap。停止02在预热阶段终止、0正式，保留但不混入完成统计。
- **Speaking focus**: 三种实现保留其必要管理开销，loop_seconds不是端到端时间或纯算术时间。MPI不是用不同rank绝对时钟相减，最大值归约本身在计时外；OpenMP进入/退出不等于OS线程每次重建。原M4/诊断/02-r1三种统计口径分开，全部慢样本保留，bootstrap仅探索性。
- **Fact IDs**: F-BASE, F-DIAG, F-LARGE, F-SERIAL, F-MPI, F-OMP。

#### Slide 10 - 备份：四组固定问题的强扩展

- **File**: 10_full_scaling.svg
- **Timing**: 问答备用，不计入280秒。
- **Audience move**: 质疑只展示最大N→能看到完整矩阵与非单调事实。
- **Relationships**: contrast: 各自固定N/M/T/α的四组强扩展曲线。
- **Title**: 备份：四组固定问题的强扩展
- **Core message**: 每个面板内固定工作量改变P/Q，各点用同网格独立串行基线。
- **Content**: 完整02-speedup原PNG，不裁切坐标/区间/脚注。MPI16在N=384/512/768/1024的S为3.4885/2.8183/2.9596/3.3493，并非随N单调增加；OpenMP16也不保证优于8。16逻辑CPU/14WSL可见core的资源限定不可省略。
- **Speaking focus**: 图上误差线的统计定义见P09；不能从相邻曲线差直接判定唯一硬件机制或以新增采样补美观。
- **Images**: 02-speedup.png，已有归档PNG字节不变。
- **Fact IDs**: F-LARGE。

#### Slide 11 - 备份：扩大工作量是联合加密，不是弱扩展

- **File**: 11_grid.svg
- **Timing**: 问答备用，不计入280秒。
- **Audience move**: 将跨规模图误认弱扩展→能写出实际累计工作量及时间前提。
- **Relationships**: link: 固定物理域下N增加同时M增加；contrast: 固定规模强扩展、扩大工作量与理想弱扩展。
- **Title**: 备份：扩大工作量是联合加密，不是弱扩展
- **Core message**: W=M(N−1)²；本矩阵M随N²增加，所以W约N⁴，不能只按每worker节点数命名。
- **Content**: 完整05-grid-speedup原PNG；02-r1固定T=0.01/α=1/r=0.16，M=N²/16，物理域仍为单位正方形。跨N比较时N与M共同改变，工作量W=M(N−1)²约随N⁴增长；这不是当前范围内的弱扩展实证。
- **Mathematical content**: W=M(N-1)^2,\qquad M=\frac{N^2}{16},\qquad W\sim\frac{N^4}{16}
- **Speaking focus**: 原M4另有随p=1/2/4扩大累计W的矩阵，W/W1为1/1.991004/4.007846；这说明它试图令W约随p增大，但并行时间没有保持相近、σ未分离测量。不能因W/p近似恒定就省略N/M/粒度变化，也不能将此与02-r1统计混合。只讨论Gustafson适用前提和实测吞吐，不能宣称验证线性扩展。
- **Images**: 05-grid-speedup.png，已有归档PNG字节不变。
- **Fact IDs**: F-BASE, F-LARGE, F-LAWS。

#### Slide 12 - 备份：Amdahl、Gustafson与解释边界

- **File**: 12_interpretation.svg
- **Timing**: 问答备用，不计入280秒。
- **Audience move**: 要求从实测归因→能写出模型且区分模型参数与实测证据。
- **Relationships**: contrast: 两种理想模型的固定/扩大工作量前提；contrast: 已支持因素与未确定硬件机制。
- **Title**: 备份：Amdahl、Gustafson与解释边界
- **Core message**: 用定律约束解释，不用定律制造未测的串行比例或理想加速结论。
- **Content**: Amdahl的f指固定问题的理想串行比例，f>0时理想极限为1/f；这是模型含义，不是本项目测得的上限。从实测S得到的有效f包含通信/同步、实现差异与环境成本，可能不恒定或超出比例范围，不等同源码占比，不能据此外推无限核心上限。Gustafson的σ为扩展问题并行执行时间中的串行部分比例，本项目未单独测量；并行时间未保持相近，不能代入虚构σ证明线性。诊断01支持计算执行上下文与行划分影响，变体没有进入正式求解器；不能唯一确认缓存/带宽/宿主根因。
- **Mathematical content**: S_A(k)=\frac{1}{f+(1-f)/k};\quad f_{\mathrm{eff}}=\frac{k/S-1}{k-1}\ (k>1);\quad S_G(k)=k-\sigma(k-1)
- **Speaking focus**: 02-r1有34/44配置出现描述性轮次趋势、11处相邻UTC起点回退；保留原时戳及慢样本。实际以各程序本地单调时钟差解释结果，但未独立校准外部物理时间；不能把UTC异常归给已确认的特定宿主机制。正式数据只来自三个原程序，隔离诊断不作为优化后正式性能。
- **Composition**: 上部模型定义与适用前提，下部证据/推断边界，避免把理论曲线与实测点混作拟合结果。
- **Fact IDs**: F-LAWS, F-BASE, F-LARGE, F-DIAG。

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under `notes/`
- **Content**: 本轮仅规划，批准后基于最终SVG修订讲稿；逐页与§IX的科学内容、事实限定和Timing一致，备份给出源码/统计解释。保留AI核查真实实例，来源集中保留在备注/报告；不将未发生的人工测试或用户审核写成已完成。现有SPEAKER_NOTES仍对应v3，尚未被本规范替换。
- **Total duration**: P01–P08预算15/20/45/35/35/35/55/40秒，总计280秒，另留20秒机动；P09–P12不计入5分钟。批准后重新统计字数并实际检查讲述时长，预算/估算不冒充人工实讲。
- **Notes style**: 中文口语化解释。
- **Presentation purpose**: 解释算法/实现/验证与真实收益及限制，披露AI使用与修正。

## Revision v3 — 2026-11-13

用户要求整体增字、减少中央留白、修复P03公式并补全五点计算流程机理。正文40px、标题44px；密集数据注释30px，导航页脚20px，公式36px。所有页重新排版而非缩放文本硬挤。P03公式用aligned两行，显式显示旧层n的五点坐标/权重、计算写入next中心、遍历全部内点/零边界、整层完成后交换、n<M回路；并行同步细节由P04/P05展开。两幅原图保持字节，按可用宽度放大；原始数据不变。


## Revision refine-spec — 2026-11-14 (pending review)

用户本轮显式要求按“懂算法/懂代码/懂验证/懂性能”细化。已在同一§IX逐页补入完整解释、来源、主讲/备份分工和时间预算；未改变已确认视觉方向、总页数、总时长或真实数值。现有SVG/PPT/讲稿未更新。旧执行锁是待同步的历史派生状态，本轮不读取其内容、不更新/使用/验证；仅在用户明确批准本规范后进入Gate 2及后续制作。
