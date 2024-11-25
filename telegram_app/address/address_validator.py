"""Provides an interface for address validation."""

from abc import ABC, abstractmethod


class AddressValidator(ABC):
    """Address validator interface."""

    @abstractmethod
    def validate_area(self, area: str) -> bool:
        """Validate the area input."""

    @abstractmethod
    def validate_address(self, area: str, street: str, house: str) -> bool:
        """Validate the address input."""
