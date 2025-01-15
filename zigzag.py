# -*- coding: utf-8 -*-
"""debug_zigzag_crawling.py"""

import pandas as pd
import time
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 페이지를 스크롤하여 2000개 리뷰를 로드하는 함수
def scroll_to_load_reviews(driver, max_reviews=2000):
    print(f"최대 {max_reviews}개의 리뷰 로드 시작...")
    loaded_reviews = set()
    scroll_count = 0  # 스크롤 횟수 카운터
    
    while len(loaded_reviews) < max_reviews:
        scroll_count += 1
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(1.5)
        print(f"[DEBUG] {scroll_count}번째 스크롤 실행 중...")  # 스크롤 번호 출력

        # 현재 로드된 리뷰 수집
        reviews = driver.find_elements(By.CSS_SELECTOR, "#__next > div.zds-themes.light-theme > div > div > div.css-xk426o.eebc9th5 > div > div")
        for num, review in enumerate(reviews, start=1):
            loaded_reviews.add(num)

        print(f"현재 로드된 리뷰 수: {len(loaded_reviews)}/{max_reviews}", end="\r")

        # 리뷰가 2000개 이상 로드되면 중지
        if len(loaded_reviews) >= max_reviews:
            break
    
    print(f"\n스크롤 완료. 총 {len(loaded_reviews)}개의 리뷰 로드 완료!")

# 리뷰 데이터를 수집하는 함수
def crawl_reviews(driver, max_reviews=2000):
    print(f"최대 {max_reviews}개의 리뷰 데이터 수집 시작...")
    reviews_data = []
    reviews = driver.find_elements(By.CSS_SELECTOR, "#__next > div.zds-themes.light-theme > div > div > div.css-xk426o.eebc9th5 > div > div")
    
    for num, review in enumerate(reviews, start=1):
        if num > max_reviews:  # 2000개까지만 수집
            break
        print(f"\n[DEBUG] 리뷰 {num} 수집 시도...")
        try:
            base_selector = f"#__next > div.zds-themes.light-theme > div > div > div.css-xk426o.eebc9th5 > div > div:nth-child({num}) > div.css-vbvoj0.e13bai5o0"
            try:
                reviewer_id = driver.find_element(By.CSS_SELECTOR, f"{base_selector} > div.css-1ecn1de.e13bai5o0 > div.css-o3enub.e1umgzx81 > div.css-4ku0lv.e13bai5o0 > p").text
            except Exception:
                reviewer_id = ""
            print(f"[DEBUG] 아이디: {reviewer_id}")

            try:
                reviewer_grade = driver.find_element(By.CSS_SELECTOR, f"{base_selector} > div.css-1ecn1de.e13bai5o0 > div.css-o3enub.e1umgzx81 > div.css-4ku0lv.e13bai5o0 > span").text
            except Exception:
                reviewer_grade = ""
            print(f"[DEBUG] 리뷰어 등급: {reviewer_grade}")

            try:
                review_date = driver.find_element(By.CSS_SELECTOR, f"{base_selector} > div.css-1ecn1de.e13bai5o0 > div.css-u4mbk0.eimmef70 > div.css-1xqlji6.eimmef70 > span.zds4_s96ru86.zds4_s96ru81c").text
            except Exception:
                review_date = ""
            print(f"[DEBUG] 작성 날짜: {review_date}")

            try:
                review_content = driver.find_element(By.CSS_SELECTOR, f"{base_selector} > div:nth-child(3) > span").text
            except Exception:
                review_content = ""
            print(f"[DEBUG] 리뷰 내용: {review_content}")

            # 데이터 저장
            reviews_data.append({
                "유저 ID": reviewer_id,
                "리뷰어 등급": reviewer_grade,
                "작성 날짜": review_date,
                "리뷰 내용": review_content
            })
            print(f"리뷰 {num} 수집 완료.", end="\r")
        except Exception as e:
            print(f"\n[ERROR] 리뷰 {num} 수집 중 오류 발생: {e}")
            continue
    print(f"\n리뷰 데이터 수집 완료! 총 {len(reviews_data)}개의 리뷰.")
    return reviews_data

# 저장된 CSV 파일을 특정 폴더에 저장
def save_to_csv(data, product_id):
    folder_path = "reviews_output"  # 저장할 폴더 이름
    os.makedirs(folder_path, exist_ok=True)  # 폴더가 없으면 생성
    filename = os.path.join(folder_path, f"reviews_{product_id}_2000.csv")
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"리뷰 데이터를 '{filename}'에 저장했습니다.")

# 메인 실행 코드
if __name__ == "__main__":
    product_ids = ["112538672"]  # 수집할 상품 ID 리스트

    for product_id in product_ids:
        print(f"\n=== 상품 ID {product_id} 리뷰 수집 시작 ===")
        driver = None
        try:
            # 웹드라이버 초기화 및 페이지 접속
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.get(f"https://zigzag.kr/review/list/{product_id}")
            time.sleep(3)

            # 스크롤 및 리뷰 데이터 수집
            scroll_to_load_reviews(driver, max_reviews=2000)
            reviews = crawl_reviews(driver, max_reviews=2000)
            save_to_csv(reviews, product_id)

        except Exception as e:
            print(f"[ERROR] 오류 발생: {e}")
        finally:
            if driver:
                driver.quit()
