# PPT与答辩材料

当前交付为用户15页手改稿的P09/P10局部修订：

- [最新PPTX](current/presentation-v5-wps-r1.pptx)、[WPS导出PDF](current/presentation-v5-wps-r1.pdf)、[两页预览](current/presentation-v5-wps-r1-p09-p10.png)、[全页总览](current/presentation-v5-wps-r1-contact.png)。
- P09补充MPI16与OpenMP16跨网格对比原生图；P10定义吞吐量及增长倍数，原生表格展示p=1、2、4三组配置，表下写“并行收益均低于理想线性扩展水平”。
- 仅P09/P10及其备注变化；其余13页XML和备注逐字节保留，媒体链接的解析内容保持。具体核查见[检查记录](../records/p9_p10_checks.json)，可追溯局部源与导出修复见[修订说明](revisions/p9-p10-20261116/README.md)。
- 图表/表格可编辑，两个新定义公式为原生Office Math。15页已由WPS实际导出，AI检查修改页和总览；源门0错误0警告，包检查通过。原稿页码和其他页面既有问题保持，未将局部修改当作整稿验收；人工演练未运行。

后续从最新PPTX编辑。下文为前序公式统一与生成版本记录，不代表用户15页改稿与旧PDF/讲稿同步。

## 前序公式统一

当前文件为用户手工修订后、经Windows MCP在WPS中统一公式的版本：

- [WPS修订PPTX](current/presentation-v5-wps.pptx)、[WPS导出PDF](current/presentation-v5-wps.pdf)、[全页总览](current/presentation-v5-wps-contact.png)。
- [公式与保留检查](../records/wps_formula_checks.json)：14页、12个原生公式，数学字体Cambria Math；分式、上下标和行内变量同步统一，清除Amdahl旧文本叠影，调整公式附近间距。
- [用户输入PPTX](current/presentation-v5.pptx)按开始时原字节保留。第9页按用户确认，四组N/M改为384/9216、512/16384、768/36864、1024/65536，与四个MPI16加速比对应。
- WPS实际导出14页PNG及PDF，AI查看全页总览和公式页；两张完整结果图原PNG字节及14页备注原文保持。第10页正文在用户输入中为空，本轮保持；外部逐页讲稿尚未按用户手工修改重新核对，真实演练未运行。

**后续编辑从WPS修订PPTX继续。** 下面的SVG、讲稿、旧v5 PDF和检查记录属于此前生成版本，不能证明当前用户修订版内容同步；从旧SVG重新导出会覆盖用户修改。本轮未通过SVG重建页面，未刷新书面报告PDF，未运行求解器或增加性能采样。

## 此前生成版本与检查记录

当前交付为2026-11-16制作的v5，按用户批准的设计规范及“非实现者只接触PPT和最终报告”要求制作。10页正文＋4页备份，主讲预算280秒，另留20秒。沿用《单幅图像去雾-第二组》参考的页眉、蓝白配色、黑体标题和楷体正文；模型、网格、五点读写、串行循环、MPI、OpenMP依次展开，再展示验证与性能。没有内部实验批次称谓、文件路径或另读实验报告的前提。

| 材料 | 文件 |
| --- | --- |
| 新版演示 | [可编辑PPTX](current/presentation-v5.pptx)、[14页PDF预览](current/presentation-v5.pdf)、[全页总览](current/presentation-v5-contact.png) |
| 讲稿与问答 | [SPEAKER_NOTES](SPEAKER_NOTES.md)、[39项DEFENSE_QA](DEFENSE_QA.md)；PPT内嵌14页备注 |
| 当前书面内容 | [最终报告Markdown](../FINAL_REPORT.md)；[既有PDF](../FINAL_REPORT.pdf)未同步最近人工修改，本轮保持 |
| 核查结果 | [包检查](current/presentation-v5_postflight.json)、[实际渲染检查](current/presentation-v5-render-check.json)、[独立数值/包检查](../records/presentation_checks.json) |
| 制作源 | [设计规范](../heat-defense_ppt169_20261112/design_spec.md)、[执行约束](../heat-defense_ppt169_20261112/spec_lock.md)、工作区svg_output/与notes/ |
| 独立图源 | [五点与完整循环SVG/PNG/PDF](../paperbanana/stencil-sol-v1/README.md)；现有素材参考，不调用新图像API |

