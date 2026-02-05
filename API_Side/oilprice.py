import xml.etree.ElementTree as ET
import urllib.request


class ApiOil:
    def __init__(self, api_key: str):
        # 클래스 생성 시 API 키를 저장합니다.
        self.api_key = api_key

    def getdata(self, oil_type: str) -> float:
        # URL 뒤에 API 키(code)를 붙여줍니다.
        url = f"https://www.opinet.co.kr/api/avgAllPrice.do?out=xml&code={self.api_key}"

        try:
            # 1. 오피넷 API 호출
            with urllib.request.urlopen(url) as response:
                xml_data = response.read().decode("utf-8")

            # 2. XML 데이터 파싱
            root = ET.fromstring(xml_data)

            # 3. 유종 이름으로 가격 찾기
            for oil in root.findall("OIL"):
                prod_name = oil.find("PRODNM").text
                price = oil.find("PRICE").text

                if prod_name == oil_type:
                    return float(price)

        except Exception as e:
            print(f"API 호출 오류: {e}")

        return -1.0