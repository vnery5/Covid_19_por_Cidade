Attribute VB_Name = "LimparCovid"
Sub limpar()

Application.ScreenUpdating = False
Application.Calculation = xlCalculationManual

Dim i As Long
i = 1

Do Until Cells(i, 8) = Empty

 Range("R" & i).Select
            ActiveCell.FormulaR1C1 = "=RC[-17] & "","" & RC[-16] & "","" & RC[-15] & "","" & RC[-10] & "","" & RC[-8] & "","" & RC[-7] & "","" & RC[-5]"
    
i = i + 1
Loop

    Range("R1:R" & i).Select
    Range(Selection, Selection.End(xlDown)).Select
    Selection.Copy
    Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False
    Application.CutCopyMode = False
    
    Columns("A:Q").Select
    Selection.Delete Shift:=xlToLeft

Range("A1").Select

Application.ScreenUpdating = True
Application.Calculation = xlCalculationAutomatic

End Sub
