import schedule
import time
from linkedin_scraper import LinkedInScraper
import logging
import os

def scrape_jobs():
    """Main function to scrape jobs."""
    try:
        print("Starting job scraping process...")
        scraper = LinkedInScraper()
        success = scraper.scrape()
        
        if success:
            print("Job scraping completed successfully")
            logging.info("Job scraping completed successfully")
        else:
            print("Job scraping failed. Check logs for details.")
            logging.error("Job scraping failed")
            
    except Exception as e:
        print(f"Error during job scraping: {str(e)}")
        logging.error(f"Error during job scraping: {str(e)}")

def main():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # Set up logging
    logging.basicConfig(
        filename='logs/scraper.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("Starting LinkedIn Job Scraper...")
    logging.info("Starting LinkedIn Job Scraper...")
    
    # Run immediately on startup
    scrape_jobs()
    
    # Schedule to run every two days
    schedule.every(2).days.at("09:00").do(scrape_jobs)
    
    print("Scheduler started. Will run every two days at 09:00 AM.")
    logging.info("Scheduler started. Will run every two days at 09:00 AM.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main() 