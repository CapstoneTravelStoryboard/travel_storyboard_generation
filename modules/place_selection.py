import pandas as pd
from modules.utils import log_to_file

# CSV 파일에서 여행지 데이터를 불러오는 함수
def load_database(filename):
    return pd.read_csv(filename, encoding="cp949", header=None).values.tolist()

# 1. 시 단위의 도시 선택
def select_city(db, log_file):
    cities = list(set([place[0] for place in db]))  # 중복 없이 도시 목록을 가져옴
    print("도시를 선택하세요:")
    for idx, city in enumerate(cities):
        print(f"{idx + 1}. {city}")
    city_choice = int(input("도시 번호 입력: ")) - 1
    selected_city = cities[city_choice]
    
    # 입력 결과를 파일에 기록
    log_to_file(f"선택한 도시: {selected_city}", log_file)
    
    return selected_city

# 2. 선택된 도시에서 관광지 선택
def select_place(city, db, log_file):
    places_in_city = [place for place in db if place[0] == city]
    print(f"{city} 내에서 관광지를 선택하세요:")
    for idx, place in enumerate(places_in_city):
        print(f"{idx + 1}. {place[1]}")
    place_choice = int(input("관광지 번호 입력: ")) - 1
    selected_place = places_in_city[place_choice]
    
    # 입력 결과를 파일에 기록
    log_to_file(f"선택한 관광지: {selected_place[1]}", log_file)
    
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


# 4. DB에서 선택된 관광지의 테마 가져오기
def get_place_info(destination, db, log_file):
    for place in db:
        if place[1] == destination:
            info = {
                "city": place[0],
                "name": place[1],
                "description": place[2],
                "theme": place[3].split(", ")  # 문자열을 리스트로 변환
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