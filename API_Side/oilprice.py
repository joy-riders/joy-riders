import os
import xml.etree.ElementTree as ET
import urllib.request
from dotenv import load_dotenv

class ApiOil:
    def __init__(self):
        # 클래스 생성 시 내부에서 .env 파일을 로드하고 키를 가져옵니다.
        load_dotenv()
        self.api_key = os.getenv('OPINET_API_KEY')

    def getdata(self, oil_type: str) -> float:
        # 키가 없는 경우 예외 처리
        if not self.api_key:
            print("오류: OPINET_API_KEY가 설정되지 않았습니다.")
            return -1.0

        url = f"https://www.opinet.co.kr/api/avgAllPrice.do?out=xml&code={self.api_key}"

        try:
            with urllib.request.urlopen(url) as response:
                xml_data = response.read().decode("utf-8")

            root = ET.fromstring(xml_data)

            for oil in root.findall("OIL"):
                prod_name = oil.find("PRODNM").text
                price = oil.find("PRICE").text

                # API 응답 유종 명칭과 입력 유종 명칭 매칭
                if prod_name == oil_type:
                    return float(price)

        except Exception as e:
            print(f"API 호출 오류: {e}")

        return -1.0