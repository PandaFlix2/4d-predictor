import database as db
from datetime import datetime, timedelta

def check_winning_numbers(ramalan_list, keputusan_actual):
    """
    Check which predicted numbers actually won
    """
    matches = []
    for nombor in ramalan_list:
        if nombor in keputusan_actual:
            matches.append(nombor)
    return matches

def get_last_draw_results(syarikat, days_back=7):
    """
    Get actual draw results from last 7 days
    """
    conn = sqlite3.connect(db.get_db_path())
    cursor = conn.cursor()
    
    cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT nombor4d, tarikh FROM keputusan 
        WHERE syarikat = ? AND tarikh >= ?
        ORDER BY tarikh DESC
    ''', (syarikat, cutoff_date))
    
    results = cursor.fetchall()
    conn.close()
    return results

def calculate_accuracy(ramalan_list, actual_results):
    """
    Calculate prediction accuracy percentage
    """
    if not actual_results:
        return 0
    
    actual_numbers = [r[0] for r in actual_results]
    matches = check_winning_numbers(ramalan_list, actual_numbers)
    
    accuracy = (len(matches) / len(ramalan_list)) * 100 if ramalan_list else 0
    return {
        'accuracy': round(accuracy, 2),
        'matches': matches,
        'total_predicted': len(ramalan_list),
        'total_actual': len(actual_numbers)
    }