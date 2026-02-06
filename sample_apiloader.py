from API_Side import CarPrice
from API_Side import CarOil
from module import CSVModule

instr = input("검색어 입력: ")
f_name = input("파일명 입력: ")

# 불러올 API를 선택

apidata = CarOil.getdata(instr)
# apidata = CarPrice.getdata(instr)

CSVModule.csv_export(f_name, apidata)


