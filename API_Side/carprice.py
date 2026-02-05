import requests
from bs4 import BeautifulSoup as bsoup
from urllib.parse import quote

class APICarprice:
    def __init__(self):
        pass

    def priceparser(self, instr):
        a = 0
        b = 0
        varbuff = 0
        for k in instr:
            if k in "1234567890" or k == ",":
                if k != ",":
                    varbuff = varbuff * 10 + int(k)
            elif varbuff != 0:
                if a == 0:
                    a = varbuff
                    varbuff = 0
                else:
                    b = varbuff
                    break

        return (a, b)

    def getdata(self, model:str) -> list:
        query_string = quote(model)
        url = f"https://www.carisyou.com/search/?qt={query_string}&menu=%EC%9E%90%EB%8F%99%EC%B0%A8&section=&nh=10&st=1&adv=0&rf=%40date&delmyquery=&sDate=0&eDate=0&sw=1&salesSeCd=0"

        html = requests.get(url).text
        soup = bsoup(html, 'html.parser')
        search_result = soup.select_one(".list_body > table > tbody").select("tr")

        res = []
        for row in search_result:
            modelname = row.select_one("h4").text.strip()
            pl, lh = self.priceparser(row.select_one("td > p").text.strip().split("가격")[1])
            res.append((modelname, pl, lh))

        return res

apicarprice = APICarprice()
