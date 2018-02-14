import openpyxl as xls

xlsxFile = "/Users/guoyapeng/Downloads/t28libSyn.xlsx"
wb = xls.load_workbook(filename=xlsxFile)
sheet1 = wb["t28svt"]
print(sheet1['C4'].value)
sheet1['A1'].value = 0

wb.save(filename="/Users/guoyapeng/Downloads/t28libSyn1.xlsx")

