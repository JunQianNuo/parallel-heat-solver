# 黑体＋楷体：仅字体修订

用户在网页对比后明确选择“黑体加楷体，字体大小不用变，请仅修改字体”。以最新人工保存的r3为输入，另存[可编辑r4](../../current/presentation-v5-wps-r4.pptx)、[WPS PDF](../../current/presentation-v5-wps-r4.pdf)、[总览](../../current/presentation-v5-wps-r4-contact.png)，输入原文件保留。

原稿主题已采用SimHei/KaiTi，大部分文字无需替换。本次修正封面标题、正确性表格中文表头、总结页“串行”残留微软雅黑、环境表中文表头及定律小标题的覆盖设置：共5个页XML、25个字体名称属性。中文标题/表头用黑体，正文用楷体；原英文字母、数字和数学字体保留。嵌入图片内文字保持原图，未重新绘图。

为满足“仅字体”，直接在原生PPTX中精确替换字体名，不经SVG重建，也不通过WPS保存重写PPTX。逐节点比较只允许DrawingML字体节点的typeface属性不同，并把字体名称归一化后对XML原字节比对；其余全部包成员逐字节保持。字号、粗斜体、基线/上下标、颜色、文本、坐标、几何、布局设置、页序、备注、图表、图片、嵌入对象及Office Math保持。证明见[font-only-checks.json](font-only-checks.json)。未声称完成ppt-master的SVG往返流程。

[交付检查](delivery.json)通过，保留字体可移植性建议。Windows MCP在WPS打开只读副本，实际导出16页PNG/PDF；AI查看总览、封面、正确性、总结、环境表和定律页。五个修改页PDF文字均位于页内，未调整任何字号或位置来适应字体。未运行Microsoft PowerPoint检查、人工演练、求解器或性能实验。

执行时输入快照和临时渲染保存在忽略目录build/logs/m5-font-only-20261116；后续独立的工作区清理已移除其中的PPT副本，备份位置见report/records/workspace-cleanup-20261116.json。最终再次确认当前r3仍与输入哈希一致、r4仍与输出哈希一致。[SHA256SUMS](SHA256SUMS)为本次独立清单，根目录运行sha256sum -c report/presentation/revisions/font-only-20261116/SHA256SUMS。此前report/SHA256SUMS及旧r3渲染证据不代表当前人工改稿已同步。已有用户报告/PPT未提交修改保留，按AGENTS.md本轮未自动提交推送。
