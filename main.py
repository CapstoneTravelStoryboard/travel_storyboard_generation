import os
from datetime import datetime
from modules.cloud_storage import upload_image_to_cloud
from modules.gpt_integration import gpt_select_title, gpt_select_intro_outro
from modules.image_generation import generate_and_save_image
from modules.place_selection import load_database, select_city, select_place, input_companion, get_place_info, select_theme
from modules.storyboard import gpt_generate_storyboard
from modules.utils import log_to_file
from modules.technique_keyword_extractor import extract_keywords_with_rag

# 메인 함수
def main():
    # 현재 시간을 제목으로 설정하여 로그 파일 이름 생성
    current_time_str = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    log_directory = f"logs/{current_time_str}"

    # 로그 디렉토리가 없으면 생성
    os.makedirs(log_directory, exist_ok=True)

    log_file = f"{log_directory}/travel_storyboard_log.txt"

    # 여행지 정보 데이터베이스 
    db = load_database("travel_database.csv")
    city = select_city(db, log_file)
    place = select_place(city, db, log_file)
    companion, companion_count = input_companion(log_file)
    
    # 선택된 관광지 정보 가져오기
    place_info = get_place_info(place[1], db, log_file)
    if not place_info:
        print("관광지 정보를 찾을 수 없습니다.")
        return
    
    # 테마 선택 및 로그 기록
    selected_theme = select_theme(place_info["theme"], log_file)
    
    # GPT를 이용해 제목 추천 (동행인 수 포함)
    selected_title = gpt_select_title(place_info["name"], selected_theme, companion, companion_count, place_info["description"], log_file)
    
    # GPT를 이용해 인트로와 아웃트로 추천
    selected_intro, selected_outro = gpt_select_intro_outro(selected_title, log_file)
    
    # 관광지의 외관과 주변 환경을 제공할 이미지 URL 수집
    image_directory = f"data_labeling/image/{place[0]}/{place[1]}"
    image_urls = []

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
        title=selected_title,
        intro_outro=(selected_intro, selected_outro),
        description=place_info["description"],
        log_file=log_file,
        image_urls=image_urls  # 이미지 URL 추가
    )

    # 스토리보드 결과 출력 및 로그 기록
    print("생성된 스토리보드:")
    print(storyboard_scenes)

    # 각 씬의 키워드를 추출
    scenes = storyboard_scenes  # 스토리보드 씬 리스트
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
        scene_image_path = f"{log_directory}/scene_{idx + 1}.png"
        generate_and_save_image(scene, destination, purpose, companion, companion_count, image_urls, scene_image_path)
        print(f"Scene {idx + 1} 이미지 저장 완료: {scene_image_path}")
        log_to_file(f"Scene {idx + 1} 이미지 저장 완료: {scene_image_path}\n", log_file)


if __name__ == "__main__":
    main()
