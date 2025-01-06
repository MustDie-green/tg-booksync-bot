import os
import re

def is_valid_book_format(file_name: str, supported_formats: set) -> bool:
    _, ext = os.path.splitext(file_name)
    return ext.lower() in supported_formats

def is_valid_auth_code(auth_code):
    re.match(r'^.{10,}$', auth_code)
    