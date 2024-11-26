"""Provide a GeoapifyValidator class to interact with the Geoapify API.

This module is used for address validation and map image generation.
"""

import json
import urllib.parse

import requests
from requests.structures import CaseInsensitiveDict

from telegram_app.address.address_validator import AddressValidator
from telegram_app.bot.lang import AREAS


class GeoapifyValidator(AddressValidator):
    """Interact with the Geoapify API to verify address."""

    def __init__(self, token: list) -> None:
        """Initialize the GeoapifyValidator with a token.

        :param token: List of tokens for authentication.
        """
        self.token = token

    def validate_area(self, area: str) -> bool:
        """Validate the area input."""
        return area.upper() in AREAS

    def validate_address(self, area: str, street: str, house: str) -> bool:
        """Validate the address input."""
        encoded_address_text = urllib.parse.quote(f"{street} {house}, {area}")
        url = f"https://api.geoapify.com/v1/geocode/autocomplete?text={encoded_address_text}&apiKey={self.token}"
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        resp = requests.get(url, headers=headers, timeout=30)
        data = json.loads(resp.text)

        # Extract lon and lat
        features = data.get("features", [])
        if features:
            first_feature = features[0]
            properties = first_feature.get("properties", {})
            self.longitude = properties.get("lon")
            self.latitude = properties.get("lat")
            return self.longitude and self.latitude
        return False

    def get_formatted_map_image_with_marker_url(self) -> str:
        """Get the formatted map image with a marker URL."""
        return (
            f"https://maps.geoapify.com/v1/staticmap?style=osm-bright&width=600&height=400&center=lonlat:"
            f"{self.longitude},{self.latitude}&zoom=16.5&marker=lonlat:{self.longitude},{self.latitude};"
            f"color:%23ff0000;size:medium&scaleFactor=2&apiKey={self.token}"
        )
