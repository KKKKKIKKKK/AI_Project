import pandas as pd
import time
import csv
import tqdm
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

# Selenium WebDriver 초기화
options = webdriver.ChromeOptions()
# options.add_argument('--headless')
# options.add_argument('--start-maximized')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 상품 ID 리스트
product_ids = ["128574337"]
# 최대 리뷰 개수 설정
max_reviews = 1000

try:
    # 각 상품 ID에 대해 크롤링
    for product_id in product_ids:
        print(f"\n[INFO] 상품 ID: {product_id} 크롤링 시작")
        
        # 해당 상품의 리뷰 페이지로 이동
        url = f"https://zigzag.kr/review/list/{product_id}"
        driver.get(url)
        time.sleep(2)  # 페이지 로드 대기

        # 지정 요소 탐색 (더미 데이터를 탐색색)
        target_selectors = [
            "div > p.zds4_s96ru86.zds4_s96ru818.css-sdnfp7.efip69o1 > div > div > p > span:nth-child(1)", #봇
            "div:nth-child({1001}) > div.css-vbvoj0.e13bai5o0 > div.css-1ecn1de.e13bai5o0 > div.css-o3enub.e1umgzx81 > div.css-4ku0lv.e13bai5o0 > p"
        ]
        found = False

        print("[INFO] 지정된 요소를 찾는 중...")
        while not found:
            try:
                # "더보기" 버튼 처리
                try:
                    more_buttons = driver.find_elements(By.CSS_SELECTOR, "p.zds4_s96ru86.zds4_s96ru817.css-xjl5eq.e1i7prb51")
                    for button in more_buttons:
                        driver.execute_script("arguments[0].click();", button)  # JavaScript로 클릭
                        print("[INFO] '더보기' 버튼 클릭 완료")
                        time.sleep(0.3)
                except Exception as e:
                    print(f"[WARNING] '더보기' 버튼 처리 중 오류 발생: {e}")

                # 지정한 요소 중 하나라도 존재하는지 확인
                for selector in target_selectors:
                    try:
                        target_element = driver.find_element(By.CSS_SELECTOR, selector)
                        found = True
                        print(f"[INFO] 지정된 요소를 찾았습니다! ({selector})")

                        # 해당 요소가 보이도록 스크롤
                        driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
                        time.sleep(1)
                        break
                    except:
                        continue

                if found:
                    break
            except Exception as e:
                print(f"[WARNING] 요소 탐색 중 오류 발생: {e}")

            # 스크롤 동작
            print(f"[INFO] 스크롤 시도중중...")
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)

        # 맨 위로 스크롤
        print("[INFO] 맨 위로 스크롤합니다...")
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.HOME)
        time.sleep(1)

        # 데이터 수집 시작
        print("[INFO] 데이터 수집 시작")
        data = []  # 데이터 저장 리스트 초기화
        current_review = 1  # 첫 리뷰 번호
        empty_count = 0  # 모든 컬럼이 없는 경우의 카운터

        while current_review <= max_reviews:
            try:
                num = current_review
                review_data = {}

                print(f"[INFO] {current_review}번 리뷰 데이터 수집 중...")

                # ★아이디
                try:
                    review_data["아이디"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div.css-1ecn1de.e13bai5o0 > div.css-o3enub.e1umgzx81 > div.css-4ku0lv.e13bai5o0 > p").text
                except:
                    review_data["아이디"] = None

                # ★리뷰어 등급
                try:
                    review_data["리뷰어 등급"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div.css-1ecn1de.e13bai5o0 > div.css-o3enub.e1umgzx81 > div.css-4ku0lv.e13bai5o0 > span").text
                except:
                    review_data["리뷰어 등급"] = None


                # ★작성 날짜
                try:
                    review_data["작성 날짜"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div.css-1ecn1de.e13bai5o0 > div.css-u4mbk0.eimmef70 > div.css-1xqlji6.eimmef70 > span.zds4_s96ru86.zds4_s96ru81c").text
                except:
                    review_data["작성 날짜"] = None

                # ★옵션1, 옵션2
                try:
                    review_data["옵션1"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div:nth-child(1) > p > span:nth-child(1)").text
                except:
                    try:
                        review_data["옵션1"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div:nth-child(1) > p > span:nth-child(1)").text
                    except:
                        review_data["옵션1"] = None
                try:
                    review_data["옵션2"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div:nth-child(1) > p > span:nth-child(2)").text
                except:
                    try:
                        review_data["옵션2"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div:nth-child(1) > p > span:nth-child(2)").text
                    except:
                        review_data["옵션2"] = None

                # ★상품 사이즈, 퀄리티, 색감
                try:
                    review_data["상품 사이즈"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div.css-1wzypsy.eimmef70 > div:nth-child(1) > p").text
                except:
                    try:
                        review_data["상품 사이즈"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div.css-1wzypsy.eimmef70 > div:nth-child(1) > p").text
                    except:
                        review_data["상품 사이즈"] = None
                try:
                    review_data["퀄리티"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div.css-1wzypsy.eimmef70 > div:nth-child(2) > p").text
                except:
                    try:
                        review_data["퀄리티"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div.css-1wzypsy.eimmef70 > div:nth-child(2) > p").text
                    except:
                        review_data["퀄리티"] = None
                try:
                    review_data["색감"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div.css-1wzypsy.eimmef70 > div:nth-child(3) > p").text
                except:
                    try:
                        review_data["색감"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div.css-1wzypsy.eimmef70 > div:nth-child(3) > p").text
                    except:
                        review_data["색감"] = None

                # ★키, 몸무게, 사이즈
                try:
                    review_data["키"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div:nth-child(3) > p > span:nth-child(1)").text
                except:
                    try:
                        review_data["키"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div:nth-child(3) > p > span:nth-child(1)").text
                    except:
                        review_data["키"] = None
                try:
                    review_data["몸무게"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div:nth-child(3) > p > span:nth-child(2)").text
                except:
                    try:
                        review_data["몸무게"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div:nth-child(3) > p > span:nth-child(2)").text
                    except:
                        review_data["몸무게"] = None
                try:
                    review_data["사이즈"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div:nth-child(3) > p > span:nth-child(3)").text
                except:
                    try:
                        review_data["사이즈"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div:nth-child(3) > p > span:nth-child(3)").text
                    except:
                        review_data["사이즈"] = None

                # ★리뷰내용
                try:
                    review_data["리뷰내용"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > span").text
                except:
                    try:
                        review_data["리뷰내용"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({num}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > span").text
                    except:
                        review_data["리뷰내용"] = None

                # 데이터 추가
                data.append(review_data)
                print(f"[INFO] {current_review}번 리뷰 데이터 수집 완료.")
            except Exception as e:
                print(f"[ERROR] {current_review}번 리뷰 데이터 수집 중 오류: {e}")

            # 다음 리뷰로 이동
            current_review += 1

            # # 스크롤 동작
            # driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            # time.sleep(0.3)

        # 상품별 데이터 저장
        df = pd.DataFrame(data)
        df.to_csv(f"셔츠_p_{product_id}.csv", index=False, encoding="utf-8-sig")
        print(f"[INFO] 상품 ID {product_id} 데이터 저장 완료")

finally:
    # 브라우저 종료
    driver.quit