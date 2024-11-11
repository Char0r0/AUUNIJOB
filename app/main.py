import os
import sys
import importlib.util
import pandas as pd
from datetime import datetime
import logging
import concurrent.futures
import threading

# Set up logging configuration with thread safety
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Thread-safe print lock
print_lock = threading.Lock()

def import_module_from_file(file_path):
    """Dynamically import module from file path"""
    spec = importlib.util.spec_from_file_location("module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def scrape_university(scraper_file):
    """Scrape a single university's job listings"""
    uni_name = scraper_file[:-3].upper()
    logging.info(f"Starting to scrape {uni_name} job listings...")
    
    try:
        # Run the corresponding university scraper
        file_path = os.path.join('uniJobCatch', scraper_file)
        import_module_from_file(file_path)
        
        # Read generated CSV file
        csv_file = f'tables/{uni_name.lower()}_job_listings.csv'
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            if 'UniName' not in df.columns:
                df['UniName'] = uni_name
            with print_lock:
                logging.info(f"{uni_name} data scraping completed, found {len(df)} positions")
            return df
        
    except Exception as e:
        logging.error(f"Error processing {uni_name}: {str(e)}")
    return None

def run_scrapers():
    """Run all university job scraping scripts in parallel"""
    # Ensure output directory exists
    os.makedirs('tables', exist_ok=True)
    
    # Get all .py files from uniJobCatch directory
    scraper_files = [f for f in os.listdir('uniJobCatch') if f.endswith('.py')]
    all_jobs = []
    
    # Use ThreadPoolExecutor to run scrapers in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all scraping tasks
        future_to_uni = {executor.submit(scrape_university, scraper_file): scraper_file 
                        for scraper_file in scraper_files}
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_uni):
            result = future.result()
            if result is not None:
                all_jobs.append(result)
    
    if all_jobs:
        # Merge all data
        combined_df = pd.concat(all_jobs, ignore_index=True)
        
        # Add scraping timestamp
        combined_df['Scrape_Date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Save merged data to tables folder
        output_file = 'tables/job_data.csv'
        combined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logging.info(f"All job data has been saved to {output_file}")
        logging.info(f"Total positions found: {len(combined_df)}")
        
        # Print statistics
        with print_lock:
            print("\nJob Statistics by University:")
            print(combined_df['UniName'].value_counts())

if __name__ == "__main__":
    logging.info("Starting parallel job scraping program...")
    run_scrapers()
    logging.info("Program completed")
