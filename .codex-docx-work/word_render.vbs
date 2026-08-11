Option Explicit

Dim sourcePath, outputPath, wordApp, doc, pageCount
sourcePath = CreateObject("Scripting.FileSystemObject").GetAbsolutePathName(WScript.Arguments(0))
outputPath = CreateObject("Scripting.FileSystemObject").GetAbsolutePathName(WScript.Arguments(1))

Set wordApp = CreateObject("Word.Application")
wordApp.Visible = False
wordApp.DisplayAlerts = 0
Set doc = wordApp.Documents.Open(sourcePath, False, True, False)
pageCount = doc.ComputeStatistics(2)
doc.ExportAsFixedFormat outputPath, 17, False, 0, 0, 1, 1, 0, True, True, 1, True, True, False
WScript.Echo "pages=" & pageCount & " pdf=" & outputPath
doc.Close False
wordApp.Quit
