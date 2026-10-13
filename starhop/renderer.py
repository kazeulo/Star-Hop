"""Drawing the world onto a (scaled-up) webcam frame."""
import cv2
import numpy as np

from . import config
from .config import PLATFORM, PLAYER

FONT = cv2.FONT_HERSHEY_SIMPLEX
RED = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def _load_sprite(name, size):
    path = config.SPRITES / name
    sprite = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if sprite is None:
        raise FileNotFoundError(path)
    sprite = cv2.resize(sprite, size)
    if sprite.shape[2] == 3:  # no alpha channel: make fully opaque
        alpha = np.full(sprite.shape[:2] + (1,), 255, dtype=sprite.dtype)
        sprite = np.concatenate([sprite, alpha], axis=2)
    return sprite


def overlay_sprite(frame, sprite, x, y):
    """Alpha-blend `sprite` onto `frame` at (x, y), clipping at the edges."""
    fh, fw = frame.shape[:2]
    sh, sw = sprite.shape[:2]
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + sw, fw), min(y + sh, fh)
    if x0 >= x1 or y0 >= y1:
        return
    part = sprite[y0 - y:y1 - y, x0 - x:x1 - x]
    alpha = part[:, :, 3:4] / 255.0
    roi = frame[y0:y1, x0:x1]
    roi[:] = (roi * (1 - alpha) + part[:, :, :3] * alpha).astype(frame.dtype)


class Renderer:
    """Draws world coordinates (webcam pixels) onto frames enlarged by `scale`."""

    def __init__(self, scale=config.DISPLAY_SCALE):
        self.scale = scale
        self._platform = _load_sprite("platform_normal.png",
                                      self._size(PLATFORM.width, PLATFORM.height))
        size = self._size(PLAYER.width, PLAYER.height)
        self._poses = {
            pose: _load_sprite(f"player_{config.CHARACTER}_{pose}.png", size)
            for pose in ("front", "stand_left", "stand_right", "jump_left", "jump_right")
        }

    def _player_sprite(self, world):
        if world.facing == 0:
            return self._poses["front"]
        state = "jump" if world.velocity < 0 else "stand"
        return self._poses[f"{state}_{'right' if world.facing > 0 else 'left'}"]

    def _size(self, w, h):
        return round(w * self.scale), round(h * self.scale)

    def prepare(self, frame):
        """Enlarge a raw webcam frame to the display size."""
        return cv2.resize(frame, None, fx=self.scale, fy=self.scale,
                          interpolation=cv2.INTER_LINEAR)

    def draw(self, frame, world, best=0, face_found=True):
        s = self.scale
        overlay_sprite(frame, self._player_sprite(world), round(world.x * s), round(world.y * s))
        for px, py in world.platforms:
            overlay_sprite(frame, self._platform, round(px * s), round(py * s))
        self._text(frame, f"Score: {world.score}", (10, 32), 1, WHITE, 2, shadow=True)
        self._text(frame, f"Best: {max(best, world.score)}", (10, 62), 0.7, WHITE, 2, shadow=True)
        if not face_found:
            self._centered(frame, "No face detected", 100, 0.9, 2, RED)
        self._controls_hint(frame)

    def _controls_hint(self, frame):
        """Right-aligned controls reminder in the top-right corner."""
        lines = ("Move head: steer", "P: pause", "Q: menu")
        scale, thickness, line_height, margin = 0.6, 1, 24, 10
        for i, text in enumerate(lines):
            (tw, _), _ = cv2.getTextSize(text, FONT, scale, thickness)
            org = (frame.shape[1] - tw - margin, 26 + i * line_height)
            self._text(frame, text, org, scale, WHITE, thickness, shadow=True)

    def draw_game_over(self, frame, score, best, new_best):
        h = frame.shape[0]
        self._centered(frame, "GAME OVER", h // 2, 2, 3, RED)
        self._centered(frame, f"Final Score: {score}", h // 2 + 45, 1, 2, RED)
        label = "New best!" if new_best else f"Best: {best}"
        self._centered(frame, label, h // 2 + 85, 0.8, 2, RED)
        self._centered(frame, "R / Space: retry    Esc: menu", h // 2 + 125, 0.7, 2, WHITE,
                       shadow=True)

    def draw_paused(self, frame):
        h = frame.shape[0]
        self._centered(frame, "PAUSED", h // 2, 2, 3, RED)
        self._centered(frame, "P: resume    Q: menu", h // 2 + 45, 0.8, 2, WHITE, shadow=True)

    @staticmethod
    def _text(frame, text, org, scale, color, thickness, shadow=False):
        if shadow:
            cv2.putText(frame, text, (org[0] + 1, org[1] + 1), FONT, scale, BLACK, thickness + 2)
        cv2.putText(frame, text, org, FONT, scale, color, thickness)

    def _centered(self, frame, text, y, scale, thickness, color, shadow=False):
        (tw, _), _ = cv2.getTextSize(text, FONT, scale, thickness)
        self._text(frame, text, ((frame.shape[1] - tw) // 2, y), scale, color, thickness, shadow)
