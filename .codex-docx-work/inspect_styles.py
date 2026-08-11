from pathlib import Path
from zipfile import ZipFile
import hashlib

from docx import Document
from docx.oxml.ns import qn


source = Path(__file__).with_name("reference.docx")
document = Document(source)

for name in ("Normal", "Title", "Heading 1", "Heading 2"):
    style = document.styles[name]
    font = style.font
    paragraph = style.paragraph_format
    print(
        name,
        {
            "font": font.name,
            "size_pt": font.size.pt if font.size else None,
            "bold": font.bold,
            "color": str(font.color.rgb) if font.color and font.color.rgb else None,
            "alignment": str(paragraph.alignment),
            "space_before_pt": paragraph.space_before.pt if paragraph.space_before else None,
            "space_after_pt": paragraph.space_after.pt if paragraph.space_after else None,
            "line_spacing": paragraph.line_spacing,
            "left_indent_pt": paragraph.left_indent.pt if paragraph.left_indent else None,
            "first_line_indent_pt": paragraph.first_line_indent.pt if paragraph.first_line_indent else None,
        },
    )

for index in (1, 7, 11, 17, 25, 31, 32, 34, 39, 44, 48, 56, 60, 65, 66, 69, 75, 79, 80, 83, 85):
    table = document.tables[index]
    grid = table._tbl.tblGrid
    widths = [col.get(qn("w:w")) for col in grid.gridCol_lst] if grid is not None else []
    table_width_element = table._tbl.tblPr.find(qn("w:tblW"))
    table_width = table_width_element.get(qn("w:w")) if table_width_element is not None else None
    print(f"table={index} rows={len(table.rows)} cols={len(table.columns)} width={table_width} grid={widths}")

with ZipFile(source) as package:
    for info in package.infolist():
        data = package.read(info.filename)
        digest = hashlib.sha256(data).hexdigest()
        print(f"PART\t{info.filename}\t{len(data)}\t{digest}")
