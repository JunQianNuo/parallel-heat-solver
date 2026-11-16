# 书面报告与答辩材料

当前PPT局部修订（2026-11-16）：[最新PPTX](presentation/current/presentation-v5-wps-r1.pptx)、[PDF](presentation/current/presentation-v5-wps-r1.pdf)、[P09/P10预览](presentation/current/presentation-v5-wps-r1-p09-p10.png)。以用户15页手改稿为输入，只改两页及备注：P09加入MPI16/OpenMP16曲线，P10给出吞吐定义、三配置表及结论，其余13页XML与备注字节保持。详见[修订说明](presentation/revisions/p9-p10-20261116/README.md)；原稿页码、其他页既有问题及旧全稿讲述时间未作全局整理，报告未改。

以下为前序工作记录。

当前PPT（2026-11-16）：以用户手改文件为输入，通过Windows MCP在WPS中统一公式，交付[WPS修订PPTX](presentation/current/presentation-v5-wps.pptx)、[WPS导出PDF](presentation/current/presentation-v5-wps.pdf)和[总览](presentation/current/presentation-v5-wps-contact.png)。14页含12个原生公式；第9页网格标注已按确认修正。用户输入文件原字节保留，第10页空白正文未改。旧SVG/讲稿及旧v5检查不代表当前人工修订内容同步，后续从WPS修订PPTX编辑，详见[PPT入口](presentation/README.md)。

以下保留此前任务记录。

当前工作（2026-11-16）：用户已确认PPT新规范及“面向非实现者、只接触PPT和最终报告”的要求。已完成[新版v5 PPTX](presentation/current/presentation-v5.pptx)、[14页PDF](presentation/current/presentation-v5.pdf)及[渲染总览](presentation/current/presentation-v5-contact.png)：10页正文＋4备份、280秒预算。讲稿、问答和核查入口已同步；实际LibreOffice打开并检查全部页，用户验收和人工实讲待完成。

书面报告以最新保存的FINAL_REPORT.md为准；本轮保持报告源稿及现有PDF原字节，PDF尚未同步最近人工修改。以下报告/PPT暂停及旧页数记录均保留此前语境。

本轮报告修订（2026-11-15）：将报告6.4拆为6.4.1“Amdahl定律：固定规模下的加速表现”和6.4.2“Gustafson定律：扩大工作量后的可扩展性”，保留原分析、公式、数据及其他正文。已同步13页PDF，两个子节完整位于第11页，四级标题及正文衔接已实际渲染检查。工作区既有的图表重绘和报告修改保留，本轮未自动提交推送。

提交记录（2026-11-16）：用户明确要求提交上述现有材料，报告/九图/统计与校验清单已重新核对，通过后按授权一并提交推送origin/M5。上文及前序记录中的“未自动提交”描述保留当时语境；报告及M5仍待验收。PDF沿用前轮已实际渲染且哈希一致的13页版本，本轮未重新生成PDF或增加实验。

第5节修订（2026-11-16）：按用户六项要求修订报告第5节：先说明比较三种实现的目的，再定义S/E；明确五档并行度，清理编译选项标签，澄清初始化后计时，展开采样次数并简述停止实验与bootstrap方法。本轮已生成并实际渲染13页PDF，第5节位于第7—8页；其他章节原文与原计时范围表保持。执行期间工作区有另一项图表修改，已保留，本轮未自动提交推送。

## 先看这两个文件

| 文件 | 用途 |
| --- | --- |
| [FINAL_REPORT.md](FINAL_REPORT.md) | 书面报告的唯一编辑源稿，后续内容修改从这里开始 |
| [FINAL_REPORT.pdf](FINAL_REPORT.pdf) | 此前生成的16页A4预览，尚未同步最近人工修改 |

第6节按“固定规模的实际加速效果—扩大工作量的吞吐变化—两个定律分析—诊断因素—实验限制”展开。使用两张重新设计的结果图，增加便于比较的原实验、工作量、吞吐和诊断表格；结论直接对应实测结果，资源/轮次/时钟限制集中说明。

报告使用已验收M4数据和重新设计的结果图。原始证据统一在[results/RESULTS.md](../results/RESULTS.md)，实现依据在[docs/DESIGN.md](../docs/DESIGN.md)。本轮第1—4节采用中文伪代码串起初始化、计算、换层、通信/同步和输出，区分解析误差与串并行差。摘要及第5—7节原文保持，第8节仅清理第三类参考残留。未修改求解器或原始数据，未新增实验，未推进PPT。

## 目录分工

