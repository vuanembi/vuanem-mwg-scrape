import json

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}


def get_root_page(session: requests.Session) -> BeautifulSoup:
    with session.get(
        "https://www.thegioididong.com/he-thong-sieu-thi-the-gioi-di-dong",
        headers=HEADERS,
    ) as r:
        return BeautifulSoup(r.content, "html.parser")


def get_root_data_value(soup: BeautifulSoup) -> list[dict]:
    return [
        {
            "province_id": i.get("data-value"),
            "province": i.get("href").replace("/sieu-thi-the-gioi-di-dong/", ""),
        }
        for i in soup.select(".scroll-box__store > ul > li > a")
    ]


def get_province_data(session: requests.Session, province_id: int) -> BeautifulSoup:
    with session.post(
        "https://www.thegioididong.com/Store/SuggestSearch",
        data={
            "provinceId": province_id,
            "districtId": 0,
            "pageIndex": 0,
            "pageSize": 1000,
            "loadAll": True,
            "type": -1,
        },
        headers=HEADERS,
    ) as r:
        return BeautifulSoup(r.content)


def get_location_data(soup: BeautifulSoup) -> list[dict]:
    els = soup.select("li > a:not([target])")
    return [
        {
            "href": el.get("href"),
            "text": el.get_text().strip(),
        }
        for el in els
    ]


if __name__ == "__main__":
    with requests.Session() as session:
        provinces = get_root_data_value(get_root_page(session))
        data = [
            get_location_data(get_province_data(session, province["province_id"]))
            for province in provinces
        ]
    data_with_province = [
        {**province, "data": data} for province, data in zip(provinces, data)
    ]
    with open("export/data.json", "w") as f:
        json.dump(data_with_province, f)
