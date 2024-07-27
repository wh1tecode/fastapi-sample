import random
import string



def generate_username(full_name: str, count: int = 8):
    digits = string.digits
    # username = "".join(random.choice(full_name + digits + "_") for i in range(count))
    username = "".join(random.choice(full_name) for i in range(count))
    digits = "".join(random.choice(full_name + digits + "_") for i in range(count))
    return username

def password_generator(count: int = 6) -> str:
    characters = list(string.ascii_letters + string.digits + "$#@")
    length = random.randint(10, 15)
    random.shuffle(characters)
    password = []
    for i in range(length):
        password.append(random.choice(characters))
    random.shuffle(password)
    password = "".join(password)
    return password[0: count]
