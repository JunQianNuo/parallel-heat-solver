# 书面报告

当前工作（2026-11-15）：报告面向非实现者，实验按目的命名为基础性能实验、补充诊断实验、扩大网格实验；正文不要求读者理解内部运行编号。本轮清理相关名称和说明，并同步12页PDF。原有两条Rivise标记与其他待修订事项保留，PPT暂停，报告仍待用户审阅。

## 先看这两个文件

| 文件 | 用途 |
| --- | --- |
| [FINAL_REPORT.md](FINAL_REPORT.md) | 书面报告的唯一编辑源稿，后续内容修改从这里开始 |
| [FINAL_REPORT.pdf](FINAL_REPORT.pdf) | 本轮从当前Markdown生成的12页A4预览，已逐页渲染检查 |

第6节按“固定规模的实际加速效果—扩大工作量的吞吐变化—两个定律分析—诊断因素—实验限制”展开。保留两张原图，增加便于比较的原实验、工作量、吞吐和诊断表格；结论直接对应实测结果，资源/轮次/时钟限制集中说明。

报告使用已验收M4数据和原图。原始证据统一在[results/RESULTS.md](../results/RESULTS.md)，实现依据在[docs/DESIGN.md](../docs/DESIGN.md)。前轮已完成第6节组织修订；本轮统一摘要、实验方法、结果与AI说明中的实验名称，简化需要依赖内部历史才能理解的措辞。算法、数据、原图和实验限制保持；不改求解器、不新增实验、不推进PPT，原伪代码/数学符号修订标记与此前衔接问题未在本轮处理。

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

检查结果写入[records/report_checks.json](records/report_checks.json)。本轮核对2图表路径、8章、归档S/E与误差比；36处数学表达式保持，逐单元格比较71行表格，仅四个实验名称和一项对照设置措辞变化，全部数值不变。记录12页PDF实际生成/逐页渲染、无内部编号残留及图注同页检查，并在内部记录保留实验名称与工件目录的对应关系。软件与AI核查不等同全报告定稿或用户验收。

修改源稿后生成PDF：

```bash
build/tools/python/bin/python report/render_report.py --font /mnt/c/Windows/Fonts/msyh.ttc --math-python python3
```

生成需要reportlab、Pillow及Matplotlib；默认只读使用本机Microsoft YaHei字体，可用`--font`指定其他已有中文TrueType字体。字体、工具环境和临时数学图片不入Git。该生成命令本轮已运行。生成器同步正文日期到页脚，逐项排版编号步骤，并将图与图注保持同页。

后续先按教师要求审阅报告内容与排版，再由用户安排PPT任务。个人信息、实际人工复核与最终验收由用户确认，不以历史M4验收替代。
