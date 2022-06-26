import json
from enum import Enum, auto
from typing import Any

import pygame
import pygame.camera
from pygame.locals import K_DOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_UP, KEYDOWN, QUIT


def encode_msg(msg: dict[str, Any]) -> str:
    return json.dumps(msg, ensure_ascii=False)


def decode_msg(msg: str) -> dict[str, Any]:
    return json.loads(msg)


pygame.init()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
PLAYER_SPEED = 2


class Direction(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super()
        self.surf = pygame.Surface((32, 32))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.facing = Direction.NORTH
        self.id = None

    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -PLAYER_SPEED)
            self.facing = Direction.NORTH
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, PLAYER_SPEED)
            self.facing = Direction.SOUTH
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-PLAYER_SPEED, 0)
            self.facing = Direction.WEST
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(PLAYER_SPEED, 0)
            self.facing = Direction.EAST

        # Keep player on the screen
        self.rect.left = max(self.rect.left, 0)
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        self.rect.top = max(self.rect.top, 0)
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
clock = pygame.time.Clock()
camlist = pygame.camera.list_cameras()
print(camlist)
player = Player()
running = True


async def receive_message(websocket):
    count = 0

    async for message_raw in websocket:
        count += 1
        msg = decode_msg(message_raw)
        if msg["type"] == "joined":
            msg["client_id"]


while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            break
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
            break

    pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)

    screen.fill((0, 0, 0))
    screen.blit(player.surf, player.rect)

    pygame.display.flip()
