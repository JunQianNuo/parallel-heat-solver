<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## communication
- primary_language: zh-CN
- audience: 并行与分布式计算课程教师
- objective: 在5分钟沿算法依赖、代码划分同步、两类误差及真实性能证据解释三实现，使教师能追问基线/计时/S/E和Amdahl/Gustafson适用边界，并披露AI核查。
- core_message: 正确性有证据，并行收益有条件
- consumption_mode: presentation

## mode
- mode: custom
- mode_references: instructional
- mode_behavior: 同一问题→懂算法→懂MPI/OpenMP代码→懂两类验证→懂基线/计时/S/E→两个定律与真实结论边界。

## visual_style
- visual_style: custom
- visual_style_behavior: 仿照指定去雾PDF的深色章节导航、蓝色通栏白字标题、白底黑字楷体正文与蓝色黑体强调、双条页脚；单页一个主题，少量图文；标题使用简短主题名，结果及判断放正文。

## colors
- background: #FFFFFF
- primary: #115EA2
- navigation: #092F51
- footer_lower: #0B3D69
- inactive: #8497A8
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
- P02: dense
- P03: dense
- P04: dense
- P05: dense
- P06: dense
- P07: dense
- P08: anchor
- P09: dense
- P10: dense
- P11: dense
- P12: dense

## images
- full-strong: images/02-speedup.png | source=user | crop=no-crop
- full-grid: images/05-grid-speedup.png | source=user | crop=no-crop

## pptx_structure
- mode: flat

## forbidden
- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`
- HTML named entities in text; write typography as raw Unicode and escape XML reserved characters
