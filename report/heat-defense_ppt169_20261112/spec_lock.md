<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## communication
- primary_language: zh-CN
- audience: 并行与分布式计算课程教师
- objective: 在5分钟解释算法、三种实现、真实验证与性能及AI核查，使教师理解归属/同步/基线/限制。
- core_message: 正确性有证据，并行收益有条件
- consumption_mode: presentation

## mode
- mode: custom
- mode_references: instructional
- mode_behavior: 先定义更新，再对照MPI/OpenMP分工同步，以正确性和性能证据收束。

## visual_style
- visual_style: custom
- visual_style_references: swiss-minimal
- visual_style_behavior: 参考两份本地模板：深蓝封面/结束页、白底正文与浅蓝分区、铜金强调；算法图占主体，主性能图用模板蓝/铜金，备份原图保留原色。

## colors
- background: #FFFFFF
- secondary_bg: #EDF3FA
- primary: #124C8D
- accent: #C38749
- secondary_accent: #477CB3
- body_text: #273848
- secondary_text: #627487
- divider: #CCD8E7
- on_blue_accent: #EDC188

## typography
- font_family: Microsoft YaHei, Arial
- title_family: Microsoft YaHei, Arial
- body_family: Microsoft YaHei, Arial
- body: 32
- title: 46
- cover: 64
- hero: 72
- subtitle: 36
- lead: 34
- annotation: 24
- footnote: 16

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
