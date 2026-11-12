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
| Design Style | 按用户指定《单幅图像去雾-第二组》参考重做页眉、疏密、推进、黑体/楷体及字号字色 |
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
| Body | 32 |
| Title | 38 |
| Cover | 46 |
| Lead | 32 |
| Annotation | 24 |
| Navigation | 16 |
| Footnote | 16 |
| Data | 24 |

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: 顶部三段导航标记阶段，蓝条白字标题提出本页主题，白底正文给一个解释或证据，蓝色短句收束。
- **Composition tendency**: 图文并置或公式→变量说明→结论；简单段落/编号，减少卡片。
- **Cross-page continuity**: 问题与路线／数值与并行方法／结果与讨论三级章节导航，全页一致；导航圆点指示本节位置；上下双色页脚。
- **Spacing posture**: 主讲页每页一个主题，2–4个主要信息单元，正文32px；细节与限定放入备份/备注。
- **Spacing anchors**: page margin=56; block gap=28; column gutter=40; corner radius=0; body leading=48.

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

### Part 1: Five-minute defense and appendix

#### Slide 01 - 二维热传导方程：显式有限差分并行求解

- **Audience move**: 不了解题目→知道题目与独立串行/MPI/OpenMP范围
- **Relationships**: membership: 三实现属于同一问题
- **Title**: 二维热传导方程：显式有限差分并行求解
- **Core message**: 同一模型的三种实现
- **Content**: 蓝色居中标题块，白底封面；课程期末汇报；姓名学号待填写；2026年11月；不引用他人身份或校徽
- **Cover impact**: 完整技术题名与三实现范围，使用参考PDF的蓝色居中标题块。

#### Slide 02 - 研究问题与汇报路线

- **Audience move**: 不知道比较对象→明白要在相同条件下比较什么
- **Relationships**: order: 基线→并行实现→验证与测试
- **Title**: 研究问题与汇报路线
- **Core message**: 相同模型和精度下，并行能带来多少收益
- **Content**: 单位正方形/零边界/正弦初值；三步：建立数值基线、实现两种并行、验证正确性与性能；模型图仅为结构示意

#### Slide 03 - 五点显式格式与双缓冲

- **Audience move**: 知道问题→理解旧层依赖与稳定性
- **Relationships**: link: 中心与四邻居；order: 读旧层→写新层→交换
- **Title**: 五点显式格式与双缓冲
- **Core message**: 整层只读旧层，完成后交换缓冲
- **Content**: 向前Euler与中心差分；h=1/N、dt=T/M；五点格式；r=αdt/h²≤1/4；时间一阶/空间二阶；真实推进M步
- **Mathematical content**: U_{ij}^{n+1}=(1-4r)U_{ij}^{n}+r(U_{i-1,j}^{n}+U_{i+1,j}^{n}+U_{i,j-1}^{n}+U_{i,j+1}^{n})

#### Slide 04 - MPI：行分块与边界交换

- **Audience move**: 知道差分→理解rank拥有行和halo
- **Relationships**: membership: 行归属rank；link: 邻rank交换；order: 通信→更新→交换
- **Title**: MPI：行分块与边界交换
- **Core message**: 先交换旧层halo，再更新拥有行
- **Content**: N8/P3分3/2/2行，全局1–3/4–5/6–7；两次Sendrecv；每rank两个halo；端部清零；P≤N−1是本实现约束；实际P来自通信器

#### Slide 05 - OpenMP：行划分与层间同步

- **Audience move**: 理解MPI→理解共享双缓冲和线程屏障
- **Relationships**: membership: 行归属线程；order: 更新→屏障→交换→屏障
- **Title**: OpenMP：行划分与层间同步
- **Core message**: 一个持续团队，先完成整层再交换
- **Content**: static,1循环分整行；N7/Q4行{1,5}/{2,6}/{3}/{4}；old/next共享、循环变量私有；for屏障→single交换→single屏障；请求/实际Q分开，Q>内部行合法

#### Slide 06 - 正确性检验与网格加密

- **Audience move**: 知道实现→理解连续精度与并行一致性分别验证
- **Relationships**: contrast: 连续精度与并行一致性；order: 网格加密
- **Title**: 正确性检验与网格加密
- **Core message**: E∞与D∞分别检查，联合加密误差约缩小四倍
- **Content**: N20/M400/E1.1262e-4，N40/M1600/E2.8181e-5，N80/M6400/E7.0470e-6；T0.1/alpha1/r0.1；dt∝h²为联合二阶，非时间二阶；离散模态及并行边界在备注展开

