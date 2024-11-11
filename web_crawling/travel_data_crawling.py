import pandas as pd
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# Selenium 설정 (Chrome 버전 115 이상)
driver = webdriver.Chrome()
driver.get("https://korean.visitkorea.or.kr/list/travelinfo.do?service=ms#ms^0^All^All^All^1^^1^#%EC%A0%84%EC%B2%B4")

# 대기 시간을 30초로 설정
wait = WebDriverWait(driver, 30)

# 이미 수집된 데이터를 읽어와 진행된 관광지를 확인
output_csv_path = "C:/Users/KimTY/CapstoneDesign/travel_storyboard_generation/data/travel_database.csv"
if os.path.exists(output_csv_path):
    collected_data = pd.read_csv(output_csv_path, encoding='utf-8-sig')
    collected_places = set(collected_data['관광지 이름'].tolist())
else:
    collected_data = pd.DataFrame()
    collected_places = set()

# 데이터를 저장할 리스트 초기화
travel_data = []

def save_image(image_url, folder_path, image_name):
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # HTTP 요청 에러 확인
        with open(os.path.join(folder_path, image_name), 'wb') as img_file:
            img_file.write(response.content)
        print(f"이미지 저장 완료: {image_name}")
    except Exception as e:
        print(f"이미지 저장 중 오류 발생: {e}")

