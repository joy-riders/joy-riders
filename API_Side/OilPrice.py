import os
import xml.etree.ElementTree as ET
import urllib.request
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPINET_API_KEY')

def getdata(oil_type: str) -> float:
    global api_key

    # 키가 없는 경우 예외 처리
    if not api_key:
        print("오류: OPINET_API_KEY가 설정되지 않았습니다.")
        return -1.0

    url = f"https://www.opinet.co.kr/api/avgAllPrice.do?out=xml&code={api_key}"

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
