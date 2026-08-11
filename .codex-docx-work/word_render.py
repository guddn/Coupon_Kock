from pathlib import Path
import sys


source = Path(sys.argv[1]).resolve()
target = Path(sys.argv[2]).resolve()
target.parent.mkdir(parents=True, exist_ok=True)

try:
    import win32com.client

    word = win32com.client.DispatchEx("Word.Application")
except ImportError:
    try:
        import comtypes.client

        word = comtypes.client.CreateObject("Word.Application")
    except ImportError as exc:
        raise SystemExit(f"Word COM libraries unavailable: {exc}")
word.Visible = False
word.DisplayAlerts = 0
document = None
try:
    document = word.Documents.Open(str(source), ReadOnly=True, AddToRecentFiles=False)
    page_count = document.ComputeStatistics(2)
    document.ExportAsFixedFormat(
        OutputFileName=str(target),
        ExportFormat=17,
        OpenAfterExport=False,
        OptimizeFor=0,
        Range=0,
        Item=0,
        IncludeDocProps=True,
        KeepIRM=True,
        CreateBookmarks=1,
        DocStructureTags=True,
        BitmapMissingFonts=True,
        UseISO19005_1=False,
    )
    print(f"pages={page_count} pdf={target}")
finally:
    if document is not None:
        document.Close(False)
    word.Quit()
