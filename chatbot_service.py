
# chatbot_service.py
from datetime import datetime
import uuid
from gcp_data_storage import GCPDataStorage
from crisis_detection_service import CrisisDetectionService
from gemini_service import GeminiService

class ChatbotService:
    def __init__(self, storage: GCPDataStorage, crisis_detector: CrisisDetectionService, model: GeminiService, contacts_file: str):
        self.storage = storage
        self.crisis_detector = crisis_detector
        self.model = model
        self.contacts_file = contacts_file

    def _log_message(self, convo_id, user_id, sender, text):
        convo = self.storage.get_conversation(convo_id) or {
            "conversation_id": convo_id, "user_id": user_id, "start_time": datetime.utcnow().isoformat(), "messages": []
        }
        convo["messages"].append({"sender": sender, "text": text, "timestamp": datetime.utcnow().isoformat()})
        self.storage.save_conversation(convo_id, convo)
        
    def handle_message(self, user_id, message, convo_id=None):
        convo_id = convo_id or str(uuid.uuid4())
        self._log_message(convo_id, user_id, "user", message)
        
        if self.crisis_detector.detect_crisis(message):
            contacts = self.storage.get_crisis_contacts(self.contacts_file)
            response_text = "It sounds like you're going through a difficult time. Please reach out for help."
            self._log_message(convo_id, user_id, "chatbot", response_text)
            return {"conversation_id": convo_id, "message": response_text, "response_type": "crisis", "crisis_contacts": contacts or []}
        
        response_text = self.model.generate_response(message)
        self._log_message(convo_id, user_id, "chatbot", response_text)
        return {"conversation_id": convo_id, "message": response_text, "response_type": "chat"}
