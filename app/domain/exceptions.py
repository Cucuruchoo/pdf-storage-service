class DuplicateDocumentError(Exception):
    """Raised when a document with the same checksum already exists."""


class DocumentNotFoundError(Exception):
    """Raised when a document does not exist."""