from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
import os
from config import (
    LINKEDIN_EMAIL, LINKEDIN_PASSWORD, JOB_KEYWORDS,
    LOCATION, MAX_DAYS_OLD, EXCEL_FILE
)

# Set up logging
logging.basicConfig(
    filename='logs/scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LinkedInScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Set up the Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        # Remove headless mode to improve reliability
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def login(self):
        """Log in to LinkedIn."""
        try:
            print("Starting LinkedIn login process...")
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(5)  # Wait longer for page to load completely
            
            # Wait for email field and enter email
            print("Entering email...")
            email_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            email_field.clear()  # Clear any existing text
            email_field.send_keys(LINKEDIN_EMAIL)
            time.sleep(2)  # Small delay between actions

            # Enter password
            print("Entering password...")
            password_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, 'password'))
            )
            password_field.clear()  # Clear any existing text
            password_field.send_keys(LINKEDIN_PASSWORD)
            time.sleep(2)  # Small delay between actions

            # Click login button
            print("Clicking login button...")
            login_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
            )
            login_button.click()

            # Wait for login to complete and verify we're on the main page
            print("Waiting for login to complete...")
            try:
                # Wait for either the feed or the nav bar to appear
                WebDriverWait(self.driver, 30).until(
                    lambda driver: (
                        len(driver.find_elements(By.CSS_SELECTOR, 'nav.global-nav')) > 0 or
                        len(driver.find_elements(By.CSS_SELECTOR, '.feed-shared-update-v2')) > 0 or
                        'feed' in driver.current_url.lower() or
                        'jobs' in driver.current_url.lower() or
                        len(driver.find_elements(By.CSS_SELECTOR, '.jobs-search-results-list')) > 0
                    )
                )
                
                # Additional verification
                if "login" in self.driver.current_url.lower():
                    print("Still on login page, login might have failed")
                    return False
                    
                print("Successfully logged in to LinkedIn")
                time.sleep(5)  # Wait for the page to fully load after login
                return True
                
            except Exception as e:
                print(f"Login verification failed: {str(e)}")
                # Take a screenshot for debugging
                try:
                    self.driver.save_screenshot('login_error.png')
                    print("Saved screenshot to login_error.png")
                except:
                    pass
                return False
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            # Take a screenshot for debugging
            try:
                self.driver.save_screenshot('login_error.png')
                print("Saved screenshot to login_error.png")
            except:
                pass
            return False

    def search_jobs(self, keyword):
        """Search for jobs with the given keyword."""
        try:
            # Construct search URL with proper encoding and filters
            encoded_keyword = keyword.replace(' ', '%20')
            encoded_location = LOCATION.replace(' ', '%20')
            search_url = f'https://www.linkedin.com/jobs/search/?keywords={encoded_keyword}&location={encoded_location}&f_TPR=r1209600'
            
            print(f"\nSearching for jobs with keyword: {keyword}")
            print(f"Search URL: {search_url}")
            
            # Navigate to search URL
            self.driver.get(search_url)
            time.sleep(5)  # Wait for page to load
            
            # First check if there are no matching jobs
            try:
                no_jobs_element = self.driver.find_element(By.CSS_SELECTOR, 'h1.t-24.t-black.t-normal.text-align-center')
                if "No matching jobs found" in no_jobs_element.text:
                    print("No matching jobs found for this keyword, skipping to next search...")
                    return False
            except:
                # If we can't find the no results text, continue with normal search
                pass
            
            # If we get here, there might be jobs, so wait for them to appear
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a.job-card-list__title--link'))
                )
                print("Found job results!")
                return True
            except Exception as e:
                print(f"Failed to find job results: {str(e)}")
                return False
            
        except Exception as e:
            print(f"Job search failed: {str(e)}")
            return False

    def extract_job_data(self):
        """Extract job data from the current page."""
        jobs = []
        try:
            # Wait a bit to ensure all jobs are loaded
            time.sleep(3)
            
            # Find all job link elements
            job_links = self.driver.find_elements(By.CSS_SELECTOR, 'a.job-card-list__title--link')
            print(f"Found {len(job_links)} job links")
            
            if not job_links:
                print("No job links found")
                return jobs

            for link_element in job_links:
                try:
                    # Scroll element into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", link_element)
                    time.sleep(1)
                    
                    # Get title from aria-label and link from href
                    title = link_element.get_attribute('aria-label')
                    link = link_element.get_attribute('href')
                    
                    if title and link:
                        jobs.append({
                            'title': title,
                            'link': link
                        })
                        print(f"Added job: {title}")
                        print(f"Link: {link}")
                    
                except Exception as e:
                    print(f"Failed to extract job: {str(e)}")
                    continue

            print(f"Successfully extracted {len(jobs)} jobs")
            return jobs

        except Exception as e:
            print(f"Failed to extract job data: {str(e)}")
            return jobs

    def parse_posting_date(self, date_text):
        """Parse the posting date text into a datetime object."""
        try:
            if 'hour' in date_text or 'hours' in date_text:
                hours = int(date_text.split()[0])
                return datetime.now() - timedelta(hours=hours)
            elif 'day' in date_text or 'days' in date_text:
                days = int(date_text.split()[0])
                return datetime.now() - timedelta(days=days)
            elif 'week' in date_text or 'weeks' in date_text:
                weeks = int(date_text.split()[0])
                return datetime.now() - timedelta(weeks=weeks)
            elif 'month' in date_text or 'months' in date_text:
                months = int(date_text.split()[0])
                return datetime.now() - timedelta(days=months * 30)
            else:
                return datetime.now()
        except:
            return datetime.now()

    def save_to_excel(self, jobs):
        """Save job data to Excel file and commit to git."""
        try:
            if not jobs:
                print("No jobs to save")
                return False
                
            # Create DataFrame
            df = pd.DataFrame(jobs)
            
            # Add timestamp
            df['scraped_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save to Excel file with better formatting
            excel_file = 'linkedin_jobs.xlsx'
            try:
                # Read existing data if file exists
                if os.path.exists(excel_file):
                    existing_df = pd.read_excel(excel_file)
                    # Combine with new data
                    combined_df = pd.concat([existing_df, df], ignore_index=True)
                else:
                    combined_df = df
                
                # Remove duplicates based on title and link
                combined_df = combined_df.drop_duplicates(subset=['title', 'link'], keep='first')
                
                # Save to Excel with formatting
                with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                    combined_df.to_excel(writer, index=False, sheet_name='Jobs')
                    # Auto-adjust column widths
                    worksheet = writer.sheets['Jobs']
                    for idx, col in enumerate(combined_df.columns):
                        max_length = max(
                            combined_df[col].astype(str).apply(len).max(),
                            len(col)
                        )
                        worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 100)
                
                print(f"Saved {len(jobs)} jobs to {excel_file}")
                
                # Git operations
                try:
                    import subprocess
                    print("\nStarting git operations...")
                    
                    # Configure git user if not already configured
                    try:
                        subprocess.run(['git', 'config', '--get', 'user.name'], check=True)
                    except:
                        print("Configuring git user...")
                        subprocess.run(['git', 'config', 'user.name', 'LinkedIn Job Scraper'], check=True)
                        subprocess.run(['git', 'config', 'user.email', 'scraper@example.com'], check=True)
                    
                    # Add the Excel file
                    print("Adding Excel file to git...")
                    subprocess.run(['git', 'add', excel_file], check=True)
                    
                    # Check if there are changes to commit
                    status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
                    if status.stdout.strip():
                        # Commit with timestamp
                        commit_message = f"Update job listings - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
                        print("Successfully committed changes to git")
                        
                        # Try to push if remote exists
                        try:
                            subprocess.run(['git', 'push'], check=True)
                            print("Successfully pushed to remote repository")
                        except Exception as e:
                            print(f"Push failed: {str(e)}")
                            print("No remote repository configured or push failed")
                    else:
                        print("No changes to commit")
                    
                except Exception as e:
                    print(f"Git operations failed: {str(e)}")
                    print("Continuing without git commit...")
                
                return True
                
            except Exception as e:
                print(f"Failed to save to Excel file: {str(e)}")
                return False
            
        except Exception as e:
            print(f"Failed to save jobs: {str(e)}")
            return False

    def test_google_sheets(self):
        """Test Google Sheets access by writing a test row."""
        try:
            print("\nTesting Google Sheets access...")
            
            # Check if credentials file exists
            if not os.path.exists('credentials.json'):
                print("Error: credentials.json file not found!")
                return False
                
            # Set up credentials
            import gspread
            from google.oauth2.service_account import Credentials
            
            scope = ['https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive']
            
            print("Loading credentials...")
            creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
            
            print("Authorizing with Google...")
            client = gspread.authorize(creds)
            
            print("Opening spreadsheet...")
            try:
                sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/17MUOxp8GwaJMA1YYpQkNulNavZlnmRQwh4K3TyAhXvM/edit?usp=sharing')
            except Exception as e:
                print(f"Error opening spreadsheet: {str(e)}")
                print("Please make sure:")
                print("1. The spreadsheet URL is correct")
                print("2. The spreadsheet is shared with the service account email")
                return False
            
            print("Getting worksheet...")
            worksheet = sheet.get_worksheet(0)
            
            # Create test data
            test_data = {
                'title': 'Test Job',
                'link': 'https://test.com',
                'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            print("Writing test data...")
            # Get existing data
            existing_data = worksheet.get_all_values()
            if existing_data:
                # Add to existing data
                next_row = len(existing_data) + 1
                worksheet.update(f'A{next_row}', [list(test_data.values())])
            else:
                # Create new sheet with headers
                worksheet.update('A1', [list(test_data.keys())])
                worksheet.update('A2', [list(test_data.values())])
            
            print("Test data written successfully!")
            print("Please check your Google Sheet to verify the test data was added.")
            return True
            
        except Exception as e:
            print(f"Google Sheets test failed: {str(e)}")
            print("Error details:", e.__class__.__name__)
            return False

    def scrape(self):
        """Main scraping function."""
        try:
            # Login first
            if not self.login():
                print("Failed to login to LinkedIn")
                return False

            print("Starting job search process...")
            all_jobs = []
            
            for keyword in JOB_KEYWORDS:
                try:
                    print(f"\nSearching for: {keyword}")
                    
                    # Search for jobs
                    if not self.search_jobs(keyword):
                        continue
                    
                    # Extract job data
                    jobs = self.extract_job_data()
                    if jobs:
                        all_jobs.extend(jobs)
                        print(f"Found {len(jobs)} jobs for {keyword}")
                    
                    time.sleep(2)  # Short wait between searches
                    
                except Exception as e:
                    print(f"Error with keyword {keyword}: {str(e)}")
                    continue

            # Save results if any jobs were found
            if all_jobs:
                if self.save_to_excel(all_jobs):
                    print(f"\nSaved {len(all_jobs)} jobs to Google Sheets")
                    return True
                else:
                    print("Failed to save jobs to Google Sheets")
                    return False
            else:
                print("No jobs found")
                return False

        except Exception as e:
            print(f"Scraping failed: {str(e)}")
            return False
        finally:
            self.close()

    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit() 