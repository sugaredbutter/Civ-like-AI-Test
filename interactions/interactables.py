import pygame

INACTIVE_TEXT_COLOR = (180, 180, 180)
ACTIVE_TEXT_COLOR = (0, 0, 0)

class TextBox:
    def __init__(self, screen, x, y, width, height, hover_text = '', text = '', font = None):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.color = INACTIVE_TEXT_COLOR
        self.hover_text = hover_text
        self.text = text
        self.active = False
        if font == None:
            self.font = pygame.font.SysFont(None, 24)
        else:
            self.font = font
        self.txt_surface = self.font.render(self.hover_text, True, self.color)

    def activate(self):
        self.active = True
        self.color = ACTIVE_TEXT_COLOR
        self.txt_surface = self.font.render(self.text, True, self.color)

    def deactivate(self):
        self.active = False
        self.color = INACTIVE_TEXT_COLOR
        if self.text == '':
            self.txt_surface = self.font.render(self.hover_text, True, self.color)

        

    def is_over(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_x, mouse_y):
            return True
        return False
    
    def draw(self, is_hovered = False):
        self.screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y + self.txt_surface.get_size()[1]/2))
        pygame.draw.rect(self.screen, ACTIVE_TEXT_COLOR if is_hovered or self.active else INACTIVE_TEXT_COLOR, self.rect, 2)

    def edit(self, event):
        if event.key == pygame.K_RETURN:
            self.deactivate()
            return False

        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        else:
            self.text += event.unicode

        self.txt_surface = self.font.render(self.text, True, self.color)
        return True