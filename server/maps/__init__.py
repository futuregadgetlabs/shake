import random

from map_1 import map_1
from map_2 import map_2


def get_random_map() -> list[str]:
    return random.choice([map_1, map_2])
