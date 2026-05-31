import sqlite3
import os
from datetime import datetime

DB_PATH = None

def get_db_path():
    global DB_PATH
    if DB_PATH is None:
        base_dir = os.path.dirname(__file__)
        instance_dir = os.path.join(base_dir, 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        DB_PATH = os.path.join(instance_dir, '4d_data.db')
    return DB_PATH

def init_db():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keputusan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarikh TEXT,
            syarikat TEXT,
            nombor4d TEXT,
            draw_ke TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_result(tarikh, syarikat, nombor4d, draw_ke=''):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO keputusan (tarikh, syarikat, nombor4d, draw_ke)
        VALUES (?, ?, ?, ?)
    ''', (tarikh, syarikat, nombor4d, draw_ke))
    conn.commit()
    conn.close()

def save_results_bulk(results):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO keputusan (tarikh, syarikat, nombor4d, draw_ke)
        VALUES (?, ?, ?, ?)
    ''', results)
    conn.commit()
    conn.close()

def get_results_by_company(syarikat, days=60):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT nombor4d, tarikh FROM keputusan 
        WHERE syarikat = ? AND tarikh >= date('now', ?)
        ORDER BY tarikh DESC
    ''', (syarikat, f'-{days} days'))
    
    data = cursor.fetchall()
    conn.close()
    return data  # Returns list of (nombor, tarikh)

def get_all_results_with_dates(syarikat):
    """Get all results with dates for a company"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT nombor4d, tarikh FROM keputusan 
        WHERE syarikat = ?
        ORDER BY tarikh DESC
    ''', (syarikat,))
    
    data = cursor.fetchall()
    conn.close()
    return data

def get_stats():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM keputusan')
    total_records = cursor.fetchone()[0]
    
    cursor.execute('SELECT DISTINCT syarikat FROM keputusan')
    companies = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT MIN(tarikh), MAX(tarikh) FROM keputusan')
    min_date, max_date = cursor.fetchone()
    
    conn.close()
    
    return {
        'total_records': total_records,
        'companies': companies,
        'date_range': {'from': min_date, 'to': max_date}
    }

def get_last_update_date():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('SELECT updated_at FROM metadata WHERE key = "last_update"')
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row[0]
    return 'Belum dikemaskini'

def set_last_update_date():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO metadata (key, value, updated_at)
        VALUES ('last_update', ?, CURRENT_TIMESTAMP)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
    conn.commit()
    conn.close()
