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

2026-11-16，用户批准新规范并要求面向只接触PPT和最终报告的非实现者，已完成14页v5：10正文＋4备份、280秒预算。当前成品为[可编辑PPTX](../presentation/current/presentation-v5.pptx)、[PDF](../presentation/current/presentation-v5.pdf)及[总览](../presentation/current/presentation-v5-contact.png)，逐页源与备注已同步，版本及核查入口见[材料说明](../presentation/README.md)。2026-11-15暂停制作的状态属于历史；旧成品保留，不能混用页码和检查。模板与字体仅本地只读，不纳入Git；用户材料验收、个人信息和真实计时演练仍待完成。
