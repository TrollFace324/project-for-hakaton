from flask import Flask, render_template, jsonify
from db_utils import get_all_appeals
from models import Appeal, SentimentEnum

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('appeals_table.html')

@app.route('/api/appeals')
def api_appeals():
    appeals = get_all_appeals()
    data = []
    for a in appeals:
        data.append({
            'id': a.id,
            'date': a.received_date.strftime('%Y-%m-%d %H:%M'),
            'full_name': a.full_name or '',
            'facility': a.facility or '',
            'phone': a.phone or '',
            'email': a.email or '',
            'serials': a.device_serial_numbers or '',
            'device_type': a.device_type or '',
            'sentiment': a.sentiment.value if a.sentiment else 'нейтраль',
            'issue': a.issue_description or '',
            'uid': a.original_uid or '',  # 🔥 НОВОЕ
            'confidence': a.confidence_score or 0  # 🔥 НОВОЕ
        })
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)