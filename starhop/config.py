"""Static game configuration and asset paths."""
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
IMG = ASSETS / "img"
SOUNDS = ASSETS / "sounds"
SPRITES = IMG / "sprites"
FACE_MODEL = ROOT / "models" / "face_detection_yunet_2023mar.onnx"

CHARACTER = "pink"  # sprite set: assets/img/sprites/player_<CHARACTER>_*.png

GAME_TITLE = "Star Hop"
TITLE_LINES = ("STAR HOP", "F A C E   J U M P")  # menu logo: big line, spaced subtitle
WINDOW_TITLE = GAME_TITLE
MENU_SIZE = (780, 440)  # landscape
DISPLAY_SCALE = 1.5  # game window size relative to the webcam frame
CAMERA_INDEX = 0
QUIT_KEY = ord("q")
PAUSE_KEY = ord("p")
RESTART_KEYS = (ord("r"), ord(" "))
MENU_KEYS = (27,)  # Esc


@dataclass(frozen=True)
class Physics:
    gravity: int = 1
    jump_strength: int = -20
    scroll_line: int = 200  # player is pushed down to this y once above it


@dataclass(frozen=True)
class PlayerSpec:
    width: int = 42  # sprites are 80x96
    height: int = 50


@dataclass(frozen=True)
class PlatformSpec:
    width: int = 84  # sprite is 120x28
    height: int = 20
    min_gap_y: int = 80
    max_gap_y: int = 100
    min_x: int = 50


PHYSICS = Physics()
PLAYER = PlayerSpec()
PLATFORM = PlatformSpec()
MUSIC_VOLUME = 0.1
STEER_SMOOTHING = 0.5  # 0..1, fraction of the distance to the face covered per frame
GAP_GROWTH_PER_SCORE = 1 / 400  # platforms spread out as the score climbs
MAX_EXTRA_GAP = 50
HIGHSCORE_FILE = ROOT / "highscore.txt"
