"""
Explorer exception definitions.
"""


class ExplorerError(Exception):
    """
    Base explorer exception.
    """


class IndexingError(ExplorerError):
    """
    Raised when indexing fails.
    """


class QueryError(ExplorerError):
    """
    Raised when an explorer query fails.
    """


class RecordNotFoundError(QueryError):
    """
    Raised when requested data does not exist.
    """