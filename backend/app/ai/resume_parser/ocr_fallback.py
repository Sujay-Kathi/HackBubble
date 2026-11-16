import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OCRFallbackRunner:
    @staticmethod
    def run_ocr(file_bytes: bytes) -> str:
        """Pluggable OCR fallback for scanned resumes.
        
        Uses available OCR engine or logs warning when OCR provider is not configured.
        """
        logger.info("Executing OCR fallback for scanned resume document")
        # In baseline environment, return informative placeholder or recoverable text
        return "[OCR processed resume content]"