#### Slide 07 - 性能测试：固定规模强扩展

- **Audience move**: 知道正确→理解真实性能与计时基线
- **Relationships**: contrast: 同规模独立串行与并行；order: 增加P/Q
- **Title**: 性能测试：固定规模强扩展
- **Core message**: MPI有收益，更多线程不保证更快
- **Content**: N1024/M65536/T0.01/alpha1；同网格独立串行中位数35.39s；MPI16 10.57s/S3.35；OpenMP8 19.67s/S1.80，16为21.44s；原10点/10条区间；16逻辑CPU覆盖14WSLcore含兄弟线程；计时/统计口径写入备注和备份
- **Visualization**: n1024-speedup — 10个点及不对称探索性区间；原统计不变。
- **Native-ready**: n1024-speedup=no
- **Composition**: 数值坐标图保留不对称区间；payload不支持该区间组合，保留可编辑图元。

#### Slide 08 - 结论、局限与AI使用

- **Audience move**: 看到结果→理解可支持结论和本人责任
- **Relationships**: contrast: 支持结论与评价边界
- **Title**: 结论、局限与AI使用
- **Core message**: 正确性有证据，并行收益有条件
- **Content**: 数值检验通过；MPI收益不随N单调、OpenMP16未必优于8；非独占WSL/轮次趋势/时钟限制；Codex辅助实现与分析，本人负责范围审核答辩；解析/串行/日志/重算核查及修正实例放备注
- **Closing impact**: 用数值正确、有限收益与AI核查责任收束，结尾“恳请批评指正”。

#### Slide 09 - 备份：计时边界与统计口径

- **Audience move**: 需要追问→能区分计时与统计对象
- **Relationships**: contrast: 计时合同与三批统计
- **Title**: 备份：计时边界与统计口径
- **Core message**: 三个计时合同可比，但三批统计不可混算
- **Content**: 串行step检查/边界/更新/交换；MPI含halo等待取rank本地最大，归约收集在外；OpenMP含团队进出和层间同步；原M4 23/115；诊断215预热/2560正式；02-r1 44预热/440正式；停止02 0正式；范围与探索性bootstrap分开

#### Slide 10 - 备份：完整强扩展结果

- **Audience move**: 需要完整矩阵→看到四组固定N/M
- **Relationships**: contrast: 四组固定问题强扩展
- **Title**: 备份：完整强扩展结果
- **Core message**: 完整原图不裁切
- **Content**: 02-speedup原PNG；各点各自串行基线；MPI16 S3.4885/2.8183/2.9596/3.3493非单调；16硬件线程共享限制；图保留原色
- **Images**: 02-speedup.png，保留完整坐标与脚注，不裁切。

#### Slide 11 - 备份：扩大工作量与可扩展性

- **Audience move**: 需要扩展讨论→区分联合加密与弱扩展
- **Relationships**: link: N增加同时M增加；contrast: 跨网格比较
- **Title**: 备份：扩大工作量与可扩展性
- **Core message**: 固定区域跨N同时增加M，不称弱扩展
- **Content**: 05-grid-speedup原图；M=N²/16，W=M(N−1)²约N⁴；MPI非单调与OpenMP16不保证优于8；不单独分离粒度
- **Images**: 05-grid-speedup.png，保留完整坐标与脚注，不裁切。

#### Slide 12 - 备份：模型与机制的适用边界

- **Audience move**: 追问根因→能区分证据/假设
- **Relationships**: contrast: 模型与实测；contrast: 支持与未确定
- **Title**: 备份：模型与机制的适用边界
- **Core message**: 理想定律不替代测量，实施因素不等于唯一硬件根因
- **Content**: Amdahl不反推代码f；Gustafson相近时间前提未满足且sigma未测；34/44配置趋势/11处UTC回退；用单调时钟但未外部物理校准；诊断支持上下文/行划分，变体保持隔离

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under `notes/`
- **Content**: 基于最终SVG，前8页按新路线重写讲稿并校准图示，备份页给出答辩解释；来源路径集中保留于报告引用及核查记录，页脚仅课程与题名，未发生的人工核查不补写。
- **Total duration**: 正文280秒预算＋20秒机动；备份不纳入5分钟；字数估算不是人工实讲。
- **Notes style**: 中文口语化解释。
- **Presentation purpose**: 解释算法/实现/验证与真实收益及限制，披露AI使用与修正。
