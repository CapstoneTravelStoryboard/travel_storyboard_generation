import pandas as pd
from collections import OrderedDict

from modules.utils import log_to_file

# CSV 파일에서 여행지 데이터를 불러오는 함수
def load_database(filename):
    return pd.read_csv(filename, encoding="utf-8-sig", header=None, skiprows=1).values.tolist()

# 1. 시/도와 구/군을 선택하는 함수
def select_city_and_district(db, log_file):
    # 시/도와 구/군을 중복 없이 가져오기
    cities = OrderedDict()
    for place in db:
        city, district = place[0], place[1]
        if city not in cities:
            cities[city] = []
        if district not in cities[city]:
            cities[city].append(district)

    # 시/도 선택
    print("시/도를 선택하세요:")
    for idx, city in enumerate(cities):
        print(f"{idx + 1}. {city}")
    city_choice = int(input("시/도 번호 입력: ")) - 1
    selected_city = list(cities.keys())[city_choice]
    
    # 선택한 시/도의 구/군 선택
    print(f"\n{selected_city}의 구/군을 선택하세요:")
    districts = cities[selected_city]
    for idx, district in enumerate(districts):
        print(f"{idx + 1}. {district}")
    district_choice = int(input("구/군 번호 입력: ")) - 1
    selected_district = districts[district_choice]
    
    # 선택 결과를 로그 파일에 기록
    log_to_file(f"선택한 시/도: {selected_city}", log_file)
    log_to_file(f"선택한 구/군: {selected_district}", log_file)
    
    return selected_city, selected_district


# 2. 선택된 시/도와 구/군에서 관광지 선택
def select_place(city, district, db, log_file):
    # 선택된 시/도와 구/군에 속하는 관광지 목록 필터링
    places_in_city_and_district = [place for place in db if place[0] == city and place[1] == district]

    if not places_in_city_and_district:
        print(f"{city}의 {district}에는 관광지가 없습니다.")
        log_to_file(f"{city}의 {district}에는 관광지가 없습니다.", log_file)
        return None

    print(f"\n{city}의 {district} 내에서 관광지를 선택하세요:")
    for idx, place in enumerate(places_in_city_and_district):
        print(f"{idx + 1}. {place[2]}")  # 관광지 이름 출력
    place_choice = int(input("관광지 번호 입력: ")) - 1
    selected_place = places_in_city_and_district[place_choice]

    # 선택한 관광지를 로그 파일에 기록
    log_to_file(f"선택한 관광지: {selected_place[2]}", log_file)

    return selected_place

# 3. 동행인 입력 (친구, 가족, 연인, 혼자, 반려동물)과 인원수 입력
def input_companion(log_file):
    companions = ["친구", "가족", "연인", "혼자", "반려동물"]
    print("동행인을 선택하세요:")
    for idx, companion in enumerate(companions):
        print(f"{idx + 1}. {companion}")
    
    companion_choice = companions[int(input("동행인 번호 입력: ")) - 1]
    
    if companion_choice == "혼자":
        companion_count = 0
    elif companion_choice == "반려동물":
        companion_count = int(input("반려동물 수를 입력하세요: "))
    else:
        companion_count = int(input("동행인 수를 입력하세요: "))
    
    # 입력 결과를 파일에 기록
    log_to_file(f"동행인: {companion_choice}, 인원 수: {companion_count}", log_file)
    
    return companion_choice, companion_count


# 4. DB에서 선택된 관광지의 정보를 가져오기
def get_place_info(destination, db, log_file):
    for place in db:
        # 관광지 이름과 일치하는지를 확인
        if place[2] == destination:
            info = {
                "city": place[0],        # 시/도
                "district": place[1],    # 구/군
                "name": place[2],        # 관광지 이름
                "description": place[3], # 특성
                "theme": place[4].split(", ")  # 문자열을 리스트로 변환
            }
            # 입력 결과를 파일에 기록
            log_to_file(f"관광지 정보: {info}", log_file)
            return info
    return None


# 5. 여행지에 등록된 테마 선택
def select_theme(theme, log_file):
    print("여행 목적을 선택하세요:")
    for idx, t in enumerate(theme):
        print(f"{idx + 1}. {t}")
    theme_choice = int(input("여행 목적 번호 입력: ")) - 1
    selected_theme = theme[theme_choice]
    
    # 입력 결과를 파일에 기록
    log_to_file(f"선택한 여행 목적: {selected_theme}\n", log_file)
    
    return selected_theme