from flask import Flask, render_template, jsonify, request
from db_utils import get_all_appeals, get_conversation_by_appeal_uid, save_conversation, get_appeal_by_uid
from models import Appeal, SentimentEnum

app = Flask(__name__)

# === API для первой таблицы (обращения) ===
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
            'uid': a.original_uid or ''
        })
    return jsonify(data)

# === API для второй таблицы (переписка) ===
@app.route('/api/conversations')
def api_conversations():
    """Возвращает всю переписку"""
    from db_utils import get_all_conversations
    convs = get_all_conversations()
    data = []
    for c in convs:
        data.append({
            'id': c.id,
            'appeal_uid': c.appeal_uid,
            'operator_message': c.operator_message or '',
            'ai_response': c.ai_response or '',
            'operator_response': c.operator_response or '',
            'ai_confidence': c.ai_confidence or 0,
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M') if c.created_at else '',
            'updated_at': c.updated_at.strftime('%Y-%m-%d %H:%M') if c.updated_at else ''
        })
    return jsonify(data)

@app.route('/api/conversation/<uid>')
def api_conversation_by_uid(uid):
    """Возвращает переписку для конкретного обращения"""
    conv = get_conversation_by_appeal_uid(uid)
    if conv:
        return jsonify({
            'appeal_uid': conv.appeal_uid,
            'operator_message': conv.operator_message or '',
            'ai_response': conv.ai_response or '',
            'operator_response': conv.operator_response or '',
            'ai_confidence': conv.ai_confidence or 0
        })
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/conversation/<uid>', methods=['POST'])
def api_update_conversation(uid):
    """Обновляет или создаёт переписку"""
    data = request.json
    conv_data = {
        'appeal_uid': uid,
        'operator_message': data.get('operator_message', ''),
        'ai_response': data.get('ai_response', ''),
        'operator_response': data.get('operator_response', ''),
        'ai_confidence': data.get('ai_confidence', 0.0)
    }
    
    success = save_conversation(conv_data)
    if success:
        return jsonify({'status': 'ok'})
    return jsonify({'error': 'Failed to save'}), 500

# === Комбинированный API для тестирования ===
@app.route('/api/full-data')
def api_full_data():
    """Возвращает обращения вместе с перепиской"""
    from db_utils import get_all_appeals_with_conversations
    data = get_all_appeals_with_conversations()
    result = []
    for item in data:
        a = item['appeal']
        c = item['conversation']
        result.append({
            'appeal': {
                'date': a.received_date.strftime('%Y-%m-%d %H:%M'),
                'full_name': a.full_name,
                'phone': a.phone,
                'email': a.email,
                'uid': a.original_uid
            },
            'conversation': {
                'ai_response': c.ai_response if c else '',
                'ai_confidence': c.ai_confidence if c else 0
            } if c else None
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)