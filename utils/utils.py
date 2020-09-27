from uuid import uuid4


def generate_string(string_length=8):
    random_ = str(uuid4())
    random_ = random_.lower()
    random_ = random_.replace("-", "")
    return random_[0:string_length]
