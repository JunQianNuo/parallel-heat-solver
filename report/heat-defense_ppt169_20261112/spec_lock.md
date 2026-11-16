<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## communication
- primary_language: zh-CN
- audience: 并行与分布式计算课程教师
- objective: 面向只能接触PPT和最终报告的课程教师，按模型、均匀网格、显式差分、串行与并行实现、主要测试结果说明算法和分工及通信同步，并完整解释比较条件和AI修正实例，不依赖仓库或实验专属报告。
- core_message: 正确性有证据，并行收益有条件
- consumption_mode: presentation

## mode
- mode: custom
- mode_references: instructional
- mode_behavior: 从薄板及条件进入，沿均匀网格、五点读写、串行完整推进、MPI连续分块和OpenMP交错分行逐步建立理解，再给出两类验证、固定规模及扩大工作量结果和AI实例。

## visual_style
- visual_style: custom
- visual_style_behavior: 仿照指定去雾PDF的深色章节导航、蓝色通栏白字标题、白底黑字楷体正文与蓝色黑体强调、双条页脚；单页一个主题，少量图文；标题使用简短主题名，结果及判断放正文。

## colors
- background: #FFFFFF
- primary: #115EA2
- navigation: #092F51
- footer_lower: #0B3D69
- inactive: #8497A8
- secondary_text: #8497A8
- body_text: #000000
- divider: #C9D7E3

## typography
- font_family: KaiTi, Arial
- body_family: KaiTi, Arial
- title_family: SimHei, Arial
- cover_family: SimHei, Arial
- lead_family: SimHei, Arial
- navigation_family: SimHei, Arial
- footnote_family: SimHei, Arial
- data_family: Arial
- body: 40
- title: 44
- cover: 58
- lead: 40
- annotation: 30
- navigation: 20
- footnote: 20
- data: 30
- diagram: 36
- compact_lead: 34
- math_script: 22

## icons
- library: none
- inventory: none

## page_rhythm
- P01: anchor
- P02: breathing
- P03: dense
- P04: breathing
- P05: dense
- P06: dense
- P07: dense
- P08: dense
- P09: dense
- P10: anchor
- P11: dense
- P12: dense
- P13: dense
- P14: dense

## page_visualizations
- P07: table/record_table
- P08: chart/line_chart
- P09: table/metric_table
- P11: table/comparison_matrix
- P12: chart/line_chart
- P13: chart/line_chart

## images
- full-strong: images/02-speedup.png | source=user | crop=no-crop
- full-grid: images/05-grid-speedup.png | source=user | crop=no-crop

## pptx_structure
- mode: flat

## forbidden
- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`
- HTML named entities in text; write typography as raw Unicode and escape XML reserved characters
- 请不要出现实验专属的报告 (user)
