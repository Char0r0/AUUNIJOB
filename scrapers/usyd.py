from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import pandas as pd
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Set up Chrome driver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Headless mode
service = Service('/usr/local/bin/chromedriver')  # Replace with your chromedriver path
driver = webdriver.Chrome(service=service, options=chrome_options)

# Read university URLs
with open(os.path.join(os.path.dirname(__file__), '..', 'universities.json'), 'r', encoding='utf-8') as f:
    universities = json.load(f)['universities']

# Find USYD's URL
usyd_url = next((uni['url'] for uni in universities if uni['name'] == "USYD"), None)

if usyd_url:
    driver.get(usyd_url)
    print(f"Requested URL: {usyd_url}")

    # Wait for the page to load
    driver.implicitly_wait(10)

    job_data = []

    while True:
        # Locate <a> tags using data-automation-id
        links = driver.find_elements(By.CSS_SELECTOR, "a[data-automation-id='jobTitle']")
        if not links:
            print("No jobs found.")
            break

        for link in links:
            job_title = link.text.strip()
            job_link = link.get_attribute("href")  # 直接获取完整链接
            job_data.append({"Job Title": job_title, "UniName": "USYD", "Link": job_link})

        # Find and click the next page button
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='next']"))
            )
            next_button.click()
            time.sleep(3)
        except Exception as e:
            break

    # Create DataFrame and output as a table
    df = pd.DataFrame(job_data)
    print(df)

    # Ensure 'tables' directory exists in the project root
    tables_dir = os.path.join(os.path.dirname(__file__), '..', 'tables')
    os.makedirs(tables_dir, exist_ok=True)

    # Output CSV file
    output_path = os.path.join(tables_dir, 'usyd_job_listings.csv')
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"usyd output to: {output_path}")

driver.quit()
