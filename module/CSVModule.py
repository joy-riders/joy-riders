import csv

def csv_import(csv_name: str) -> list[tuple]:
    car_data = []
    with open(csv_name, 'r', encoding='utf-8') as f:
        read = csv.reader(f)
        for row in read:
            car_data.append(tuple(row))
    return car_data


def csv_export(file_name: str, indata: list[tuple]):
    with open(file_name, 'w', encoding='UTF8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(indata)


def csv_merge(file_path1: str, file_path2: str) -> list[tuple]:
    data = []  # 데이터를 담을 빈 리스트 준비
    try:
        l1 = csv_import(file_path1)
        l2 = csv_import(file_path2)

        for row in l1:
            data.append(row)

        for row2 in l2:
            flag = False
            for row1 in l1:
                if row1[0] == row2[0]:
                    flag = True

            if not flag:
                data.append(row2)

    except FileNotFoundError:  # 파일이 없으면 에러
        print(f"파일을 찾을 수 없습니다")
    return data


