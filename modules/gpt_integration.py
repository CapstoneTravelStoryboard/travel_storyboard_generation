import re
from openai import OpenAI

from modules.utils import log_to_file
from config.settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# GPT를 이용해 제목 추천
def gpt_select_title(destination, purpose, companion, companion_count, description, log_file):
    prompt = f"여행지: {destination}, 여행지 특성: {description}, 여행 목적: {purpose}, 동행인: {companion} ({companion_count}명)\n"
    prompt += "위 정보에 기반하여 여행 영상의 제목을 5가지 추천해줘."
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 여행 관련 제목을 추천하는 전문가입니다.\n\
            아래의 형식으로 제목을 제안해 주세요:\n\
            항목순서. 여기에 제목을 기입해주세요. \n\n\
            1. \n\
            2. \n\
            3. \n\
            4. \n\
            5. \n\
            "},
            {"role": "user", "content": prompt}
        ]
    )
    
    content = response.choices[0].message.content 
    log_to_file(f"GPT 추천 제목들: {content}\n", log_file)  # GPT 응답 기록
    titles = re.split(r'\d+\.\s', content)[1:]  # 숫자.로 시작하는 패턴 기준으로 분리, 첫 빈 항목 제거

    # 출력 및 선택
    print("제목을 선택하세요:")
    for idx, title in enumerate(titles):
        print(f"{idx + 1}. {title}")
    
    title_choice = int(input("제목 번호 입력: ")) - 1
    selected_title = titles[title_choice]
    
    # 선택된 제목을 파일에 기록
    log_to_file(f"선택한 제목: {selected_title}\n", log_file)
    
    return selected_title


# GPT를 이용해 인트로/아웃트로 추천
def gpt_select_intro_outro(title, log_file):
    prompt = f"여행 영상 제목: {title}\n"
    prompt += "이 제목을 기반으로 인트로와 아웃트로를 5가지 추천해줘."
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 여행 영상 스토리보드를 위한 인트로와 아웃트로를 추천하는 전문가입니다.\n\
            아래의 형식을 참고하여 인트로와 아웃트로를 각각 5가지씩 제안해 주세요.\n\
            항목순서. 여기에는 인트로 혹은 아웃트로 제목을 기입해주세요.: 여기에는 인트로 혹은 아웃트로에 대해 설명해주세요. 제목과 내용을 한줄에 적어주세요.\n\n\
            인트로:\n\
            1. \n\
            2. \n\
            3. \n\
            4. \n\
            5. \n\n\
            아웃트로:\n\
            1. \n\
            2. \n\
            3. \n\
            4. \n\
            5. \n\n"\
            },
            {"role": "user", "content": prompt}
        ]
    )
    
    content = response.choices[0].message.content
    log_to_file(f"{content}\n", log_file) # GPT 응답 파일에 기록
    sections = content.split("\n\n아웃트로:")  
    intro_section = sections[0].replace("인트로:", "").strip()  
    outro_section = sections[1].strip() if len(sections) > 1 else ""  
    
    intros = [
        intro.strip().split(" ", 1)[1] if intro[0].isdigit() and len(intro.split(" ", 1)) > 1 else intro
        for intro in intro_section.split("\n") if intro.strip()
    ]
    outros = [
        outro.strip().split(" ", 1)[1] if outro[0].isdigit() and len(outro.split(" ", 1)) > 1 else outro
        for outro in outro_section.split("\n") if outro.strip()
    ]
    
    print("인트로를 선택하세요:")
    for idx, intro in enumerate(intros):
        print(f"{idx + 1}. {intro}")
    intro_choice = int(input("인트로 번호 입력: ")) - 1
    selected_intro = intros[intro_choice]
    
    print("아웃트로를 선택하세요:")
    for idx, outro in enumerate(outros):
        print(f"{idx + 1}. {outro}")
    outro_choice = int(input("아웃트로 번호 입력: ")) - 1
    selected_outro = outros[outro_choice]
    
    # 선택된 인트로/아웃트로를 파일에 기록
    log_to_file(f"선택한 인트로: {selected_intro}\n", log_file)
    log_to_file(f"선택한 아웃트로: {selected_outro}\n", log_file)
    
    return selected_intro, selected_outro
