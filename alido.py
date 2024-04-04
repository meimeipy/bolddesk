import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/restore-tickets', methods=['POST'])
def restore_tickets():
    ticket_ids = request.json.get('ticketIdList')
    if not ticket_ids or len(ticket_ids) > 100:
        return jsonify({'error': 'Invalid ticketIdList'}), 400

    api_url = "https://vittel.bolddesk.com/api/v1/tickets/restore"
    api_key = "mYmIMgJNC0/aayRpdqcaYKoh+O+E2Jta6WbGl+Z8zyU="
    headers = {
        "x-api-key": api_key, "Content-Type": "application/json"
    }
    data = {'ticketIdList': ticket_ids}
    response = requests.post(api_url, headers=headers, json=data)
    print(response.text)
    if response.status_code == 200:
        return response.json()
    else:
        return jsonify({'error': 'API request failed'}), response.status_code
if __name__ == '__main__':  
    app.run(debug=True)
    