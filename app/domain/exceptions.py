class DomainError(Exception):
    """Base class for expected business failures."""


class DuplicateSKUError(DomainError):
    pass


class ProductNotFoundError(DomainError):
    pass


class InvalidQuantityError(DomainError):
    pass


class InvalidPriceError(DomainError):
    pass


class InsufficientStockError(DomainError):
    pass


class InactiveProductError(DomainError):
    pass
