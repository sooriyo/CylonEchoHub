import string
import random


def generate_verification_token():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