try:
    try:
        # 모든 버튼 요소 가져오기
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        for button in buttons:
            if "인기순" in button.text:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                driver.execute_script("arguments[0].click();", button)
                print("인기순 버튼 클릭 완료")
                break
    except TimeoutException:
        print("인기순 버튼을 클릭하는 동안 TimeoutException 발생")
    except ElementClickInterceptedException:
        print("요소가 가려져 클릭할 수 없음")

    # 해시태그 버튼 클릭 시도
    try:
        hashtag_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="3f36ca4b-6f45-45cb-9042-265c96a4868c"]/button/span')))
        hashtag_button.click()
        time.sleep(2)  # 해시태그 클릭 후 페이지가 업데이트될 수 있으므로 대기
    except Exception as e:
        print("해시태그 버튼을 찾지 못했습니다:", e)

    while True:
        # 페이지 로드 완료 대기
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

        # 페이지 내 모든 여행지 링크를 수집하는 XPath
        travel_links_xpath = '//*[@id="contents"]/div[2]/div[1]/ul/li/div[2]/div/a'

        # 스크롤을 사용하여 페이지 로드 완료를 보장
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 스크롤 후 대기

        # 현재 페이지의 모든 여행지 링크를 가져옴
        try:
            travel_links = wait.until(EC.presence_of_all_elements_located((By.XPATH, travel_links_xpath)))
        except TimeoutException:
            print("여행지 링크를 찾지 못했습니다. 페이지 로드가 오래 걸릴 수 있습니다.")
            break

        # 관광지 이름을 담을 리스트
        travel_names = [link.text for link in travel_links]

        # 수집한 관광지 이름 출력
        print("수집한 관광지 목록:")
        print(travel_names)

        # 각 관광지 링크에 대해 상세 페이지로 이동하여 작업 수행
        for i in range(len(travel_links)):
            # 링크를 새로 찾기 위해 반복마다 페이지로 돌아가 다시 로드
            travel_links = driver.find_elements(By.XPATH, travel_links_xpath)

            # 관광지 이름 추출
            travel_name = travel_links[i].text

            # 이미 수집된 관광지는 건너뛰기
            if travel_name in collected_places:
                print(f"이미 수집된 관광지, 건너뜀: {travel_name}")
                continue

            print(f"Processing: {travel_name}")

            # 링크 클릭하여 상세 페이지로 이동
            try:
                driver.execute_script("arguments[0].click();", travel_links[i])
            except ElementClickInterceptedException:
                print("요소가 가려져 클릭할 수 없음. 다시 시도합니다.")

            # 상세 페이지에서 필요한 작업 수행
            try:
                # 페이지 로드 완료 대기
                wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

                # 지역 탐색
                region = "정보 없음"
                city = "정보 없음"
                district = "정보 없음"
                for selector in ['#topAddr', 'div.area_address > span']:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                        region = element.text
                        if ' ' in region:
                            city, district = region.split(' ', 1)
                        else:
                            city = region  # 지역 정보가 하나만 있을 경우
                        break
                    except NoSuchElementException:
                        continue
                if region == "정보 없음":
                    print("지역 정보를 찾을 수 없습니다.")

                # 폴더 경로 설정 및 폴더 생성
                folder_path = f"C:/Users/KimTY/CapstoneDesign/travel_storyboard_generation/data_labeling/images/{city}/{district}"
                os.makedirs(folder_path, exist_ok=True)

                # 관광지 이름 탐색
                place_name = "정보 없음"
                for selector in ['#topTitle', 'h2.titleType1']:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                        place_name = element.text
                        break
                    except NoSuchElementException:
                        continue
                if place_name == "정보 없음":
                    print("관광지 이름을 찾을 수 없습니다.")

                # 관광지 특성 탐색
                place_characteristics = "정보 없음"
                for selector in [
                    'div.inr_wrap p',  # 상세 정보
                    'div.detail > p',
                    'div#content p',
                    'div.text_area p',
                    'div.content_box div p',
                    'div.detail_content p',
                ]:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                        place_characteristics = element.text
                        if place_characteristics.strip():
                            break
                    except NoSuchElementException:
                        continue
                if place_characteristics == "정보 없음":
                    print("관광지 특성을 찾을 수 없습니다.")

                # 테마 탐색
                theme = "정보 없음"
                try:
                    theme_elements = driver.find_elements(By.CSS_SELECTOR, 'div.tag_cont ul li span')
                    themes = [elem.text for elem in theme_elements if elem.text.strip()]
                    if themes:
                        theme = ", ".join(themes)
                except NoSuchElementException:
                    print("테마를 찾을 수 없습니다.")

                # 이미지 URL 탐색 (최대 2장까지 수집)
                image_urls = []
                image_selectors = ['div.swiper-slide img', 'div.photo_gallery img']
                for selector in image_selectors:
                    try:
                        images = driver.find_elements(By.CSS_SELECTOR, selector)
                        for img in images:
                            src = img.get_attribute('src')
                            if src and len(image_urls) < 2:
                                image_urls.append(src)
                                image_name = f"{place_name}_{len(image_urls)}.jpg"
                                save_image(src, folder_path, image_name)
                            if len(image_urls) >= 2:
                                break
                    except NoSuchElementException:
                        continue

                # 데이터 리스트에 추가
                travel_data.append({
                    "시/도": city,
                    "구/군": district,
                    "관광지 이름": place_name,
                    "특성": place_characteristics,
                    "테마": theme
                })

                # 출력 결과
                print(f"시/도: {city}")
                print(f"구/군: {district}")
                print(f"관광지 이름: {place_name}")
                print(f"관광지 특성: {place_characteristics}")
                print(f"테마: {theme}")
                print(f"이미지 URLs: {image_urls}")

                # 페이지마다 데이터를 CSV 파일에 저장
                df = pd.DataFrame(travel_data)
                if not collected_data.empty:
                    df = pd.concat([collected_data, df]).drop_duplicates(subset=['관광지 이름'], keep='first')
                df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')

            except Exception as e:
                print(f"데이터 수집 중 오류 발생: {e}")

            # 작업 완료 후 뒤로가기
            driver.back()

            try:
                # 페이지가 로드될 때까지 대기
                wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                wait.until(EC.presence_of_all_elements_located((By.XPATH, travel_links_xpath)))
            except TimeoutException:
                print("요소 로딩 대기 중 TimeoutException 발생. 페이지를 새로 고침하고 다시 시도합니다.")
                driver.refresh()  # 페이지 새로 고침
                time.sleep(5)  # 페이지가 다시 로드될 시간을 확보
                continue  # 다음 루프로 이동


        # 현재 페이지 번호 찾기
        try:
            current_page = driver.find_element(By.CSS_SELECTOR, 'div.page_box a.on')
            current_page_number = int(current_page.text)

            # 다음 페이지 번호 클릭 시도
            try:
                next_page_button = driver.find_element(By.LINK_TEXT, str(current_page_number + 1))
                next_page_button.click()
                time.sleep(2)  # 페이지가 넘어가는 동안 대기
            except Exception:
                # "다음" 버튼 클릭 시도
                next_button = driver.find_element(By.CSS_SELECTOR, 'a.btn_next.ico')
                next_button.click()
                time.sleep(2)  # 페이지가 넘어가는 동안 대기

        except Exception as e:
            print("페이지 이동 중 오류 발생 또는 더 이상 다음 페이지가 없습니다:", e)
            break  # 더 이상 다음 페이지가 없는 경우 종료

finally:
    driver.quit()

print("데이터 수집 및 저장이 완료되었습니다.")
