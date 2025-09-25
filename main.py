from pygame.examples.sprite_texture import renderer

from multiplayer import client
from game import rendering

client = client.GameClient()


rendering.main(client)