图示、文字和主性能图保留可编辑图元，4个公式为原生Office Math。完整对比图使用两张未经改写的PNG，完整保留并可在PPT/PDF放大查看。原始结果、求解器、构建配置及课程资料保持，本轮没有新的求解器运行或性能采样。姓名学号暂留待填写。

## 讲述与核查

正文仅第1—10页，备份第11—14页不计入主讲。讲稿956个中英文/数字字符，按280字符/分钟加20秒停顿估算约224.9秒；280秒为逐页讲述预算，不把估算冒充真实演练。可利用余量指图、停顿和过渡，人工计时演练及Microsoft PowerPoint本机显示/编辑待本人完成。

实际LibreOffice打开PPTX并导出14页PDF，全部页面渲染，AI查看总览及第3/8/11/14页放大图；文字没有越界。包内14页备注、4原生公式及298个可编辑文本run，无动画或自动切换。主图10个点和10条不对称区间对照统计CSV，最大坐标误差小于0.003px；两张完整图在PPT包内保留原文件字节。

源质量门有5项建议，均为独立条件、参数或指标行使用分开文本框的组织提示，没有边界或公式错误；它们不属于同一叙述段落，保留独立编辑对象。包检查为passed-with-warnings。PowerPoint Office Math使用原生对象；LibreOffice显示其矢量/文字回退，不能代替PowerPoint人工编辑验证。

## 核查与再导出

以下检查只读归档数据，不启动求解器。报告检查独立使用上级check_report.py；本工具不宣称报告PDF与最新Markdown同步。

```bash
build/tools/python/bin/python report/presentation/check_materials.py
python3 scripts/check_results.py
```

以下命令仅适用于此前生成版本，该阶段以svg_output为设计源。修改内容应先同步同一设计规范，保持公式、图表和讲稿一致；不要从PDF或截图反向制作。以下技能路径为本机安装位置：

```bash
python3 /home/nuo/.codex/skills/ppt-master/scripts/project_manager.py validate report/heat-defense_ppt169_20261112
python3 /home/nuo/.codex/skills/ppt-master/scripts/svg_quality_checker.py report/heat-defense_ppt169_20261112 --canonical-authoring --stage final --json
python3 /home/nuo/.codex/skills/ppt-master/scripts/total_md_split.py report/heat-defense_ppt169_20261112
python3 /home/nuo/.codex/skills/ppt-master/scripts/finalize_svg.py report/heat-defense_ppt169_20261112
build/tools/python/bin/python /home/nuo/.codex/skills/ppt-master/scripts/svg_to_pptx.py report/heat-defense_ppt169_20261112 --no-animations
```

从exports中选择本次成功导出的文件，复制为current/presentation-v5.pptx后，用本机LibreOffice实际打开并渲染。render_presentation.py默认读取v5，支持--input、--soffice、--library-path和--fontconfig。本轮使用忽略目录build/tools/libreoffice中的LibreOffice 24.2.7.2，修复了目录迁移遗留的3份本地配置旧路径；无需系统安装，字体只读使用，不随Git。

P03公式矢量回退沿用已修复的STIX排版，原生公式仍可编辑。工具仅生成公式片段，不生成整页：

```bash
python3 report/presentation/render_formula_preview.py --source report/heat-defense_ppt169_20261112/svg_output/03_stencil.svg --output build/formula-preview.svg
```

## 版本与历史

v4-r1仍保留在current中，v1—v4位于history。旧12页交付、批注修订和检查记录属于各自历史，不与v5页码混用。2026-11-15暂停PPT制作；2026-11-16用户恢复并确认新规范。本轮制作不等于用户对PPT或M5的最终验收。
