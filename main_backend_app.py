
# main_backend_app.py
import os
import uuid
import bcrypt
import logging
from flask import Flask, request, jsonify

from gcp_data_storage import GCPDataStorage
from crisis_detection_service import CrisisDetectionService
from gemini_service import GeminiService
from chatbot_service import ChatbotService

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# --- Service Initialization ---
# In a real deployment, these environment variables MUST be set.
storage_service = GCPDataStorage(
    project_id=os.environ.get("GCP_PROJECT_ID", "your-gcp-project-id"),
    conversation_bucket_name=os.environ.get("CONVERSATION_BUCKET_NAME", "your-convo-bucket"),
    crisis_contacts_bucket_name=os.environ.get("CRISIS_CONTACTS_BUCKET_NAME", "your-crisis-bucket"),
    users_bucket_name=os.environ.get("USERS_BUCKET_NAME", "your-users-bucket")
)
crisis_service = CrisisDetectionService()
gemini_service = GeminiService(api_key=os.environ.get("GEMINI_API_KEY", "your-gemini-api-key"))
chatbot_service = ChatbotService(
    storage=storage_service,
    crisis_detector=crisis_service,
    model=gemini_service,
    contacts_file=os.environ.get("CRISIS_CONTACTS_FILE_NAME", "crisis_contacts.json")
)

# --- API Endpoints ---
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    if storage_service.get_user(data['email']):
        return jsonify({'error': 'User already exists'}), 409
    
    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_data = {'user_id': str(uuid.uuid4()), 'email': data['email'], 'password_hash': hashed}
    storage_service.save_user(user_data)
    return jsonify({'user_id': user_data['user_id'], 'email': user_data['email']}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = storage_service.get_user(data['email'])
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({'user_id': user['user_id'], 'email': user['email']}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    response = chatbot_service.handle_message(data['user_id'], data['message'], data.get('conversation_id'))
    return jsonify(response)

# A simple health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
