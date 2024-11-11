import json
import csv
import requests
from bs4 import BeautifulSoup
import os

# Read university information from JSON file
with open('universities.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get the URL for UNSW
base_url = next((uni['url'] for uni in data['universities'] if uni['name'] == 'UNSW'), None)

job_data = []  # Create an empty list to store job data
page = 1  # Initialize page number

while True:
    # Build the request URL
    request_url = f"https://external-careers.jobs.unsw.edu.au/cw/en/listing?page={page}&page-items=20"
    
    # Send POST request
    response = requests.post(request_url)
    
    if response.status_code != 200:
        print("No more jobs to load or request failed.")
        break  # If request failed, exit the loop

    # Parse job information
    soup = BeautifulSoup(response.text, 'html.parser')
    job_links = soup.find_all('a', class_='job-link')

    if not job_links:
        print("No more jobs found.")
        break  # If no jobs found, exit the loop

    for job in job_links:
        title = job.text
        link = job['href']
        full_link = f"https://external-careers.jobs.unsw.edu.au{link}"  # Complete the link
        
        # Check if it already exists
        if not any(job['Job Title'] == title and job['Link'] == full_link for job in job_data):
            job_data.append({"Job Title": title, "Link": full_link})  # Add job information to the list

    print(f"Page {page} processed, found {len(job_links)} jobs.")  # Print the number of jobs found on the current page
    page += 1  # Increment page number

# Output all job data
print("All job data:")
print(job_data)  # Print job data

# Write job data to CSV file
csv_file_path = 'tables/unsw_job_listings.csv'
os.makedirs('tables', exist_ok=True)  # Ensure tables directory exists
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['Job Title', 'Link']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()  # Write header
    writer.writerows(job_data)

print(f"Job data has been successfully saved to {csv_file_path}")
