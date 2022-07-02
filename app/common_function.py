from hashlib import md5


def get_md5_encode(string: str) -> str:
    m = md5()
    m.update(string.encode())
    return m.hexdigest()
