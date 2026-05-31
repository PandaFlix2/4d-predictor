from flask import Flask, render_template, jsonify
import database as db
import analyzer as az
import scraper as sc
import os
from datetime import datetime

app = Flask(__name__)

# Setup database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
os.makedirs(INSTANCE_DIR, exist_ok=True)
db.DB_PATH = os.path.join(INSTANCE_DIR, '4d_data.db')

# Initialize database on startup
db.init_db()

@app.route('/')
def index():
    """Main page - show predictions"""
    predictions = az.get_predictions_for_week()
    last_update = db.get_last_update_date()
    return render_template('index.html', 
                         predictions=predictions, 
                         last_update=last_update)

@app.route('/api/predictions')
def api_predictions():
    """API endpoint for predictions (JSON)"""
    return jsonify(az.get_predictions_for_week())

@app.route('/api/hot/<syarikat>')
def api_hot(syarikat):
    if syarikat not in ['Magnum', 'Toto', 'Kuda']:
        return jsonify({'error': 'Invalid company'}), 400
    return jsonify(az.analyze_hot_numbers(syarikat))

@app.route('/api/trending/<syarikat>')
def api_trending(syarikat):
    if syarikat not in ['Magnum', 'Toto', 'Kuda']:
        return jsonify({'error': 'Invalid company'}), 400
    return jsonify(az.get_trending_up(syarikat))

@app.route('/update')
def update_data():
    try:
        sc.update_all_data()
        return jsonify({
            'status': 'success', 
            'message': 'Data berjaya dikemaskini!',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/stats')
def stats():
    return jsonify(db.get_stats())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)