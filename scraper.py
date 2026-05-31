import requests
from bs4 import BeautifulSoup
from datetime import datetime
import database as db
import re

def scrape_4dmoon_top3():
    """Scrape ONLY 1st, 2nd, 3rd Prize from 4dmoon.com - NO DEMO NUMBERS"""
    results = {'Magnum': [], 'Toto': [], 'Kuda': []}
    
    try:
        url = "https://www.4dmoon.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        text = response.text
        
        # ============================================
        # SCRAPE MAGNUM 4D - Look for exact pattern
        # ============================================
        # Pattern: "Magnum 4D" then find 3 four-digit numbers in sequence
        magnum_match = re.search(r'Magnum 4D.*?(\d{4}).*?(\d{4}).*?(\d{4})', text, re.DOTALL | re.IGNORECASE)
        if magnum_match:
            results['Magnum'] = [magnum_match.group(1), magnum_match.group(2), magnum_match.group(3)]
            print(f"  ✓ Magnum: {results['Magnum']}")
        
        # ============================================
        # SCRAPE SPORTS TOTO 4D
        # ============================================
        toto_match = re.search(r'SportsToto 4D.*?(\d{4}).*?(\d{4}).*?(\d{4})', text, re.DOTALL | re.IGNORECASE)
        if toto_match:
            results['Toto'] = [toto_match.group(1), toto_match.group(2), toto_match.group(3)]
            print(f"  ✓ Toto: {results['Toto']}")
        
        # ============================================
        # SCRAPE GRAND DRAGON / KUDA
        # ============================================
        kuda_match = re.search(r'Grand Dragon 4D.*?(\d{4}).*?(\d{4}).*?(\d{4})', text, re.DOTALL | re.IGNORECASE)
        if kuda_match:
            results['Kuda'] = [kuda_match.group(1), kuda_match.group(2), kuda_match.group(3)]
            print(f"  ✓ Kuda: {results['Kuda']}")
        
        # ============================================
        # If any company has no data, leave as empty list
        # ============================================
        for company in results:
            if not results[company]:
                print(f"  ✗ {company}: No data scraped")
        
    except Exception as e:
        print(f"  ✗ Scrape error: {e}")
        # Return empty results - NO DEMO NUMBERS
        results = {'Magnum': [], 'Toto': [], 'Kuda': []}
    
    return results

def update_current_week_data():
    """Update with current week's TOP 3 data from 4dmoon - NO DEMO"""
    print("Fetching TOP 3 data from 4dmoon.com...")
    
    scraped_data = scrape_4dmoon_top3()
    today = datetime.now().strftime('%Y-%m-%d')
    
    results_batch = []
    
    for syarikat, numbers in scraped_data.items():
        for num in numbers:
            if num and len(num) == 4:
                results_batch.append((today, syarikat, num, 'TOP 3 Prize'))
    
    if results_batch:
        # Clear old data to keep only latest
        import sqlite3
        conn = sqlite3.connect(db.get_db_path())
        cursor = conn.cursor()
        cursor.execute("DELETE FROM keputusan")
        conn.commit()
        conn.close()
        
        # Save new data
        db.save_results_bulk(results_batch)
        print(f"✅ Saved {len(results_batch)} TOP 3 records")
    else:
        print("❌ No TOP 3 data scraped. Database remains empty.")
    
    return len(results_batch)

def update_all_data():
    """Main function - scrape ONLY TOP 3 prizes from 4dmoon (NO DEMO)"""
    print("=" * 50)
    print("Scraping 1st, 2nd, 3rd Prize from 4dmoon.com...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Initialize database
    db.init_db()
    
    # Scrape current TOP 3 data
    record_count = update_current_week_data()
    
    if record_count > 0:
        db.set_last_update_date()
    else:
        print("⚠️ No data scraped. Last update date not changed.")
    
    # Show stats
    stats = db.get_stats()
    print("-" * 50)
    print(f"Update Complete!")
    print(f"Total records in database: {stats['total_records']}")
    print(f"Companies: {', '.join(stats['companies']) if stats['companies'] else 'None'}")
    print("=" * 50)
    
    return record_count > 0

if __name__ == "__main__":
    update_all_data()
