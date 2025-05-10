# LinkedIn Jobs Scraper for Israel

This project automatically scrapes LinkedIn job postings for software internships and computer science positions in Israel, saving them to an Excel file and sending email notifications.

## Features

- Daily scraping of LinkedIn jobs at 6 PM
- Filters for software internships and computer science positions
- Excludes jobs older than 2 weeks
- Saves data to Excel with daily updates
- Email notifications for new jobs
- GitHub Actions automation

## Setup Instructions

1. **Environment Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configuration**
   - Create a `.env` file with your credentials:
     ```
     LINKEDIN_EMAIL=your_linkedin_email
     LINKEDIN_PASSWORD=your_linkedin_password
     GMAIL_EMAIL=your_gmail_email
     GMAIL_APP_PASSWORD=your_gmail_app_password
     ```

3. **Running the Script**
   ```bash
   python main.py
   ```

## File Structure

- `main.py`: Main script for job scraping
- `config.py`: Configuration settings
- `linkedin_scraper.py`: LinkedIn scraping functionality
- `email_sender.py`: Email notification system
- `data/`: Directory for Excel files
- `logs/`: Directory for log files

## GitHub Actions

The script runs automatically at 6 PM daily using GitHub Actions. The workflow is configured in `.github/workflows/daily_scrape.yml`.

## Data Storage

Job listings are stored in Excel files in the `data` directory, with a new sheet added daily. 