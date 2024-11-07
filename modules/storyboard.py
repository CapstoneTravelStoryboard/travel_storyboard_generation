import openai
from modules.utils import log_to_file
from config.settings import OPENAI_API_KEY


openai.api_key = OPENAI_API_KEY
client = openai.api_key


# 8. GPT를 이용한 스토리보드 생성
def gpt_generate_storyboard(destination, purpose, companion, companion_count, title, intro_outro, description, log_file, image_urls):
    prompt = f"""
    당신은 여행 영상 스토리보드 생성 전문가입니다. 아래의 양식을 참고하여 주어진 정보를 바탕으로 적당한 개수의 씬으로 나눠서 스토리보드를 작성해주세요. 각 씬마다 구체적인 장면과 촬영 기법을 설명해주세요.

    스토리보드 양식:
    - scene (여기에 씬 순서를 넣어주세요.) "여기에 씬 제목을 넣어주세요.":
        1. **영상**: 이 씬에서 어떤 장면이 나오는지 자세히 설명해주세요.
        2. **화각**: 카메라가 어떤 각도에서 장면을 촬영하는지 설명해주세요.
        3. **카메라 무빙**: 카메라가 어떻게 움직이는지, 특별한 촬영 기법이 있다면 설명해주세요.
        4. **구도**: 화면에서 대상이 어떻게 배치되고, 어떤 느낌을 주는지 설명해주세요.

    이제 위 양식을 참고하여, 아래 정보를 바탕으로 여러 개의 씬으로 나눠서 스토리보드를 작성해주세요. 
    씬을 제외하고는 어떠한 추가적인 내용을 포함하지 말아주세요.

    여행지: {destination}
    여행지 특성: {description}
    여행 목적: {purpose}
    동행인: {companion} ({companion_count}명)
    제목: {title}
    인트로: {intro_outro[0]}
    아웃트로: {intro_outro[1]}
    이미지 URL: {image_urls}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    
    storyboard = response.choices[0].message.content
    print(storyboard)
    log_to_file(f"생성된 스토리보드:\n{storyboard}\n", log_file)
    # 씬별로 나누어 저장하기 위한 리스트
    storyboard_scenes = []

    # GPT 응답을 씬별로 분할하여 리스트에 저장
    scenes = storyboard.split("- scene")  # 씬 구분을 위해 "scene"을 기준으로 분할
    for i, scene in enumerate(scenes[1:], 1):  # 첫 번째 항목은 빈 항목이므로 제외하고 처리
        formatted_scene = f"- scene{scene.strip()}"  # 씬 번호는 기존 GPT 응답에서 유지
        storyboard_scenes.append(formatted_scene)

    return storyboard_scenes