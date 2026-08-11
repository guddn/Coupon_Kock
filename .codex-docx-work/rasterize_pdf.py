from pathlib import Path
import sys

import fitz


source = Path(sys.argv[1])
output_dir = Path(sys.argv[2])
output_dir.mkdir(parents=True, exist_ok=True)
document = fitz.open(source)
matrix = fitz.Matrix(1.5, 1.5)
for index, page in enumerate(document):
    pixmap = page.get_pixmap(matrix=matrix, alpha=False)
    pixmap.save(output_dir / f"page-{index + 1}.png")
print(f"pages={len(document)} output={output_dir}")
