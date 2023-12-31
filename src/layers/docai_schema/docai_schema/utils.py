import random
import string

import tiktoken

alphabet = string.ascii_lowercase + string.digits + string.ascii_uppercase
tokenizer = tiktoken.get_encoding("cl100k_base")


def guid(length: int = 10) -> str:
    """Generate a random string of fixed length"""
    return "".join(random.choices(alphabet, k=length))


def encode(string: str) -> list[int]:
    """Encode a string into tokens"""
    return tokenizer.encode(string)


def decode(tokens: list[int]) -> str:
    """Decode tokens into a string"""
    return tokenizer.decode(tokens)


def count_tokens(string: str) -> int:
    """Count the number of tokens in a string"""
    return len(encode(string))
