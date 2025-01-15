import pandas as pd
import time
import gc  # 가비지 컬렉터
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 상품 ID 리스트
product_ids = ["111493815"]

# 최대 리뷰 개수 설정
max_reviews = 1000

# Selenium WebDriver 설정 함수
def initialize_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 크롬 창을 띄우지 않음
    # options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

try:
    # 각 상품 ID에 대해 크롤링
    for product_id in product_ids:
        print(f"\n[INFO] 상품 ID: {product_id} 크롤링 시작")

        # Selenium WebDriver 초기화
        driver = initialize_driver()

        try:
            # 해당 상품의 리뷰 페이지로 이동
            url = f"https://zigzag.kr/review/list/{product_id}"
            driver.get(url)
            time.sleep(2)  # 페이지 로드 대기

            # 지정 요소 탐색
            target_selectors = [
                "div > p.zds4_s96ru86.zds4_s96ru818.css-sdnfp7.efip69o1 > div > div > p > span:nth-child(1)",
                "div:nth-child(1001) > div.css-vbvoj0.e13bai5o0 > div.css-1ecn1de.e13bai5o0 > div.css-o3enub.e1umgzx81 > div.css-4ku0lv.e13bai5o0 > p"
            ]
            found = False

            print("[INFO] 지정된 요소를 찾는 중...")
            while not found:
                try:
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
                try:
                    print(f"[INFO] 스크롤 시도중...")
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.3)

                    # 강제로 스크롤 동작이 멈추었을 경우 대비 추가 스크롤
                    driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(0.5)
                    driver.execute_script("window.scrollBy(0, -20);")
                    print("[INFO] 강제 스크롤 수행 완료")
                except Exception as e:
                    print(f"[WARNING] 강제 스크롤 중 오류 발생: {e}")

            if found:
                print("[INFO] 지정된 요소를 찾았으므로 스크롤을 멈춥니다.")

            # 데이터 수집 시작
            print("[INFO] 데이터 수집 시작")
            data = []  # 데이터 저장 리스트 초기화
            current_review = 1  # 첫 리뷰 번호

            while current_review <= max_reviews:
                try:
                    review_data = {}
                    print(f"[INFO] {current_review}번 리뷰 데이터 수집 중...")

                    # "더보기" 버튼 처리
                    try:
                        more_buttons = driver.find_elements(By.CSS_SELECTOR, "p.zds4_s96ru86.zds4_s96ru817.css-xjl5eq.e1i7prb51")
                        for button in more_buttons:
                            driver.execute_script("arguments[0].click();", button)  # JavaScript로 클릭
                            print("[INFO] '더보기' 버튼 클릭 완료")
                            time.sleep(0.3)
                    except Exception as e:
                        print(f"[WARNING] '더보기' 버튼 처리 중 오류 발생: {e}")

                    # ★아이디
                    try:
                        review_data["아이디"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div.css-1ecn1de.e13bai5o0 > div.css-o3enub.e1umgzx81 > div.css-4ku0lv.e13bai5o0 > p").text
                    except:
                        review_data["아이디"] = None

                    # ★리뷰어 등급
                    try:
                        review_data["리뷰어 등급"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div.css-1ecn1de.e13bai5o0 > div.css-o3enub.e1umgzx81 > div.css-4ku0lv.e13bai5o0 > span").text
                    except:
                        review_data["리뷰어 등급"] = None


                    # ★작성 날짜
                    try:
                        review_data["작성 날짜"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div.css-1ecn1de.e13bai5o0 > div.css-u4mbk0.eimmef70 > div.css-1xqlji6.eimmef70 > span.zds4_s96ru86.zds4_s96ru81c").text
                    except:
                        review_data["작성 날짜"] = None

                    # ★옵션1, 옵션2
                    try:
                        review_data["옵션1"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div:nth-child(1) > p > span:nth-child(1)").text
                    except:
                        try:
                            review_data["옵션1"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div:nth-child(1) > p > span:nth-child(1)").text
                        except:
                            review_data["옵션1"] = None
                    try:
                        review_data["옵션2"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div:nth-child(1) > p > span:nth-child(2)").text
                    except:
                        try:
                            review_data["옵션2"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div:nth-child(1) > p > span:nth-child(2)").text
                        except:
                            review_data["옵션2"] = None

                    # ★상품 사이즈, 퀄리티, 색감
                    try:
                        review_data["상품 사이즈"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div.css-1wzypsy.eimmef70 > div:nth-child(1) > p").text
                    except:
                        try:
                            review_data["상품 사이즈"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div.css-1wzypsy.eimmef70 > div:nth-child(1) > p").text
                        except:
                            review_data["상품 사이즈"] = None
                    try:
                        review_data["퀄리티"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div.css-1wzypsy.eimmef70 > div:nth-child(2) > p").text
                    except:
                        try:
                            review_data["퀄리티"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div.css-1wzypsy.eimmef70 > div:nth-child(2) > p").text
                        except:
                            review_data["퀄리티"] = None
                    try:
                        review_data["색감"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div.css-1wzypsy.eimmef70 > div:nth-child(3) > p").text
                    except:
                        try:
                            review_data["색감"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div.css-1wzypsy.eimmef70 > div:nth-child(3) > p").text
                        except:
                            review_data["색감"] = None

                    # ★키, 몸무게, 사이즈
                    try:
                        review_data["키"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div:nth-child(3) > p > span:nth-child(1)").text
                    except:
                        try:
                            review_data["키"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div:nth-child(3) > p > span:nth-child(1)").text
                        except:
                            review_data["키"] = None
                    try:
                        review_data["몸무게"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div:nth-child(3) > p > span:nth-child(2)").text
                    except:
                        try:
                            review_data["몸무게"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div:nth-child(3) > p > span:nth-child(2)").text
                        except:
                            review_data["몸무게"] = None
                    try:
                        review_data["사이즈"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > div > div > div:nth-child(3) > p > span:nth-child(3)").text
                    except:
                        try:
                            review_data["사이즈"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > div > div > div:nth-child(3) > p > span:nth-child(3)").text
                        except:
                            review_data["사이즈"] = None

                    # ★리뷰내용
                    try:
                        review_data["리뷰내용"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(2) > span").text
                    except:
                        try:
                            review_data["리뷰내용"] = driver.find_element(By.CSS_SELECTOR, f"div:nth-child({current_review}) > div.css-vbvoj0.e13bai5o0 > div:nth-child(3) > span").text
                        except:
                            review_data["리뷰내용"] = None

                    # 데이터 추가
                    data.append(review_data)
                    print(f"[INFO] {current_review}번 리뷰 데이터 수집 완료.")
                except Exception as e:
                    print(f"[ERROR] {current_review}번 리뷰 데이터 수집 중 오류: {e}")

                # 다음 리뷰로 이동
                current_review += 1

            # 상품별 데이터 저장
            df = pd.DataFrame(data)
            df.to_csv(f"review_data_{product_id}.csv", index=False, encoding="utf-8-sig")
            print(f"[INFO] 상품 ID {product_id} 데이터 저장 완료")

        finally:
            # 브라우저 종료 및 메모리 정리
            driver.quit()
            del data  # 리스트 삭제
            gc.collect()  # 가비지 컬렉터 실행
            print("[INFO] 메모리 정리 완료")

except Exception as e:
    print(f"[ERROR] 전체 크롤링 중 오류 발생: {e}")