#!/usr/bin/env python3
"""
Discourse Scraper Script for TDS Virtual TA
Usage: python scraper_script.py [start_date] [end_date]
Example: python scraper_script.py 2025-01-01 2025-04-14
"""

import sys
import os
from datetime import datetime
from scraper.discourse_scraper import DiscourseScraper
from config import Config

def main():
    # Parse command line arguments
    if len(sys.argv) >= 3:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
    else:
        start_date = Config.START_DATE
        end_date = Config.END_DATE
    
    # Validate date format
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format")
        sys.exit(1)
    
    print(f"Scraping Discourse posts from {start_date} to {end_date}")
    print(f"Course URL: {Config.TDS_COURSE_URL}")
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Initialize scraper
    scraper = DiscourseScraper(Config.DISCOURSE_BASE_URL, Config.TDS_COURSE_URL)
    
    # Scrape posts
    try:
        posts = scraper.scrape_all_posts(start_date, end_date)
        
        if posts:
            # Save to file
            filename = f"data/discourse_posts_{start_date}_to_{end_date}.json"
            scraper.save_posts_to_file(posts, filename)
            
            # Also save as the default filename
            scraper.save_posts_to_file(posts, "data/discourse_posts.json")
            
            print(f"\nScraping completed successfully!")
            print(f"Total posts scraped: {len(posts)}")
            print(f"Data saved to: {filename}")
            
            # Print sample of what was found
            print(f"\nSample posts found:")
            for i, post in enumerate(posts[:3]):
                print(f"{i+1}. {post.get('topic_title', 'No title')}")
                print(f"   By: {post.get('username', 'Unknown')}")
                print(f"   Content preview: {post.get('raw_content', '')[:100]}...")
                print()
            
        else:
            print("No posts found in the specified date range.")
            
    except Exception as e:
        print(f"Error during scraping: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()