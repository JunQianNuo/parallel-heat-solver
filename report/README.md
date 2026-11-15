# 书面报告

当前工作（2026-11-15）：先审阅、完善书面报告，PPT工作暂停。报告面向课程教师独立阅读，先说明功能、输入输出与实际效果，随后直接交代项目方法和结果分析；已删除课程概念入门解释、引用编号、证据索引及内部交接指引，并同步生成PDF。姓名、学号仍待填写，报告尚未验收。

## 先看这两个文件

| 文件 | 用途 |
| --- | --- |
| [FINAL_REPORT.md](FINAL_REPORT.md) | 书面报告的唯一编辑源稿，后续内容修改从这里开始 |
| [FINAL_REPORT.pdf](FINAL_REPORT.pdf) | 本轮从当前Markdown生成的12页A4预览，已逐页渲染检查 |

现稿先说明薄板冷却问题、三种方式的功能、输入参数与CSV/摘要输出，再给出均匀网格、五点格式、双数组时间推进与稳定性处理。实现部分按分工与依赖讲解MPI邻接行交换和OpenMP换层同步；验证区分解析误差与串并行差。性能部分先交代公平比较方法，再展示最大网格的实际耗时及完整趋势、Amdahl/Gustafson与诊断限制，最后说明AI使用与项目结论。

报告使用已验收M4数据和原图。原始证据统一在[results/RESULTS.md](../results/RESULTS.md)，实现依据在[docs/DESIGN.md](../docs/DESIGN.md)。教师阅读的正文已删除仓库引用、提交身份、内部验收/交接说明与复现脚本入口；课程通用定义与比喻已删除，实验数据、项目统计口径、测试方法和AI核查实例保留。内部追溯仍通过本入口及records维护，已有数据、正式程序和性能结论口径保持。未新增实验；材料核查不作为重新运行求解器的测试记录。

## 目录分工

```text
report/
├── FINAL_REPORT.md / FINAL_REPORT.pdf   书面报告源稿与现有预览
├── render_report.py                    从源稿生成A4 PDF
├── check_report.py                     独立核查报告，不依赖PPT
├── README.md / SHA256SUMS              本入口与当前文件校验清单
├── records/                            M5准备、历史核查、目录迁移和本轮报告检查
├── presentation/                       既有PPT成品、讲稿、问答和相关工具
│   ├── current/                        最近既有v4-r1；仍待用户验收
│   └── history/v1…v4/                  历版成品保留
├── heat-defense_ppt169_20261112/        既有PPT制作工作区，位置保留
└── paperbanana/                        制图工具调研、输入样稿和独立机理图
```

2026-11-15前一轮目录整理前共有98个跟踪文件，其中39个位于根目录；33个文件归类移动，未删除历史材料。现在报告正文、预览和工具与PPT成品分开。PPT工作区保留位置以免影响已有预览服务；目录整理时仅修复其指向移动文件的链接；本轮报告修订未修改PPT页面或重新导出。

| 其他入口 | 内容 |
| --- | --- |
| [records/README.md](records/README.md) | 准备说明、历史审核记录、旧校验清单及本轮迁移检查的区别 |
| [presentation/README.md](presentation/README.md) | PPT各版本、讲稿、问答和后续恢复制作所需命令；当前不推进 |
| [PPT工作区说明](heat-defense_ppt169_20261112/README.md) | 规范、源SVG、素材副本、备注与工具审计 |
| [制图调研与素材](paperbanana/README.md) | PaperBanana安装调研及本地绘制的SVG/PNG/PDF；属于辅助素材 |

## 书面报告工具

检查现稿及归档数值，不调用求解器、不检查或渲染PPT：

```bash
build/tools/python/bin/python report/check_report.py
```

检查结果写入[records/report_checks.json](records/report_checks.json)。包含2个图表素材链接、8个章节、归档CSV中的加速比/效率与误差比、PDF签名/页数/文字页界。本次修订记录另核对36处数学表达式与57行科学表格保持、最大网格5行耗时，记录12页PDF实际生成/逐页渲染、引用残留检查与图注同页检查；check_report.py本身只读取PDF，不执行生成或目视检查。文件存在或软件核查通过不等同报告内容已人工验收。

修改源稿后生成PDF：

```bash
build/tools/python/bin/python report/render_report.py --font /mnt/c/Windows/Fonts/msyh.ttc --math-python python3
```

生成需要reportlab、Pillow及Matplotlib；默认只读使用本机Microsoft YaHei字体，可用`--font`指定其他已有中文TrueType字体。字体、工具环境和临时数学图片不入Git。该生成命令本轮已运行。生成器同步正文日期到页脚，逐项排版编号步骤，并将图与图注保持同页。

后续先按教师要求审阅报告内容与排版，再由用户安排PPT任务。个人信息、实际人工复核与最终验收由用户确认，不以历史M4验收替代。
