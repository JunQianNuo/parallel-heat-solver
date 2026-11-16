# P7、P11与校徽封面修订

以用户最新保存的15页r2为输入，另存[16页PPTX](../../current/presentation-v5-wps-r3.pptx)、[WPS PDF](../../current/presentation-v5-wps-r3.pdf)、[修改页预览](../../current/presentation-v5-wps-r3-changes.png)和[总览](../../current/presentation-v5-wps-r3-contact.png)。原r1/r2未覆盖。执行中发现用户再次保存P1版式，重新导入最新输入后导出；本目录检查记录给出实际输入/输出哈希。

- 新增首位封面：沿用蓝白、黑体/楷体，校徽提取自本地只读《单幅图像去雾-第二组》封面，未改原PDF；不另写学校全称。报告人为靳卓凡，小组成员为王君豪、靳卓凡。
- 原P7（输出P8）：原三组网格表新增D∞列，三值均为0。已有验证数据涵盖相同T、α、r的Debug/Release、MPI和OpenMP实际1—4执行单元，不能推广到所有配置。表格为可编辑文本与线条，未声称是Office原生表格对象；符号采用实际下标。
- 原P11（输出P12）：左栏三条总结，第三条为“并行收益受实现与配置影响”；右栏AI声明为“AI辅助代码实现与报告初稿”。用户要求两位成员分工、AI使用环节及核查/采纳实例留空，按要求保留可填写位置。删去排他词“仅”，避免与已记录的测试、实验和材料制作中的AI参与相矛盾。

仅两页正文和备注及新封面有编辑。其余13页XML、备注原字节和关联媒体/图表解析内容保持；28个原生oMath XML节点数量保持。原页脚页码未全局改写，旧外部全稿讲稿也未同步人工改稿；最新对应讲稿以PPT内嵌备注为准。没有增加动画、配音或自动翻页。

实际执行ppt-master Edit Native：导入、局部编辑、刷新摘要、源质量检查、roundtrip导出、交付检查和文字回读。首次JPEG校徽导出产生重复jpg内容类型，交付检查失败；将同一校徽像素转为PNG后从源SVG重导，未手改PPT包或绕过检查。最终源门0错误0警告，postflight及包/关系检查通过；字体可移植性仍有建议，WPS目标环境已实际渲染16页并检查三处修改与总览。三处修改页PDF文字位于页面内。未运行人工演练、Microsoft PowerPoint检查或新增数值/性能实验；不能将软件渲染当作用户验收。

使用[checks.json](checks.json)、[D列数据核对](d-column-evidence.json)、[交付检查](delivery.json)、[源质量](svg_quality_report.json)和[导出检查](postflight.json)追溯。完整临时往返工作区及只读输入备份位于忽略目录build/logs/m5-p7-p11-cover-20261116。局部SVG依赖同一输入原生对象，不能脱离输入恢复全稿；重导时先导入匹配哈希的输入，再覆盖本目录对应SVG、notes、images和page_plan，刷新摘要、运行roundtrip源门与导出。此次未启用native-charts-and-tables。

[SHA256SUMS](SHA256SUMS)覆盖本次修订资料和四份交付，路径相对仓库根目录，可在根目录执行sha256sum -c report/presentation/revisions/p7-p11-cover-20261116/SHA256SUMS。report/SHA256SUMS保留此前快照，未用它宣称当前用户报告或r1/r2修改已校验、已提交。存在任务外报告修改，按AGENTS.md本轮未自动提交/推送。分工与实例待用户填写，材料仍待审阅。
