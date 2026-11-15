# 书面报告

当前工作（2026-11-15）：先审阅、完善书面报告，PPT工作暂停。报告现有稿件保留原内容，尚未由用户验收为最终稿；姓名、学号仍待填写。

## 先看这两个文件

| 文件 | 用途 |
| --- | --- |
| [FINAL_REPORT.md](FINAL_REPORT.md) | 书面报告的唯一编辑源稿，后续内容修改从这里开始 |
| [FINAL_REPORT.pdf](FINAL_REPORT.pdf) | 现有8页A4预览，与本轮整理前字节一致；本轮没有重新生成 |

现稿依次包含：任务与范围；数学模型、均匀网格/时间离散、五点格式、稳定性和双缓冲；独立串行/MPI/OpenMP实现；正确性证据；性能环境、编译和计时口径；三批真实结果及Amdahl/Gustafson分析；AI使用；结论与复现；引用。

报告使用已验收M4数据和原图。原始证据统一在[results/RESULTS.md](../results/RESULTS.md)，实现依据在[docs/DESIGN.md](../docs/DESIGN.md)。本轮仅整理文件与核查入口，不新增实验、不改报告科学内容，也不把既有检查当作本轮求解器测试。

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

整理前共有98个跟踪文件，其中39个位于根目录；33个文件归类移动，未删除历史材料。现在报告正文、预览和工具与PPT成品分开。PPT工作区保留位置以免影响已有预览服务；本轮只修复其指向移动文件的链接，没有修改页面或重新导出。

| 其他入口 | 内容 |
| --- | --- |
| [records/README.md](records/README.md) | 准备说明、历史审核记录、旧校验清单及本轮迁移检查的区别 |
| [presentation/README.md](presentation/README.md) | PPT各版本、讲稿、问答和后续恢复制作所需命令；当前不推进 |
| [PPT工作区说明](heat-defense_ppt169_20261112/README.md) | 规范、源SVG、素材副本、备注与工具审计 |
| [制图调研与素材](paperbanana/README.md) | PaperBanana安装调研及本地绘制的SVG/PNG/PDF；属于辅助素材 |

## 书面报告工具

检查现稿及归档数值，不调用求解器、不检查或渲染PPT：

```bash
build/m5-tools/bin/python report/check_report.py
```

检查结果写入[records/report_checks.json](records/report_checks.json)。包含报告链接、章节、归档CSV中的加速比/效率与误差比、已有PDF签名/页数/文字页界；文件存在或软件核查通过不等同报告内容已人工验收。

修改源稿后生成PDF：

```bash
build/m5-tools/bin/python report/render_report.py --font /mnt/c/Windows/Fonts/msyh.ttc --math-python python3
```

生成需要reportlab、Pillow及Matplotlib；默认只读使用本机Microsoft YaHei字体，可用`--font`指定其他已有中文TrueType字体。字体、工具环境和临时数学图片不入Git。该生成命令本轮未运行，现有PDF保持原样。

后续先按教师要求审阅报告内容与排版，再由用户安排PPT任务。个人信息、实际人工复核与最终验收由用户确认，不以历史M4验收替代。
