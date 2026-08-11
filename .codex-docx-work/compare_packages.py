from pathlib import Path
from zipfile import ZipFile
import hashlib
import sys


reference = Path(sys.argv[1])
final = Path(sys.argv[2])
editable = {"word/document.xml", "word/media/image1.png", "word/media/image2.png"}


def inventory(path: Path) -> dict[str, tuple[int, str]]:
    with ZipFile(path) as package:
        return {
            info.filename: (len(data := package.read(info.filename)), hashlib.sha256(data).hexdigest())
            for info in package.infolist()
        }


before = inventory(reference)
after = inventory(final)
if before.keys() != after.keys():
    print("PACKAGE PART SET CHANGED")
    print("missing", sorted(before.keys() - after.keys()))
    print("added", sorted(after.keys() - before.keys()))
    raise SystemExit(1)

changed = {name for name in before if before[name] != after[name]}
unexpected = changed - editable
print("changed", sorted(changed))
print("unexpected", sorted(unexpected))
if unexpected:
    raise SystemExit(1)
