from collections import Counter
import database as db

def analyze_hot_numbers(syarikat, days=60, top_n=20):
    """Analyze most frequent numbers with their last seen date"""
    results = db.get_results_by_company(syarikat, days)
    
    if not results:
        return []
    
    # Separate numbers and dates
    numbers = [r[0] for r in results]
    date_map = {}
    for num, date in results:
        if num not in date_map:
            date_map[num] = date
    
    frequency = Counter(numbers)
    total_draws = len(numbers)
    
    hot_numbers = []
    for number, freq in frequency.most_common(top_n):
        percentage = (freq / total_draws) * 100
        hot_numbers.append({
            'nombor': number,
            'frekuensi': freq,
            'peratusan': round(percentage, 2),
            'tarikh_terakhir': date_map.get(number, 'Tiada'),
            'label': '🔥 Hot'
        })
    
    return hot_numbers

def get_predictions_for_week():
    """Get weekly predictions with dates"""
    predictions = {}
    
    for syarikat in ['Magnum', 'Toto', 'Kuda']:
        hot = analyze_hot_numbers(syarikat, days=60, top_n=15)
        predictions[syarikat] = hot[:15]
    
    return predictions
