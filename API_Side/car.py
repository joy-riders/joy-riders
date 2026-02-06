import os
from dotenv import load_dotenv

class ApiCar:
    def __init__(self):
        load_dotenv()
        self.CAR_ID = os.getenv('CAR_ID')

    def getdata(self, model_name:str) -> list:
        # print(CAR_ID)
        if not self.CAR_ID:
            raise ValueError('CAR_ID 없음')

        import requests

        url = 'https://apis.data.go.kr/B553530/CAREFF/CAREFF_LIST?serviceKey=e2662a6ac375d47f49a02db9e44f8e6abc87244fd2176a548fe453f1ec448f6d&pageNo=1&numOfRows=20&apiType=json'

        headers = {
            'CAR_ID': self.CAR_ID
        }

        params = {
            'pageNo': 1,
            'numOfRows': 1000,
            'q2': model_name,
            # 'q4': str(input('연식을 입력하세요'))
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            try:
                data_item = data["response"]["body"]["items"]["item"]
                if isinstance(data_item, dict):
                    data_item = [data_item]
            except (KeyError, TypeError):
                return []  
            keys = [
                "MODEL_NM",
                "COMP_NM",
                "FUEL_NM",
                "DISPLAY_EFF",
                "URBAN_EFF",
                "HIGHWAY_EFF",
                "RANGE_PER_CHARGE",
                "ESTIMATED_FUEL_COST",
                "GRADE",
                "ENGINE_DISPLACEMENT",
            ]

            res = []
            for item in data_item:
                buff = []
                for key in keys:
                    buff.append(item[key])
                res.append(tuple(buff))
        else:
            print("Error Code:" + response.status_code)
        return res

apicar = ApiCar()