```text
report/
├── FINAL_REPORT.md / FINAL_REPORT.pdf   书面报告源稿与现有预览
├── render_report.py                    从源稿生成A4 PDF
├── check_report.py                     独立核查报告，不依赖PPT
├── README.md / SHA256SUMS              本入口与当前文件校验清单
├── records/                            M5准备、历史核查、目录迁移和本轮报告检查
├── presentation/                       PPT成品、逐页讲稿、问答和相关工具
│   ├── current/                        最新v5（10正文＋4备份），保留v4-r1
│   └── history/v1…v4/                  历版成品保留
├── heat-defense_ppt169_20261112/        既有PPT制作工作区，位置保留
└── paperbanana/                        制图工具调研、输入样稿和独立机理图
```

2026-11-15前一轮目录整理前共有98个跟踪文件，其中39个位于根目录；33个文件归类移动，未删除历史材料。现在报告正文、预览和工具与PPT成品分开。PPT工作区保留位置以免影响已有预览服务；目录整理时仅修复其指向移动文件的链接；本轮报告修订未修改PPT页面或重新导出。

| 其他入口 | 内容 |
| --- | --- |
| [records/README.md](records/README.md) | 准备说明、历史审核记录、旧校验清单及本轮迁移检查的区别 |
| [presentation/README.md](presentation/README.md) | PPT各版本、讲稿、问答、当前v5核查与生成命令 |
| [PPT工作区说明](heat-defense_ppt169_20261112/README.md) | 规范、源SVG、素材副本、备注与工具审计 |
| [制图调研与素材](paperbanana/README.md) | PaperBanana安装调研及本地绘制的SVG/PNG/PDF；属于辅助素材 |

## 本轮图表更新（2026-11-15）

扩大网格实验9组图（18个PNG/SVG）已在原路径替换，中文、无标题及图内解释、只标N或P(Q)。全部原始样本和统计区间保留；归一化耗时定义、统计方法及资源限制见图外generation.json和results/RESULTS.md。旧PPT及其图像副本保持原版本。

本轮实际运行绘图、scripts/check_results.py、报告生成及独立检查，通过44配置/440样本覆盖和归档统计核对。13页PDF全部渲染，AI查看总览和第10页，两图及图注完整同页；绘图时所有坐标及图例均在画布内。报告源稿保持本轮开始时用户稿的原字节，检查器兼容其当前表头。尚未人工验收，尚未提交/推送，原因是用户源稿已有其他未提交修改。

## 书面报告工具

检查现稿及归档数值，不调用求解器、不检查或渲染PPT：

```bash
build/tools/python/bin/python report/check_report.py
```

检查结果写入[records/report_checks.json](records/report_checks.json)。本轮逐格核对固定规模11行的耗时/S和四网格6列的串行耗时及MPI/OpenMP16 S/E，另核对8章、2图链接与M3误差比/观测阶。两表之外的源稿逐字保持，143处数学表达式保持。13页PDF均已实际渲染，AI查看总览和第9页；两表完整同页、数字不折行、图注同页及页界通过。软件与AI核查不等同全报告定稿或用户验收。

修改源稿后生成PDF：

```bash
build/tools/python/bin/python report/render_report.py --font /mnt/c/Windows/Fonts/msyh.ttc --math-python python3
```

生成需要reportlab、Pillow及Matplotlib；默认只读使用本机Microsoft YaHei字体，可用`--font`指定其他已有中文TrueType字体。字体、工具环境和临时数学图片不入Git。该生成命令本轮已运行。生成器同步正文日期到页脚，逐项排版编号步骤，保留伪代码缩进并避免整段跨页，行内数学字号/基线随正文或表格字号，并将图与图注保持同页。

后续由用户审阅当前PPT与报告，完成个人信息和实际计时演练。个人信息、实际人工复核与最终验收由用户确认，不以历史M4验收替代。


2026-11-16图表更新：已按最新选择恢复按网格分组子图的N、M，重新生成9组图替换原文件，同步当前用户稿的13页PDF；两张结果图位于第10页。统计核查通过，PPT保持。前文去掉M为历史选择。


本次提交授权（2026-11-16）：用户明确要求将第5节及同期恢复N/M标识的材料一并提交；报告/归档统计/九图/校验清单重新检查通过，按授权提交推送origin/M5。前序未提交说明为当时记录，报告及M5仍待用户验收。


第6节本轮统计：人工保存稿相对e413c69为119→267行、5031→10307字符、6→5张表；AI格式稿相对保存稿新增数学排版65处（7行间＋58行内），删除用户确认的旧标题/旧导语，最终第6节256行。内容通过反向还原核对，数值保持；完整统计见records/report_checks.json。当前PDF为16页，前文13页均属前序交付记录。


本次提交授权（2026-11-16，第6节与统一标题）：用户明确要求一并提交人工第6节、公式适配、35个标题、16页PDF及工具/记录。独立报告检查、标题/PDF属性及校验清单复查通过，按授权提交推送origin/M5；前序未提交说明保留当时语境，材料仍待用户验收。
