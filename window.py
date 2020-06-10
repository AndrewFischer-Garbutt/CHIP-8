import pygame

class window:
    def __init__(self, hight, width, draw_color, title='New window'):
       self.dimension = (hight, width)
       self.draw_color = draw_color
       self.title = title

       self.BACKGROUND_COLOR = (0,0,0)
       self.DRAW_COLOR = (255,255,255)
       self.DRAW_HIGHT = 10
       self.DRAW_WIDTH = 10

       self.debug = False

    def draw_window(self):
        self.display = pygame.display.set_mode(self.dimension)
        
        pygame.display.set_caption(self.title)
        self.display.fill(self.BACKGROUND_COLOR)

        pygame.display.flip()

    def draw_sprite(self, x_pos, y_pos, pixel_data):
        for i in range(len(pixel_data)):
            for j in range(8):
                if (pixel_data[i] << j) & 0x80:
                    params = ( x_pos + self.DRAW_WIDTH * j,
                               y_pos + self.DRAW_HIGHT * i,
                               self.DRAW_WIDTH,
                               self.DRAW_HIGHT 
                            )

                    if self.debug:
                        print(params)
                    pygame.draw.rect(self.display, self.DRAW_COLOR, params)
        pygame.display.flip()

    def clear_screen(self):
       self.display.fill(self.BACKGROUND_COLOR)

if __name__ == '__main__':
        w = window(640, 320, (255, 255, 255))
        w.draw_window()
        w.draw_sprite(100, 100, [0xF0,0x90,0x90,0x90,0xF0])
        w.draw_sprite(50, 50, [0xBA,0x7C,0xD6,0x54,0xAA])
        ZERO = [
                0b01100000,    
                0b10010000,    
                0b10010000,    
                0b10010000,    
                0b01100000
            ]

        ONE = [
                0b01100000,    
                0b00100000,    
                0b00100000,    
                0b00100000,    
                0b01110000
            ]

        w.clear_screen()

        w.draw_sprite(200, 50, ONE)
        running = True
        while running:
          for event in pygame.event.get():
            if event.type == pygame.QUIT:
              running = False

