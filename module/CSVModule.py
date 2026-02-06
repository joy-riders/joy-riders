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


def csv_import(file_path: str) -> list[tuple]:
    """ CSV 파일을 읽어 튜플 리스트로 반환하는 함수 """
    data = []  # 데이터를 담을 빈 리스트 준비
    try:
        with open(file_path, 'r', encoding='utf-8') as f:  # 파일을 '읽기(r)' 모드로 열기
            # csv.reader를 사용하면 쉼표 분리나 따옴표 처리 자동
            reader = csv.reader(f)  # csv 전용 도구로 파일 내용을 한 줄씩 읽기
            for row in reader:  # 읽어온 내용을 한 줄(row)씩 반복
                if row:  # 만약 빈 줄이 아니라면 (데이터가 들어있다면)
                    # 각 칸의 앞뒤 공백 제거
                    clean_row = tuple(item.strip() for item in row)
                    data.append(clean_row)  # [값1, 값2] 형태의 리스트를 (값1, 값2) 튜플로 바꿔서 보관
    except FileNotFoundError:  # 파일이 없으면 에러
        print(f"파일을 찾을 수 없습니다: {file_path}")
    return data


