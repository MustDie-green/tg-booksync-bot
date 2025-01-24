import os
import re

def is_valid_book_format(file_name: str, supported_book_formats: set) -> bool:
    _, ext = os.path.splitext(file_name)
    return ext.lower() in supported_book_formats

def is_valid_email(email_candidate):
    re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email_candidate)
    