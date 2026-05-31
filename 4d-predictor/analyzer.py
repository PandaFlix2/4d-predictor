from collections import Counter
import database as db

def analyze_hot_numbers(syarikat, days=60, top_n=20):
    results = db.get_results_by_company(syarikat, days)
    
    if not results:
        return []
    
    frequency = Counter(results)
    total_draws = len(results)
    
    hot_numbers = []
    for number, freq in frequency.most_common(top_n):
        percentage = (freq / total_draws) * 100
        hot_numbers.append({
            'nombor': number,
            'frekuensi': freq,
            'peratusan': round(percentage, 2),
            'label': '🔥 Hot'
        })
    
    return hot_numbers

def get_trending_up(syarikat):
    recent = Counter(db.get_results_by_company(syarikat, days=30))
    previous = Counter(db.get_results_by_company(syarikat, days=60, offset=30))
    
    trending = []
    for number in recent:
        recent_freq = recent[number]
        prev_freq = previous.get(number, 0)
        
        if recent_freq > prev_freq:
            increase = ((recent_freq - prev_freq) / max(prev_freq, 1)) * 100
            trending.append({
                'nombor': number,
                'kenaikan': round(increase, 1),
                'recent_freq': recent_freq
            })
    
    return sorted(trending, key=lambda x: x['kenaikan'], reverse=True)[:10]

def get_predictions_for_week():
    predictions = {}
    
    for syarikat in ['Magnum', 'Toto', 'Kuda']:
        hot = analyze_hot_numbers(syarikat, days=60, top_n=15)
        trending = get_trending_up(syarikat)
        
        combined = []
        seen = set()
        
        for item in hot[:12]:
            if item['nombor'] not in seen:
                combined.append(item)
                seen.add(item['nombor'])
        
        for item in trending[:8]:
            if item['nombor'] not in seen:
                combined.append({
                    'nombor': item['nombor'],
                    'frekuensi': item['recent_freq'],
                    'peratusan': round((item['recent_freq'] / 30) * 100, 2),
                    'label': '📈 Trending'
                })
                seen.add(item['nombor'])
        
        predictions[syarikat] = combined[:20]
    
    return predictions