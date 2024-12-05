import os
from datetime import datetime
from modules.cloud_storage import upload_image_to_cloud
from modules.gpt_integration import gpt_select_title, gpt_select_intro_outro
from modules.image_generation import generate_and_save_image_dalle
from modules.selection import load_database, select_city_and_district, select_place, input_companion, get_place_info, select_theme, input_departure_and_arrival_dates_with_season
from modules.storyboard import gpt_generate_storyboard, parse_storyboard
from modules.utils import get_image_urls, save_to_excel
from modules.technique_keyword_extractor import extract_keywords_with_rag

# 메인 함수
def main(): 
    # 여행지 정보 데이터베이스 
    db = load_database("C:/Users/KimTY/CapstoneDesign/travel_storyboard_generation/data/travel_database.xlsx")

    # 여행 날짜 선택
    departure_date, arrival_date, season = input_departure_and_arrival_dates_with_season()
    print(f"출발 날짜: {departure_date}, 도착 날짜: {arrival_date}, 계절: {season}")    

    # 시/도와 구/군 선택
    selected_city, selected_district = select_city_and_district(db)

    # 선택된 시/도와 구/군에서 관광지 선택
    place = select_place(selected_city, selected_district, db)
    companion, companion_count = input_companion()
    
    # 선택된 관광지 정보 가져오기
    place_info = get_place_info(place[2], db)
    print(place_info)
    if not place_info:
        print("관광지 정보를 찾을 수 없습니다.")
        return
    
    # 테마 선택 및 로그 기록
    selected_theme = select_theme(place_info["theme"])
    
    # GPT를 이용해 제목 추천 (동행인 수 포함)
    selected_title = gpt_select_title(place_info["name"], selected_theme, companion, companion_count, season, place_info["description"])
    
    # GPT를 이용해 인트로와 아웃트로 추천
    selected_intro, selected_outro = gpt_select_intro_outro(selected_title)
    
    # 관광지의 외관과 주변 환경을 제공할 이미지 URL 수집
    image_directory = "C:/Users/KimTY/CapstoneDesign/travel_storyboard_generation/data_labeling/images"
    image_urls = get_image_urls(image_directory, place)

    # 이미지 디렉토리에서 특정 확장자의 이미지를 클라우드(S3)에 업로드하고, 해당 URL을 리스트에 추가
    for img in os.listdir(image_directory):
        if img.endswith(('.png', '.jpg', '.jpeg')):
            image_path = f"{image_directory}/{img}"
            bucket_name = 'capstonestoryboard'
            s3_file_name = f"images/{place[0]}/{place[1]}/{img}"
            cloud_image_url = upload_image_to_cloud(image_path, bucket_name, s3_file_name) # 클라우드에 업로드
            image_urls.append(cloud_image_url)  # 클라우드 이미지 URL 추가
    print(image_urls)
    
    # 스토리보드 생성 (동행인 수 포함)
    storyboard_scenes = gpt_generate_storyboard(
        destination=place_info["name"],
        purpose=selected_theme,
        companion=companion,
        companion_count=companion_count,
        season = season,
        title=selected_title,
        intro_outro=(selected_intro, selected_outro),
        description=place_info["description"],
        image_urls=image_urls # 이미지 URL 추가
    )

    # 스토리보드 결과 출력 및 로그 기록
    print("생성된 스토리보드:")
    print(storyboard_scenes)

    # 분리된 스토리보드 데이터 리스트 
    chuncked_scenes_data = parse_storyboard(storyboard_scenes)
    print(chuncked_scenes_data)

    # 각 씬의 키워드를 추출 storyboard_scenes
    scenes = storyboard_scenes
    keywords = {}

    for scene_number, scene in enumerate(scenes):
        keyword = extract_keywords_with_rag(scene)  # scene_description 대신 scene 사용
        keywords[scene_number+1] = keyword

    # 결과 출력
    for scene, keyword in keywords.items():
        print(f"{scene}:{keyword}")
    
    # 씬별 이미지 생성 및 저장
    destination = place_info["name"]
    purpose = selected_theme
    for idx, scene in enumerate(storyboard_scenes):
        print(f"Scene {idx + 1} 이미지 생성 중...")
        generate_and_save_image_dalle(scene, destination, purpose, companion, companion_count, season, image_urls)
        print(f"Scene {idx + 1} 이미지 저장 완료")
    
    # 데이터 저장
    excel_output_path = "C:/Users/KimTY/CapstoneDesign/travel_storyboard_generation/data/travel_storyboard.xlsx"
    save_to_excel(
        storyboard=storyboard_scenes,
        region_info={"city": selected_city, "district": selected_district},
        place_info=place_info,
        season=season,
        companion=companion,
        companion_count=companion_count,
        selected_theme=selected_theme,
        output_path=excel_output_path
    )

if __name__ == "__main__":
    main()
