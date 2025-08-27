
# crisis_detection_service.py
import logging

logger = logging.getLogger(__name__)

class CrisisDetectionService:
    def __init__(self):
        self.crisis_keywords = [
            "suicide", "kill myself", "harm myself", "want to die", "ending my life",
            "hopeless", "end it all", "can't go on", "no reason to live", "self-harm",
        ]
        logger.info(f"CrisisDetectionService initialized with {len(self.crisis_keywords)} keywords.")

    def detect_crisis(self, message: str) -> bool:
        processed_message = message.lower()
        return any(keyword in processed_message for keyword in self.crisis_keywords)
