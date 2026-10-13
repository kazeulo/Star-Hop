"""Pygame start menu: animated title, mascot, then play."""
import math

import pygame

from . import config, highscore

NEON = (190, 150, 255)
TEXT = (240, 232, 255)
MUTED = (160, 150, 200)
BUTTON = (60, 30, 120)
BUTTON_HOVER = (100, 58, 180)
PANEL = (12, 8, 40, 170)
SCROLL_SPEED = 18  # background pixels per second


def _image(name, size):
    path = config.SPRITES / name
    return pygame.transform.smoothscale(pygame.image.load(str(path)).convert_alpha(), size)


def show_menu():
    """Block until the user picks an option.

    Returns True to start playing, False to exit.
    The menu window is closed before returning so it does not linger behind the game.
    """
    pygame.display.init()
    try:
        return _Menu().run()
    finally:
        pygame.display.quit()


class _Menu:
    def __init__(self):
        self.screen = pygame.display.set_mode(config.MENU_SIZE)
        pygame.display.set_caption(config.WINDOW_TITLE)
        width = self.screen.get_width()
        self.cx = width // 2
        self.best = highscore.load()
        self._load_assets()
        self._layout()

    def _load_assets(self):
        self.background = pygame.image.load(
            str(config.SPRITES / "background_tile_seamless.png")).convert()
        self.title_font = pygame.font.SysFont("arial", 50, bold=True)
        self.sub_font = pygame.font.SysFont("arial", 24, bold=True)
        self.button_font = pygame.font.SysFont("arial", 26, bold=True)
        self.small_font = pygame.font.SysFont("arial", 15)

        self.title_line, self.subtitle = (
            self.title_font.render(config.TITLE_LINES[0], True, TEXT),
            self.sub_font.render(config.TITLE_LINES[1], True, NEON),
        )
        self.glow = self.title_font.render(config.TITLE_LINES[0], True, NEON)
        self.platform = _image("platform_normal.png", (110, 26))
        self.mascot = _image(f"player_{config.CHARACTER}_jump_right.png", (76, 91))

    def _layout(self):
        self.platform_rect = self.platform.get_rect(midtop=(self.cx, 260))
        self.play_rect = pygame.Rect(0, 0, 180, 46)
        self.play_rect.midtop = (self.cx - 100, 306)
        self.exit_rect = pygame.Rect(0, 0, 180, 46)
        self.exit_rect.midtop = (self.cx + 100, 306)
        self.help_rect = pygame.Rect(0, 0, 330, 58)
        self.help_rect.midtop = (self.cx, 372)

    # input 
    def run(self):
        clock = pygame.time.Clock()
        while True:
            result = self._handle_events()
            if result is not _CONTINUE:
                return result
            self._draw(pygame.time.get_ticks() / 1000, pygame.mouse.get_pos())
            pygame.display.flip()
            clock.tick(60)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.play_rect.collidepoint(event.pos):
                    return True
                if self.exit_rect.collidepoint(event.pos):
                    return False
        return _CONTINUE

    # drawing 
    def _draw(self, t, mouse):
        self._draw_background(t)
        self._draw_title(t)
        self._draw_mascot(t)
        self._draw_button(self.play_rect, "PLAY", mouse)
        self._draw_button(self.exit_rect, "EXIT", mouse)
        self._draw_help()

    def _draw_background(self, t):
        tile_w, tile_h = self.background.get_size()
        y = -int(t * SCROLL_SPEED) % tile_h  # scroll downward, wrapping the tile
        for x in range(0, config.MENU_SIZE[0], tile_w):
            self.screen.blit(self.background, (x, y))
            self.screen.blit(self.background, (x, y - tile_h))

    def _draw_title(self, t):
        pulse = 0.5 + 0.5 * math.sin(t * 2)
        glow = self.glow.copy()
        glow.set_alpha(int(90 + 120 * pulse))
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            self.screen.blit(glow, glow.get_rect(midtop=(self.cx + dx, 10 + dy)))
        self.screen.blit(self.title_line, self.title_line.get_rect(midtop=(self.cx, 10)))
        self.screen.blit(self.subtitle, self.subtitle.get_rect(midtop=(self.cx, 66)))
        if self.best:
            best = self.small_font.render(f"BEST  {self.best}", True, MUTED)
            self.screen.blit(best, best.get_rect(midtop=(self.cx, 97)))

    def _draw_mascot(self, t):
        """The player bounces on a platform, like in the game."""
        bob = abs(math.sin(t * 3.5)) * 60
        feet = self.platform_rect.top + 6 - bob
        self.screen.blit(self.mascot, self.mascot.get_rect(midbottom=(self.cx, feet)))
        self.screen.blit(self.platform, self.platform_rect)

    def _draw_button(self, rect, label, mouse):
        hovered = rect.collidepoint(mouse)
        grown = rect.inflate(8, 4) if hovered else rect
        pygame.draw.rect(self.screen, BUTTON_HOVER if hovered else BUTTON, grown,
                         border_radius=20)
        pygame.draw.rect(self.screen, NEON, grown, width=2, border_radius=20)
        text = self.button_font.render(label, True, TEXT)
        self.screen.blit(text, text.get_rect(center=grown.center))

    def _draw_help(self):
        panel = pygame.Surface(self.help_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, PANEL, panel.get_rect(), border_radius=10)
        self.screen.blit(panel, self.help_rect)
        lines = ("Move your head left / right to steer",
                 "Menu:  Enter play   Esc exit",
                 "In game:  P pause   Q menu   R retry")
        for i, text in enumerate(lines):
            surf = self.small_font.render(text, True, TEXT if i == 0 else MUTED)
            self.screen.blit(surf, surf.get_rect(midtop=(self.cx, self.help_rect.top + 4 + i * 17)))


_CONTINUE = object()
