import pygame


background_colour = (0,0,0)

WHITE = (255,255,255)
SCREEN_HIGHT = 32
SCREEN_WIDTH = 64

DISPLAY = pygame.display.set_mode((10 * SCREEN_WIDTH, 10 * SCREEN_HIGHT))

pygame.display.set_caption('CHIP 8 Enterpter')
DISPLAY.fill(background_colour)

pygame.draw.rect(DISPLAY, WHITE, (200,150,100,50))

pygame.display.flip()

running = True
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
