from minio import Minio
from minio.error import S3Error
import uuid
from typing import BinaryIO
from dp.types import ObjectStorageSettings
from dp.services.logger import logger


class MinIOStorageService():
    def __init__(self, settings: ObjectStorageSettings):
        self.logger = logger
        self.settings: ObjectStorageSettings = settings
        self.client = Minio(
            settings.os_settings.os_endpoint,
            access_key=settings.os_settings.os_access_key,
            secret_key=settings.os_settings.os_secret_key,
            secure=False,
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.settings.os_endpoint):
                self.client.make_bucket(self.settings.os_endpoint)
                self.logger.info(f"Created bucket: {self.settings.os_endpoint}")
        except S3Error as e:
            self.logger.error(f"MinIO Bucket Creation Error: {e}")
            raise

    async def upload_file(
        self,
        file: BinaryIO,
        filename: str = None,
        content_type: str = None
    ) -> str:
        """
        Upload a file to MinIO with unique naming and optional content type

        Args:
            file (BinaryIO): File-like object to upload
            filename (str, optional): Original filename
            content_type (str, optional): MIME content type

        Returns:
            str: Unique object path in storage
        """
        try:
            unique_filename = f"{uuid.uuid4()}_{filename or 'unknown_file'}"

            self.client.put_object(
                bucket_name=self.settings.os_endpoint,
                object_name=unique_filename,
                data=file,
                length=file.seek(0, 2),  # Get file size
                content_type=content_type
            )

            self.logger.info(f"File uploaded: {unique_filename}")
            return unique_filename

        except S3Error as e:
            self.logger.error(f"Upload failed for {filename}: {e}")
            raise
