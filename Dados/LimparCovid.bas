Attribute VB_Name = "LimparCovid"
Sub LimparBasedeDados()

    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    
    Dim i As Long
    i = 1
    
    Do Until Cells(i, 1) = Empty
        
    i = i + 1
    Loop

    Range("S1:S" & i).FormulaR1C1 = "=RC[-18] & "","" & RC[-17] & "","" & RC[-16] & "","" & TEXT(RC[-11],""aaaa-mm-dd"") & "","" & RC[-9] & "","" & RC[-8] & "","" & RC[-7] & "","" & RC[-6] & "","" & RC[-5]"

    Range("S1:S" & i) = Range("S1:S" & i).Value
    
    Columns("A:R").Select
    Selection.Delete Shift:=xlToLeft

    Range("A1").Select
    
    Application.ScreenUpdating = True
    Application.Calculation = xlCalculationAutomatic

End Sub
