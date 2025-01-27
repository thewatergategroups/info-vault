"""
Helper classes
"""

from enum import StrEnum


class DbActions(StrEnum):
    """Database actions"""

    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"


class DocType(StrEnum):
    """Document type"""

    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    JSON = "json"
    CSV = "csv"
    IMAGE = "image"
    VIDEO = "video"
    UNKNOWN = "unknown"
