import requests
from bs4 import BeautifulSoup
from datetime import datetime
import database as db
import re

def scrape_4dmoon_top3():
    """Scrape ONLY 1st, 2nd, 3rd Prize from 4dmoon.com"""
    results = {'Magnum': [], 'Toto': [], 'Kuda': []}
    
    try:
        url = "https://www.4dmoon.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.text
        
        # ============================================
        # SCRAPE MAGNUM 1st, 2nd, 3rd PRIZE
        # ============================================
        magnum_pattern = r'Magnum 4D.*?1st Prize\s*(\d{4})\s*2nd Prize\s*(\d{4})\s*3rd Prize\s*(\d{4})'
        match = re.search(magnum_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            results['Magnum'] = [match.group(1), match.group(2), match.group(3)]
            print(f"  Magnum TOP 3: {results['Magnum']}")
        
        # ============================================
        # SCRAPE SPORTS TOTO 1st, 2nd, 3rd PRIZE
        # ============================================
        toto_pattern = r'SportsToto 4D.*?1st Prize\s*(\d{4})\s*2nd Prize\s*(\d{4})\s*3rd Prize\s*(\d{4})'
        match = re.search(toto_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            results['Toto'] = [match.group(1), match.group(2), match.group(3)]
            print(f"  Toto TOP 3: {results['Toto']}")
        
        # ============================================
        # SCRAPE GRAND DRAGON/KUDA 1st, 2nd, 3rd PRIZE
        # ============================================
        kuda_pattern = r'Grand Dragon 4D.*?1st Prize\s*(\d{4})\s*2nd Prize\s*(\d{4})\s*3rd Prize\s*(\d{4})'
        match = re.search(kuda_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            results['Kuda'] = [match.group(1), match.group(2), match.group(3)]
            print(f"  Kuda TOP 3: {results['Kuda']}")
        
        # If patterns above fail, try alternative method
        if not any(results.values()):
            # Find all "1st Prize", "2nd Prize", "3rd Prize" patterns
            prize_pattern = r'(?:1st|2nd|3rd)\s+Prize\s*(\d{4})'
            all_prizes = re.findall(prize_pattern, text)
            
            # Distribute to companies (first 3 = Magnum, next 3 = Toto, next 3 = Kuda)
            if len(all_prizes) >= 9:
                results['Magnum'] = all_prizes[0:3]
                results['Toto'] = all_prizes[3:6]
                results['Kuda'] = all_prizes[6:9]
                print(f"  Alternative method: Magnum={results['Magnum']}, Toto={results['Toto']}, Kuda={results['Kuda']}")
        
    except Exception as e:
        print(f"  Scrape error: {e}")
    
    return results

def update_current_week_data():
    """Update with current week's TOP 3 data from 4dmoon"""
    print("Fetching TOP 3 data from 4dmoon.com...")
    
    scraped_data = scrape_4dmoon_top3()
    today = datetime.now().strftime('%Y-%m-%d')
    
    results_batch = []
    
    for syarikat, numbers in scraped_data.items():
        for num in numbers:
            if num:  # Only if number exists
                results_batch.append((today, syarikat, num, 'TOP 3 Prize'))
    
    if results_batch:
        db.save_results_bulk(results_batch)
        print(f"Saved {len(results_batch)} TOP 3 records")
    else:
        print("WARNING: No TOP 3 data scraped!")
    
    return len(results_batch)

def update_all_data():
    """Main function - scrape ONLY TOP 3 prizes from 4dmoon"""
    print("=" * 50)
    print("Scraping ONLY 1st, 2nd, 3rd Prize from 4dmoon.com...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Initialize database
    db.init_db()
    
    # Scrape current TOP 3 data
    update_current_week_data()
    
    # Update metadata
    db.set_last_update_date()
    
    # Show stats
    stats = db.get_stats()
    print("-" * 50)
    print(f"Update Complete!")
    print(f"Total records in database: {stats['total_records']}")
    print(f"Companies: {', '.join(stats['companies'])}")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    update_all_data()
