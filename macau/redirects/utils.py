import binascii
from base64 import b64decode

from django.http import HttpRequest
from django.utils.crypto import constant_time_compare


def check_basic_auth(request: HttpRequest, username: str, password: str) -> bool:
    for authentication in request.headers.get("Authorization", "").split(","):
        authentication_tuple = authentication.split(" ", 1)
        if len(authentication_tuple) != 2:
            return False

        if "basic" != authentication_tuple[0].lower():
            return False

        try:
            provided_credentials = b64decode(authentication_tuple[1].strip()).split(
                b":", 1
            )
        except (UnicodeDecodeError, binascii.Error):
            return False

        if len(provided_credentials) != 2:
            return False

        username_valid = constant_time_compare(provided_credentials[0], username)
        password_valid = constant_time_compare(provided_credentials[1], password)

        return username_valid and password_valid

    return False
