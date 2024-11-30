import os
import pandas as pd
from datetime import datetime


# 로그를 파일에 저장하는 함수
def log_to_file(log_content, log_file):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_content + "\n")

def get_image_urls(image_directory, place):
    image_urls = []
    # 전체 이미지 디렉토리 경로에 시/도, 구/군, 관광지 이름을 포함시킴
    full_image_directory = os.path.join(image_directory, place[0], place[1])  # 시/도, 구/군, 관광지 이름 폴더 경로 구성

    if os.path.exists(full_image_directory):
        images = [img for img in os.listdir(full_image_directory) if img.endswith(('.png', '.jpg', '.jpeg'))]
        # 첫 두 장만 선택
        for idx, img in enumerate(sorted(images)[:2], start=1):
            image_urls.append(f"images/{place[0]}/{place[1]}/{place[2]}_{idx}.jpg")
    else:
        print(f"{full_image_directory} 경로가 존재하지 않습니다.")

    return image_urls

def save_to_excel(storyboard, region_info, place_info, season, companion, companion_count, selected_theme, output_path):
    """
    데이터 정리 후 Excel 파일로 특정 xlsx에 저장
    """
    # 생성된 시간
    created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 데이터 구성
    data = {
        "생성된 시간": [created_time],
        "스토리보드": [", ".join(storyboard)],  # 스토리보드 내용을 한 셀에 저장
        "city": [region_info["city"]],  # 시/도
        "district": [region_info["district"]],  # 구/군
        "관광지 이름": [place_info["name"]],
        "테마": [place_info["theme"]],
        "계절": [season],
        "동행인": [companion],
        "인원수": [companion_count],
        "선택된 테마": [selected_theme]
    }

    # DataFrame 생성
    df_new = pd.DataFrame(data)

    # 기존 파일에 추가하거나 새 파일 생성
    try:
        # 기존 파일 읽기
        if os.path.exists(output_path):
            df_existing = pd.read_excel(output_path)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new

        # 저장
        df_combined.to_excel(output_path, index=False)
        print(f"데이터가 {output_path}에 저장되었습니다.")
    except Exception as e:
        print(f"데이터 저장 중 오류 발생: {e}")
