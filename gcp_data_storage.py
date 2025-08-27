
# gcp_data_storage.py
from google.cloud import storage
import json
import logging

logger = logging.getLogger(__name__)

class GCPDataStorage:
    def __init__(self, project_id: str, conversation_bucket_name: str, crisis_contacts_bucket_name: str, users_bucket_name: str):
        self.client = storage.Client(project=project_id)
        self.conversation_bucket = self.client.bucket(conversation_bucket_name)
        self.crisis_contacts_bucket = self.client.bucket(crisis_contacts_bucket_name)
        self.users_bucket = self.client.bucket(users_bucket_name)

    def _upload_json(self, bucket, blob_name, data):
        blob = bucket.blob(blob_name)
        blob.upload_from_string(json.dumps(data, indent=2), content_type='application/json')

    def _download_json(self, bucket, blob_name):
        blob = bucket.blob(blob_name)
        return json.loads(blob.download_as_string()) if blob.exists() else None

    def save_conversation(self, convo_id, data):
        self._upload_json(self.conversation_bucket, f"{convo_id}.json", data)

    def get_conversation(self, convo_id):
        return self._download_json(self.conversation_bucket, f"{convo_id}.json")
        
    def get_crisis_contacts(self, filename):
        return self._download_json(self.crisis_contacts_bucket, filename)

    def get_user(self, email):
        return self._download_json(self.users_bucket, f"user_{email}.json")

    def save_user(self, data):
        self._upload_json(self.users_bucket, f"user_{data['email']}.json", data)
