# scraper for kfc reviews on trustpilot (selenium, headless chrome)
# the csv is already in the repo, so this only needs to run if you want fresh data:
#     python scraper_KFC.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time


def scrape_kfc_reviews(url, num_pages=20):
    # run browser in background (headless)
    options = Options()
    options.add_argument("--headless")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    records = []

    try:
        for page in range(1, num_pages + 1):
            driver.get(f"{url}?page={page}")
            time.sleep(3)  # wait for js to load
            containers = driver.find_elements(By.XPATH, '//article')

            for container in containers:
                try:
                    star_img = container.find_element(
                        By.XPATH, './/img[contains(@alt, "Rated")]'
                    )
                    rating = int(star_img.get_attribute("alt").split()[1])
                    review = container.find_element(By.XPATH, './/p').text
                    date = container.find_element(
                        By.TAG_NAME, "time"
                    ).get_attribute("datetime")

                    records.append({"review": review, "rating": rating, "date": date})
                except Exception:
                    continue  # skip if something breaks
    finally:
        driver.quit()

    df = pd.DataFrame(records)
    # trustpilot repeats the same featured reviews on every page -- keep each review once
    return df.drop_duplicates(subset=["review", "rating", "date"]).reset_index(drop=True)


if __name__ == "__main__":
    kfc_url = "https://www.trustpilot.com/review/kfc.com"
    df_kfc = scrape_kfc_reviews(kfc_url, num_pages=20)
    df_kfc.to_csv("trustpilot_kfc_reviews.csv", index=False)
    print(f"saved {len(df_kfc)} reviews")
