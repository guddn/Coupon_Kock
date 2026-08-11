# Template execution contract

## Reference

- Original retained reference: `D:/대학강의/2026 AI 부트캠프/Part 1/AJOU_PBL_1차_MVP_프로젝트_통합_제출양식(배포)_update.docx` (Unicode decomposition preserved on disk).
- Task-local byte copy: `D:/development/Github/_AJOU_class/2026-1_AI_Bootcamp/Coupon_Kock/.codex-docx-work/reference.docx`.
- SHA-256: `b4ac44221b73d3110ae559eac4b9093f1124013e7e5f62670aa152926243aa84`.
- Render evidence: Microsoft Word hidden export to `reference-render/reference-word.pdf`; 29 pages; 29 PNG pages at 120 DPI. LibreOffice was not installed.
- Evidence: `template_inventory.txt`, `template-style-evidence.json`, `style_and_package_inventory.txt`.

## Page system

- One A4 portrait section, 8.27 x 11.69 inches.
- Margins: left/right/top 0.71 inches, bottom 0.67 inches.
- Header/footer are unlinked; different-first-page is enabled. Header distance and footer distance remain source-controlled.
- One PAGE field in `word/footer1.xml`; no TOC fields.
- Source pagination is 29 pages. Content expansion is permitted because this is a fillable integrated report, but section geometry, header, footer, and PAGE field must remain unchanged.

## Typography and components

- Retain embedded source fonts and theme. Do not add a generic design preset.
- Title: 28 pt, bold, `#17365D`, 8 pt after, single line spacing.
- Heading 1: 17 pt, bold, `#2E74B5`, 18 pt before, 10 pt after.
- Heading 2: 13.5 pt, bold, `#2E74B5`, 14 pt before, 7 pt after.
- Body/callout fonts, paragraph rhythm, blue-gray section labels, table fills/borders, header `PBL | 1차 MVP 프로젝트`, and footer PAGE field are preserve-only.
- Two source inline images are editable because they describe the system architecture and agent flow. Keep their existing relationships and displayed sizes; replace only the PNG payloads.

## Tables and geometry

- 87 top-level tables. Standard table width is 9866 DXA. Existing `tblGrid`, cell widths, fills, borders, and cell margins remain source-controlled.
- Header rows and all existing row properties remain. New API rows in table 32 may clone its final body row so geometry and formatting stay source-derived.
- Narrative cells may grow vertically. No fixed row height will be introduced.

## Content flow and slot map

- Preserve instructional/section-callout tables: 0, 2-5, 9, 14, 19, 24, 29, 33, 38, 43, 47, 51, 55, 59, 64, 68, 73, 78, 82, 86.
- Fill or update project slots: tables 1, 6-8, 10-13, 15-18, 20-23, 25-28, 30-32, 34-37, 39-42, 44-46, 48-50, 52-54, 56-58, 60-63, 65-67, 69-72, 74-77, 79-81, 83-85.
- Cover paragraphs and section headings remain unchanged.
- Stable locators are `word/document.xml` top-level table index + row index + cell index. Existing cell paragraph/run properties are preserved while visible text nodes are replaced.
- Unknown personal facts are not invented: author uses the prefilled name 김형우; formal multi-user testing, presentation file, and video are marked not yet completed/attached.
- Implemented and planned scope must be separated: manual coupon registration, GPS, maps, public-data nearby query, Firestore, deterministic calculator, ADK tool trace, Cloud Run/Firebase are implemented; image OCR, production RAG/vector retrieval, user card/telecom profile, background geofencing/push are partial or planned.

## Package preservation

- Editable parts: `word/document.xml`, `word/media/image1.png`, `word/media/image2.png`, and core metadata only if required.
- Preserve-only: content types, all relationships, footnotes/endnotes, header/footer, fonts, theme, settings, customXml, numbering, styles, web settings, font table, and app properties.
- Baseline size/hash inventory is in `style_and_package_inventory.txt`. Final audit must confirm all preserve-only parts are byte-identical.

## Fidelity gates

- Original retained reference and task-local reference must keep the recorded SHA-256.
- Section count, A4 geometry, header/footer, PAGE field, styles, numbering, table grids, relationships, and embedded fonts must remain.
- No placeholder tokens such as `[여기에 작성]`, `[URL]`, `[이름]`, `[실제]`, or `[YYYY-MM-DD]` may remain in editable slots; unchecked checklist items may be represented as `[미완]` with a reason.
- Every final page must be exported by Word and inspected from PNGs. Fail on clipping, overlap, broken table borders, unreadable Korean glyphs, unexplained pagination, or stale architecture diagrams.
