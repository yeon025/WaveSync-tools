import json


def main():
    with open("resources/json/transform/resonator_stats.json", "r", encoding="utf-8") as f:
        resonators = json.load(f)

    resonators.sort(
        key=lambda x: (
            x["release version"],
            x["name"]
        )
    )

    with open(
        "resources/json/transform/resonator_stats.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            resonators,
            f,
            ensure_ascii=False,
            indent=4
        )

    print(f"{len(resonators)}개 정렬 완료")


if __name__ == "__main__":
    main()