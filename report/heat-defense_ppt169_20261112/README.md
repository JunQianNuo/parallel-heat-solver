# heat-defense

- Canvas format: ppt169
- Created: 20261112

## Directories

- `svg_output/`: raw SVG output
- `svg_final/`: self-contained SVG visual preview; may be inserted manually as an SVG image, but PowerPoint Convert to Shape is unsupported
- `images/`: runtime image pool; converter assets keep their original short filenames when possible
- `icons/`: project icon set — selected library icons copied in (via icon_sync.py) plus any custom icons you add; embedded from here at export
- `notes/`: speaker notes
- `templates/`: project templates
- `live_preview/`: browser preview runtime files and history (lock.json, server.log, edits.jsonl, annotations.jsonl)
- `sources/`: source materials and normalized markdown
- `analysis/`: machine-extracted intermediate analysis (PPTX intake, image_analysis.csv) — the pipeline's canonical must-read source/asset facts
- `validation/`: cold workflow audit log, SVG quality reports, and PPTX postflight audit reports
- `exports/`: final native DrawingML pptx deliverables only (timestamped); `_native_charts_tables.pptx` name with `--native-charts-and-tables`, `_narrated.pptx` name when narration audio is embedded
- `backup/<timestamp>/`: svg_output/ archive (always written in default-flow mode; safe to delete old timestamps)

## 当前状态

2026-11-15起优先完成书面报告，本工作区暂停制作。源文件保留原位置，浏览器运行目录不迁移。最近既有成品为[可编辑v4-r1](../presentation/current/presentation-v4-r1.pptx)及[PDF](../presentation/current/presentation-v4-r1.pdf)，版本与工具入口见[归档说明](../presentation/README.md)。本轮只修复移动文件的链接，没有改页面、公式、图表、备注或重新导出。模板与字体仅本地只读，不纳入Git。
