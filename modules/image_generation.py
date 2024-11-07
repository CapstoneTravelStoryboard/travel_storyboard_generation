import requests
import openai
from config.settings import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
client = openai.api_key

# DALL·E 3를 사용하여 이미지를 생성하고 저장하는 함수
def generate_and_save_image(scene_description, destination, purpose, companion, companion_count, image_urls, save_path):
    prompt = (
        "You are an expert in generating images for storyboards. "
        f"Create an image based on a video storyboard scene description: {scene_description}. "
        f"This scene is set in {destination}, where the purpose of the trip is {purpose}. "
        f"The traveler is accompanied by {companion_count} {companion}(s). "
        "Since this scene is part of a storyboard, include the cinematic atmosphere. "
        f"Reference the following images of the destination for accuracy in visual elements: {', '.join(image_urls)}."
    )
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    
    image_url = response.data[0].url
    
    # 이미지 다운로드 및 저장
    img_data = requests.get(image_url).content
    with open(save_path, 'wb') as handler:
        handler.write(img_data)
