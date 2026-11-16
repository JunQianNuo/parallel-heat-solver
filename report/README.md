# 书面报告与答辩材料

| 材料 | 当前入口 |
| --- | --- |
| 报告编辑源稿 | [FINAL_REPORT.md](FINAL_REPORT.md) |
| 报告预览 | [FINAL_REPORT.pdf](FINAL_REPORT.pdf)，尚未同步最近人工修改 |
| 最新PPT r4 | [可编辑PPTX](presentation/current/presentation-v5-wps-r4.pptx)、[PDF](presentation/current/presentation-v5-wps-r4.pdf) |
| 上一版PPT r3 | [可编辑PPTX](presentation/current/presentation-v5-wps-r3.pptx)、[PDF](presentation/current/presentation-v5-wps-r3.pdf) |
| 讲稿及问答 | [PPT材料说明](presentation/README.md) |
| 历史核查与清理清单 | [records/README.md](records/README.md) |

2026-11-16按用户要求清理旧版：报告只保留当前编辑源稿及现有PDF，PPT只保留最新两版r4/r3。旧成品、旧预览、制作导出副本和临时报告快照已移出工作区；所有移除文件都有仓库外备份，详情见[清理清单](records/workspace-cleanup-20261116.json)。本轮保留当前报告及两版PPT/PDF原字节，没有重新生成材料。

旧制作SVG、备注、预览网页和运行缓存已清理；已应用的修订源与历史检查记录继续保留用于追溯。原始实验数据及分析见[results/RESULTS.md](../results/RESULTS.md)，数学与并行设计见[docs/DESIGN.md](../docs/DESIGN.md)。

报告工具仍使用本地Python环境：

```bash
build/tools/python/bin/python report/check_report.py
build/tools/python/bin/python report/render_report.py --font /mnt/c/Windows/Fonts/msyh.ttc --math-python python3
```

生成需要reportlab、Pillow、Matplotlib及已有中文字体。字体、工具环境和临时数学图片不入Git。check_report.py只核查报告及归档数值，不检查PPT；上述命令本轮未运行。

用户审阅、真实成员贡献/AI核查实例填写、实际计时演练及M5验收仍待完成。工作区已有任务外报告修改，本轮不自动提交推送。
