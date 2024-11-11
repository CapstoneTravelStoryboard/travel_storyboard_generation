import os

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