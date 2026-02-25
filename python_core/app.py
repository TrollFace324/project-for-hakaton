from flask import Flask, render_template, jsonify
from db_utils import get_all_emails
from models import Email  # для сериализации

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/emails')
def api_emails():
    emails = get_all_emails()
    # Превращаем объекты в словари
    data = []
    for email in emails:
        data.append({
            'id': email.id,
            'subject': email.subject,
            'sender': email.sender,
            'received_date': email.received_date.strftime('%Y-%m-%d %H:%M:%S'),
            'body': email.body[:100] + '...' if len(email.body) > 100 else email.body
        })
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True) 