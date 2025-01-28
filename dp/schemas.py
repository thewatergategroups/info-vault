"""
Schemas
"""

from enum import StrEnum


class DbActions(StrEnum):
    """Database actions"""

    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"


class DocType(StrEnum):
    """Document type"""

    JPEG = "image/jpeg"
    PNG = "image/png"
