from typing import Tuple
import pymupdf


class ResumeTextExtractor:
    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes) -> Tuple[str, bool]:
        """Extract text from PDF bytes.
        
        Returns:
            Tuple[str, bool]: (extracted_text, needs_ocr)
        """
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        full_text = []

        for page in doc:
            text = page.get_text()
            if text:
                full_text.append(text)

        joined_text = "\n".join(full_text).strip()
        doc.close()

        # If extracted text is less than 50 characters, PDF is likely scanned or image-based
        needs_ocr = len(joined_text) < 50
        return joined_text, needs_ocr
