"""Module for Bullex profile resource."""

from bullexapi.http.resource import Resource


class Profile(Resource):
    """Class for Bullex profile resource."""
    # pylint: disable=too-few-public-methods

    url = "profile"
