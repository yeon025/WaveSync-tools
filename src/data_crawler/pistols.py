from util import crawl_weapon_stats, save_json


URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EB%AC%B4%EA%B8%B0/%EA%B6%8C%EC%B4%9D"
)

weapons = crawl_weapon_stats(URL)

save_json(weapons, "resources/json/pistols.json")

print(f"{len(weapons)}개 권총 저장 완료")
