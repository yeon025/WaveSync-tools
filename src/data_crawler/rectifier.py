from util import crawl_weapon_stats, save_json


URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EB%AC%B4%EA%B8%B0/%EC%A6%9D%ED%8F%AD%EA%B8%B0"
)

weapons = crawl_weapon_stats(URL)

save_json(weapons, "resources/json/rectifier.json")

print(f"{len(weapons)}개 증폭기 저장 완료")
