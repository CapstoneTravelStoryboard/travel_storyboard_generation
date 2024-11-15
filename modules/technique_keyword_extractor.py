import json
import numpy as np
from openai import OpenAI
from config.settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# RAG를 활용하여 키워드를 추출하는 함수 정의
def extract_keywords_with_rag(scene_description):
    # Retrieval 단계: 씬 설명에서 촬영기법을 식별하여 context 생성
    # 촬영기법 데이터베이스 (예: 각 기법별 설명과 임베딩)
    with open('C:/Users/KimTY/CapstoneDesign/travel_storyboard_generation/embedding/techniques_embeddings.json', 'r', encoding='utf-8') as f:
        techniques_db = json.load(f)

    # 씬 설명을 임베딩하여 가장 가까운 촬영 기법 찾기
    scene_embedding = client.embeddings.create(
        input=scene_description,
        model="text-embedding-3-small"
    ).data[0].embedding

    # 각 촬영 기법의 임베딩과 유사도 계산
    best_technique = None
    highest_similarity = -1

    # 카테고리와 기법을 순차적으로 돌면서 유사도 계산
    for category, techniques in techniques_db.items():
        for technique_name in techniques["techniques"].keys():
            technique_name = technique_name
            description_embedding = techniques["techniques"][technique_name]["description_embedding"]

        # 코사인 유사도 계산
        similarity = np.dot(scene_embedding, description_embedding) / (np.linalg.norm(scene_embedding) * np.linalg.norm(description_embedding))

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_technique = technique_name 
            best_description_embedding = description_embedding

    # Generation 단계: ChatGPT에 해당 씬의 설명과 촬영 기법 context를 전달하여 핵심 키워드 생성
    response = client.chat.completions.create(
      model="gpt-4o",  # 사용하고자 하는 모델
      messages = [
        {"role": "system", "content": 
        f"### 지시사항 ###\n"
        f"당신은 영상촬영 전문가입니다. 주어진 촬영 기법을 설명하고, 장면에서의 적용 방법을 제시해주세요. 이 작업을 정확하게 수행하면 보상을 받을 것입니다.\n\n"
        f"촬영 기법: {best_technique}\n"
        f"설명 요약: {best_description_embedding}\n\n"
        f"### 작성 형식 ###\n"
        f"촬영 기법에 대한 설명과 이 기법이 장면에 어떻게 적용되는지 자연스럽게, 간결한 어투로 한 줄로 서술해주세요.\n\n"
        f"예시:\n"
        f"이 기법은 인물의 감정을 강조하기 위해 가까운 화각으로 사용되며, 촬영 시 집중감을 높여줍니다.\n"
        },
        {"role": "user", "content": f"장면 설명:\n{scene_description}\n\n"}
        ],
        temperature=0.2
    )
    
    return response.choices[0].message.content