from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import pandas as pd  # Import pandas library
import time  # Import time library
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os  # Import os library

# Set up Chrome driver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Headless mode
service = Service('/usr/local/bin/chromedriver')  # Replace with your chromedriver path
driver = webdriver.Chrome(service=service, options=chrome_options)

# Read university URLs
with open(os.path.join(os.path.dirname(__file__), '..', 'universities.json'), 'r', encoding='utf-8') as f:
    universities = json.load(f)['universities']

# Find UQ's URL
uq_url = next((uni['url'] for uni in universities if uni['name'] == "UQ"), None)

if uq_url:
    driver.get(uq_url)  # Directly request USYD's URL
    print(f"Requested URL: {uq_url}")  # Print the requested URL

    # Wait for the page to load
    driver.implicitly_wait(10)

    job_data = []  # Create an empty list to store job data

    while True:
        # Locate <a> tags using data-automation-id
        links = driver.find_elements(By.CSS_SELECTOR, "a[data-automation-id='jobTitle']")
        if not links:
            print("No jobs found.")
            break

        for link in links:
            job_title = link.text.strip()  # Extract job title
            job_link = link.get_attribute("href")  # 直接获取完整链接
            job_data.append({"Job Title": job_title, "UniName": "UQ", "Link": job_link})  # Add job data to the list

        # Find and click the next page button
        try:
            # Use explicit wait to find the "next" button
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='next']"))
            )
            next_button.click()  # Click the next page button
            time.sleep(3)  # Wait for the page to load
        except Exception as e:
            # print("No more pages or error occurred:", e)
            break

    # Create DataFrame and output as a table
    df = pd.DataFrame(job_data)
    print(df)  # Print the table

    # Ensure 'tables' directory exists in the project root
    tables_dir = os.path.join(os.path.dirname(__file__), '..', 'tables')
    os.makedirs(tables_dir, exist_ok=True)

    # Output CSV file
    output_path = os.path.join(tables_dir, 'uq_job_listings.csv')
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"uq output to: {output_path}")

driver.quit()  # Close the browser
