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
with open('../universities.json', 'r', encoding='utf-8') as f:
    universities = json.load(f)['universities']

# Find USYD's URL
uq_url = next((uni['url'] for uni in universities if uni['name'] == "UQ"), None)

if uq_url:
    driver.get(uq_url)  # Directly request USYD's URL
    print(f"Requested URL: {uq_url}")  # Print the requested URL

    # Wait for the page to load
    driver.implicitly_wait(10)

    job_data = []  # Create an empty list to store job data

    # Ensure the tables folder exists
    if not os.path.exists('tables'):
        os.makedirs('tables')

    while True:
        # Locate <a> tags using data-automation-id
        links = driver.find_elements(By.CSS_SELECTOR, "a[data-automation-id='jobTitle']")
        if not links:
            print("No jobs found.")
            break

        for link in links:
            job_title = link.text.strip()  # Extract job title
            job_link = uq_url + link.get_attribute("href")  # Extract link
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

    # Output as a CSV file
    df.to_csv('tables/uq_job_listings.csv', index=False, encoding='utf-8-sig')  # Output as a CSV file
    print("usyd output to: uq_job_listings.csv")

driver.quit()  # Close the browser
