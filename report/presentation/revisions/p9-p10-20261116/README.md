# P09/P10 局部修订（2026-11-16）

用户确认P09增加OpenMP16对照后，对其15页手改PPT执行ppt-master Edit Native PPTX流程。输入为[用户手改WPS版](../../current/presentation-v5-wps.pptx)，输出为[修订PPTX](../../current/presentation-v5-wps-r1.pptx)、[WPS PDF](../../current/presentation-v5-wps-r1.pdf)、[两页预览](../../current/presentation-v5-wps-r1-p09-p10.png)。输入哈希及归档数值核查见[本轮检查](../../../records/p9_p10_checks.json)。

- P09：新增可编辑原生折线图，对比四组网格的MPI16/OpenMP16加速比；修正错误的工作量不变表述，保留N/M、MPI数值及结论。图中类别是四个独立网格配置，等距排列；不是连续数值横轴。点为各规模中位数之比，未额外绘制区间。
- P10：定义吞吐量及相对各实现自身单执行单元配置的增长倍数；新增原生三配置表，给出用户指定结论及p>1适用范围，标题不称弱扩展。
- 仅这两页及备注变化，其余13页XML、关联关系和备注与输入逐字节一致；两个完整结果图PNG原字节保留。原稿页码仍沿用此前值（P09显示8/14、P10显示9/14），其他页面没有进行全局改写；第11页原有空白正文保持。

[slide_09.svg](slide_09.svg)、[slide_10.svg](slide_10.svg)是当前输入经往返导入后的局部编辑源，并非可脱离原始PPT单独恢复整份文件的模板；[两页备注](slide_09.md)及[第10页备注](slide_10.md)只同步对应页，不代表旧外部全稿与15页改稿同步。[编辑计划](edit_plan.json)、[源质量门](svg_quality_report.json)、[导出检查](postflight.json)和[交付检查](delivery.json)保留本轮适用范围。源门0错误0警告、包检查通过；交付检查仅有字体可移植性建议，已经WPS实际打开检查，未运行Microsoft PowerPoint检查或人工演练。

完整临时往返工作区保存在忽略目录build/logs/m5-p9-p10-20261116/roundtrip。可从输入重新运行pptx_to_svg.py --inheritance-mode both --roundtrip，随后将本目录两份SVG、两份备注覆盖到新工作区对应目录，刷新摘要并运行--roundtrip质量门，再导出。所有未编辑页须由输入原生恢复，不能从历史整套SVG重建。

本轮工具首次导出新增Office Math时缺少a14前缀绑定；[本地导出入口](export_with_math_namespace.py)只为原导出器登记标准Office Math命名空间，原有校验全部保留，安装的skill文件未改。最终调用该入口加参数“工作区 --roundtrip --native-charts-and-tables --primary-language zh-CN”。原生公式改为预留足够高度的一行数学对象，解决WPS对分组块回退的重叠显示；不使用公式图片或手写OMML。P09受影响的旧条件公式按批准内容替换，其他WPS公式不重建。

WPS对最终文件导出15页PNG及PDF，未保存或规范化PPTX，因此保留13页原生字节证明。AI实际查看P09/P10放大图和全页总览。仅本轮两页的PDF文字边界检查通过；P02原稿有越界标签，保持输入内容，不将整稿说成已通过全局排版验收。书面报告、求解器、原始数据和课程资料未改，未新增采样。
