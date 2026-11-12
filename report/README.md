# 最终报告与答辩材料

M5材料已完成生成及AI工具核查，待用户验收。用户确认报告Markdown＋A4 PDF、16:9可编辑PPTX＋PDF、逐页讲稿/问答，并确认算法示意＋计算流程＋证据陈述的组合设计。个人信息暂留待填写。

| 材料 | 文件 |
| --- | --- |
| 最终报告 | [Markdown](FINAL_REPORT.md)、[8页A4 PDF](FINAL_REPORT.pdf) |
| 5分钟演示 | [可编辑PPTX](presentation.pptx)、[12页PDF预览](presentation.pdf)、[渲染总览](presentation-contact.png) |
| 逐页讲稿 | [SPEAKER_NOTES](SPEAKER_NOTES.md)：8页正文、280秒预算，另留20秒；PPT已嵌入12页备注 |
| 答辩准备 | [DEFENSE_QA](DEFENSE_QA.md)：算法、代码、统计、资源、时钟及AI说明 |
| 核查结果 | [REVIEW](REVIEW.md)、[自动核查JSON](material_checks.json)、[PPT包检查](presentation_postflight.json) |
| 制作依据 | [M5_PREPARATION](M5_PREPARATION.md)、[设计规范](heat-defense_ppt169_20261112/design_spec.md)、[执行约束](heat-defense_ppt169_20261112/spec_lock.md) |

原始证据在[results](../results/RESULTS.md)。本阶段未修改求解器、未运行新的数值构建/回归、未增加采样。课程资料只读、不随Git；字体只读使用、不分发。PPT正文、算法图、性能主图均为可编辑文本/图元，五点公式含原生Office Math；两页备份图复用完整原PNG。科学计算数据未被替换为装饰性图像。

## 讲述与人工待办

只讲第1–8页，第9–12页留给提问。讲稿1220个中英文/数字字符，在280字符/分钟加20秒停顿的显式假设下约281.4秒；这是估算，不能代替本人计时演练。姓名学号、本人对代码和结论的掌握、真实实讲及PowerPoint本机显示/编辑仍待本人核实。M4验收不能代替M5材料验收。

## 复现材料

报告生成使用reportlab、Pillow与带Matplotlib的Python；PPT生成使用本地ppt-master技能。默认报告只读使用已有Microsoft YaHei字体，可通过--font指定机器上已有的中文TrueType字体。技能包、字体和工具环境不纳入Git。

```bash
build/m5-tools/bin/python report/render_report.py --font /mnt/c/Windows/Fonts/msyh.ttc --math-python python3
python3 report/check_materials.py
python3 scripts/check_results.py
```

PPT的规范、源SVG、两幅既有图表副本、统计CSV副本和备注均在heat-defense_ppt169_20261112。svg_output是唯一页面设计源；不从PDF或预览图反向制作。将下列技能路径替换为本机实际位置，先验证/导出，再使用LibreOffice实际打开PPTX生成PDF：

```bash
python3 /home/nuo/.codex/skills/ppt-master/scripts/project_manager.py validate report/heat-defense_ppt169_20261112
python3 /home/nuo/.codex/skills/ppt-master/scripts/svg_quality_checker.py report/heat-defense_ppt169_20261112 --canonical-authoring --stage final --json
python3 /home/nuo/.codex/skills/ppt-master/scripts/total_md_split.py report/heat-defense_ppt169_20261112
python3 /home/nuo/.codex/skills/ppt-master/scripts/finalize_svg.py report/heat-defense_ppt169_20261112
build/m5-tools/bin/python /home/nuo/.codex/skills/ppt-master/scripts/svg_to_pptx.py report/heat-defense_ppt169_20261112 --no-animations
# 选择本次exports目录的新文件复制为report/presentation.pptx，再渲染：
python3 report/render_presentation.py --soffice /path/to/soffice
```

本轮使用解包在build/m5-lo的隔离LibreOffice24.2.7.2及只读Windows字体配置，未系统安装。render_presentation.py还支持--library-path及--fontconfig。PDF从最终PPTX实际转换，展示非PowerPoint客户端的公式预览回退；包内Office Math验证不等同已在Microsoft PowerPoint中人工编辑。

PPT Master的时间戳exports、backup、svg_final和浏览器运行状态按本目录.gitignore排除；最终PPTX/PDF位于本目录。生成日志与质量报告保留在项目validation。源报告归档副本仅归一化了相对链接，原CSV与PNG副本字节不变。
