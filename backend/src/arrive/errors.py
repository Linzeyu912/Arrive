class DomainError(Exception):
    """Base class for expected domain failures."""


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class InvariantError(DomainError):
    pass
