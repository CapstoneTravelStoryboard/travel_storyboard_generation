import json
import numpy as np
import openai
from config.settings import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
client = openai.api_key

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

    # techniques_db가 데이터 구조로 제공되었다고 가정
    for technique_name, technique_data in techniques_db.items():
        technique_embedding = technique_data['description_embedding']  # 설명 임베딩

        # 코사인 유사도 계산
        similarity = np.dot(scene_embedding, technique_embedding) / (np.linalg.norm(scene_embedding) * np.linalg.norm(technique_embedding))

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_technique = technique_name 

    # Generation 단계: ChatGPT에 해당 씬의 설명과 촬영 기법 context를 전달하여 핵심 키워드 생성
    response = client.chat.completions.create(
      model="gpt-4o",  # 사용하고자 하는 모델
      messages = [
        {"role": "system", "content": 
         f"당신은 영상촬영 전문가입니다. 다음은 촬영기법에 대한 설명입니다:\n\n\{techniques_db}\n\n이 설명을 참고하여, 다음 씬의 대표 촬영 기법인{best_technique}에 대해서 설명해주세요. 아래 형식을 참고해주세요\
            \n\n\
            여기에 촬영 기법 이름을 넣어주세요: 여기에 촬영기법에 대한 설명과 적용방법 설명을 넣어주세요. "},
        {"role": "user", "content": f"장면 설명:\n{scene_description}\n\n"}
    ]
    )
    
    return response.choices[0].message.content