import os
from score_evaluate import extract_match_info

def score_breakdown(info):
    # 예상 평균 레벨
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

    # 여자 플래버 안내문
    if info["female"] == 0:
        female_notice = "여자 플래버가 없는 매치입니다!"
    else:
        female_notice = f"여자 플래버가 {info['female']}명 참여하는 매치입니다!"

    # 최종 점수 (여자 플래버 3명 이상은 0점)
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
    return {
        "level_score": level_score,
        "team_score": team_score,
        "field_score": field_score,
        "pom_score": pom_score,
        "price_score": price_score,
        "total_score": total_score,
        "female_notice": female_notice
    }

def rank_matches_in_folder(folder_path):
    results = []
    all_info = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".html"):
            full_path = os.path.join(folder_path, filename)
            info = extract_match_info(full_path)
            breakdown = score_breakdown(info)
            results.append((filename, breakdown["total_score"]))
            all_info.append((filename, breakdown, info))

    # score 기준 내림차순 정렬, 동점시 파일명 알파벳순
    results.sort(key=lambda x: (-x[1], x[0]))

    # 상위 3개만 뽑기 (동점 포함)
    top3 = results[:3]
    print("\n=== 상위 1, 2, 3등 매치 상세 ===")
    for rank, (filename, score) in enumerate(top3, 1):
        # 파일명에 해당하는 breakdown 정보 찾기
        bd = [x for x in all_info if x[0] == filename][0][1]
        print(f"\n{rank}등: {filename} (총 score: {bd['total_score']:.1f})")
        print(f"  - 예상 평균 레벨 점수 : {bd['level_score']}")
        print(f"  - 팀 구성 점수       : {bd['team_score']}")
        print(f"  - 구장 크기 점수     : {bd['field_score']}")
        print(f"  - POM 점수          : {bd['pom_score']:.1f}")
        print(f"  - 금액 점수         : {bd['price_score']}")
        print(f"  - {bd['female_notice']}")

if __name__ == "__main__":
    folder = input("매치 html이 담긴 폴더 경로를 입력하세요: ").strip()
    rank_matches_in_folder(folder)
