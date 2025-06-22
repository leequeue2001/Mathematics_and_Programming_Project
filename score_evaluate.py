from bs4 import BeautifulSoup
import re
import sys

def extract_match_info(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    text = soup.get_text(separator="\n")

    # 1. 예상 평균 레벨
    match = re.search(r"예상 평균 레벨은\s*(아마추어[1-5])\s*입니다", text)
    level = match.group(1) if match else None

    # 2. 팀 구성 (6vs6)
    match = re.search(r"(\d+)vs(\d+)", text)
    team_format = match.group(0) if match else None

    # 3. 구장 크기 (40x18m)
    match = re.search(r"(\d+)\s*[x×]\s*(\d+)\s*m", text)
    if match:
        w = int(match.group(1))
        h = int(match.group(2))
        field_size = (w, h)
    else:
        field_size = None

    # 4. 금액
    match = re.search(r"(\d{1,3},?\d{3})원", text)
    price = int(match.group(1).replace(",", "")) if match else None

    # 5. POM (자동 추출)
    match = re.search(r"POM이\s*(\d+)명", text)
    pom_count = int(match.group(1)) if match else 0

    # 6. 여자 플래버
    match = re.search(r"여자 플래버\s*(\d+)명|여자 플래버\s*(\d+)명이 신청했어요", text)
    if match:
        female = match.group(1) if match.group(1) else match.group(2)
        female = int(female)
    elif "여자 플래버 1명이 신청했어요" in text:
        female = 1
    else:
        female = 0

    return {
        "level": level,
        "team_format": team_format,
        "field_size": field_size,
        "price": price,
        "pom_count": pom_count,
        "female": female,
        "text": text
    }

def calculate_score(info):
    # 예상 평균 레벨 (점수 변경)
    if info["level"] == "아마추어3":
        level_score = 10
    elif info["level"] in ["아마추어2", "아마추어4"]:
        level_score = 9
    elif info["level"] in ["아마추어1", "아마추어5"]:
        level_score = 7
    else:
        level_score = 4

    # 팀 구성
    if info["team_format"] == "6vs6":
        team_score = 5
    elif info["team_format"] == "5vs5":
        team_score = 3
    else:
        team_score = 1

    # 구장 크기
    if info["field_size"]:
        area = info["field_size"][0] * info["field_size"][1]
        if area >= 800:
            field_score = 5
        elif area >= 750:
            field_score = 4
        elif area >= 700:
            field_score = 3
        else:
            field_score = 2
    else:
        field_score = 0

    # POM
    pom_score = info["pom_count"] * 0.2

    # 금액
    if info["price"] == 10000:
        price_score = 2
    elif info["price"] == 11000:
        price_score = 1
    else:
        price_score = 0

    # 여자 플래버 안내 및 score 처리
    if info["female"] == 0:
        female_notice = "여자 플래버가 없는 매치입니다!"
    else:
        female_notice = f"여자 플래버가 {info['female']}명 참여하는 매치입니다!"

    print("\n---- 항목별 점수 ----")
    print(f"예상 평균 레벨 점수       : {level_score}")
    print(f"팀 구성(6vs6 등) 점수     : {team_score}")
    print(f"구장 크기 점수            : {field_score}")
    print(f"POM 점수                 : {pom_score:.1f}")
    print(f"금액 점수                 : {price_score}")

    # 여자 플래버 3명 이상이면 score는 0점!
    if info["female"] >= 3:
        total_score = 0
    else:
        total_score = (
            level_score +
            team_score +
            field_score +
            pom_score +
            price_score
        )
    print(f"\n최종 score: {total_score}")

    print(f"\n{female_notice}")

    return total_score

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python 파일이름.py [html파일명]")
    else:
        html_path = sys.argv[1]
        info = extract_match_info(html_path)
        calculate_score(info)
