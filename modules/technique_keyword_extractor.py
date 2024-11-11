import json
import numpy as np
from openai import OpenAI
from config.settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# RAG를 활용하여 키워드를 추출하는 함수 정의
def extract_keywords_with_rag(scene_description):
    # Retrieval 단계: 씬 설명에서 촬영기법을 식별하여 context 생성
    # 촬영기법 데이터베이스 (예: 각 기법별 설명과 임베딩)
    with open('embedding/techniques_embeddings.json', 'r', encoding='utf-8') as f:
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
         f"당신은 영상촬영 전문가입니다. 다음 씬의 대표 촬영 기법인{best_technique}:{best_description_embedding}에 대해서 설명해주세요. 아래 형식을 참고해주세요\
            \n\n\
            여기에 촬영기법에 대한 설명과 씬에서의 적용방법 설명을 간단하게 한 줄로 넣어주세요. "},
        {"role": "user", "content": f"장면 설명:\n{scene_description}\n\n"}
    ]
    )
    
    return response.choices[0].message.content