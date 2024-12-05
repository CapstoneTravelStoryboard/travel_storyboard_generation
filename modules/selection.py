import pandas as pd
from collections import OrderedDict
from datetime import datetime

# xlsx 파일에서 여행지 데이터를 불러오는 함수
def load_database(filename, sheet_name=0):
    return pd.read_excel(filename, sheet_name=sheet_name, header=0).values.tolist()

# 여행날짜를 이용하여 국내 계절 분류
def input_departure_and_arrival_dates_with_season():
    """
    사용자가 여행의 출발 날짜와 도착 날짜를 입력하도록 하고,
    여행 날짜에 맞는 계절을 반환합니다.
    """
    def get_season(date):
        """
        주어진 날짜에 해당하는 계절을 반환합니다.
        """
        month = date.month
        if 3 <= month <= 5:
            return "봄(Spring)"
        elif 6 <= month <= 8:
            return "여름(Summer)"
        elif 9 <= month <= 11:
            return "가을(Autumn)"
        else:
            return "겨울(Winter)"

    while True:
        try:
            departure_date_str = input("출발 날짜를 입력하세요 (YYYY-MM-DD): ")
            arrival_date_str = input("도착 날짜를 입력하세요 (YYYY-MM-DD): ")
            
            # 입력된 날짜를 datetime 객체로 변환
            departure_date = datetime.strptime(departure_date_str, "%Y-%m-%d")
            arrival_date = datetime.strptime(arrival_date_str, "%Y-%m-%d")

            # 출발 날짜가 도착 날짜보다 늦으면 오류 출력
            if departure_date > arrival_date:
                print("출발 날짜는 도착 날짜보다 빨라야 합니다. 다시 입력해주세요.")
                continue

            # 계절 판별
            departure_season = get_season(departure_date)
            arrival_season = get_season(arrival_date)

            # 동일한 계절인지 확인
            if departure_season == arrival_season:
                season = departure_season
            else:
                season = f"{departure_season}에서 {arrival_season}까지"
            
            return departure_date_str, arrival_date_str, season
        except ValueError:
            print("날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력해주세요.")
            continue

# 1. 시/도와 구/군을 선택하는 함수
def select_city_and_district(db):
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
    
    return selected_city, selected_district


# 2. 선택된 시/도와 구/군에서 관광지 선택
def select_place(city, district, db):
    # 선택된 시/도와 구/군에 속하는 관광지 목록 필터링
    places_in_city_and_district = [place for place in db if place[0] == city and place[1] == district]

    if not places_in_city_and_district:
        print(f"{city}의 {district}에는 관광지가 없습니다.")
        return None

    print(f"\n{city}의 {district} 내에서 관광지를 선택하세요:")
    for idx, place in enumerate(places_in_city_and_district):
        print(f"{idx + 1}. {place[2]}")  # 관광지 이름 출력
    place_choice = int(input("관광지 번호 입력: ")) - 1
    selected_place = places_in_city_and_district[place_choice]

    return selected_place

# 3. 동행인 입력 (친구, 가족, 연인, 혼자, 반려동물)과 인원수 입력
def input_companion():
    companions = ["친구", "가족", "연인", "혼자", "반려동물"]
    print("동행인을 선택하세요:")
    for idx, companion in enumerate(companions):
        print(f"{idx + 1}. {companion}")
    
    companion_choice = companions[int(input("동행인 번호 입력: ")) - 1]
    
    if companion_choice == "혼자":
        companion_count = 0
    elif companion_choice == "연인":
        companion_count = 2
    elif companion_choice == "반려동물":
        companion_count = int(input("반려동물 수를 입력하세요: "))
    else:
        companion_count = int(input("인원 수를 입력하세요: "))
    
    
    return companion_choice, companion_count


# 4. DB에서 선택된 관광지의 정보를 가져오기
def get_place_info(destination, db):
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
            return info
    return None


# 5. 여행지에 등록된 테마 선택
def select_theme(theme):
    print("여행 목적을 선택하세요:")
    for idx, t in enumerate(theme):
        print(f"{idx + 1}. {t}")
    theme_choice = int(input("여행 목적 번호 입력: ")) - 1
    selected_theme = theme[theme_choice]
    
    return selected_theme