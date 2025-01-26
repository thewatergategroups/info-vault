# from dp.services.logger import logger
# from doctr.models import ocr_predictor
# from doctr.io import DocumentFile
# from typing import Dict, Any


# class OCRProcessingService:
#     def __init__(self):
#         self.logger = logger
#         try:
#             self.model = ocr_predictor(det_arch='db_resnet50', rec_arch='crnn_vgg16_bn')
#             self.logger.info("OCR Model loaded successfully")
#         except Exception as e:
#             self.logger.error(f"OCR Model Loading Error: {e}")
#             raise

#     #  TODO: Implement with database model
#     async def extract_metadata(self, file_path: str) -> Dict[str, Any]:
#         """
#         Extract comprehensive metadata from document
#         """
#         try:
#             doc = DocumentFile.from_path(file_path)
#             result = self.model(doc)

#             metadata = {
#                 "page_count": len(doc),
#                 "text_blocks": [
#                     {
#                         "text": block.value,
#                         "confidence": block.confidence
#                     } for block in result.pages[0].blocks
#                 ],
#                 "words": [
#                     {
#                         "text": word.value,
#                         "confidence": word.confidence
#                     } for word in result.pages[0].words
#                 ],
#                 "languages_detected": self._detect_languages(result)
#             }

#             return metadata

#         except Exception as e:
#             self.logger.error(f"OCR Metadata Extraction Error: {e}")
#             raise

#     def _detect_languages(self, result) -> list[str]:
#         # TODO: implement via langdetect
#         return ["en"]
