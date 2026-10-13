"""One play session: webcam in, rendered frames out."""
import cv2

from . import config, highscore
from .audio import Audio
from .face_tracker import FaceTracker
from .renderer import Renderer
from .world import World


class Game:
    def __init__(self, tracker: FaceTracker, audio: Audio):
        self.tracker = tracker
        self.audio = audio
        self.renderer = Renderer()
        self.world = World(tracker.width, tracker.height)
        self.best = highscore.load()
        self._new_best = False

    def run(self):
        """Play rounds until the user quits to the menu or the camera fails."""
        self.audio.start.play()
        try:
            while self._play_round() and self._game_over_screen():
                pass
        finally:
            self.audio.stop_music()
            cv2.destroyAllWindows()

    def _play_round(self):
        """Run one round. Returns True if the player died, False if they quit."""
        self.world.reset()
        self.audio.play_music()
        paused = False
        while True:
            frame = self.tracker.read()
            if frame is None:
                return False

            center_x = self.tracker.face_center_x(frame)
            frame = self.renderer.prepare(frame)
            if not paused:
                if center_x is not None:
                    self.world.steer_toward(center_x)
                if self.world.step():
                    self.audio.jump.play()
                if self.world.game_over:
                    self._save_score()
                    return True

            self.renderer.draw(frame, self.world, self.best, center_x is not None)
            if paused:
                self.renderer.draw_paused(frame)
            cv2.imshow(config.WINDOW_TITLE, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == config.QUIT_KEY:
                return False
            if key == config.PAUSE_KEY:
                paused = not paused
                (self.audio.pause_music if paused else self.audio.resume_music)()

    def _game_over_screen(self):
        """Show results and wait. Returns True to play again, False for the menu."""
        self.audio.stop_music()
        self.audio.game_over.play()
        frame = self.tracker.read()
        if frame is None:
            return False
        frame = self.renderer.prepare(frame)
        self.renderer.draw_game_over(frame, self.world.score, self.best, self._new_best)
        cv2.imshow(config.WINDOW_TITLE, frame)
        while True:
            key = cv2.waitKey(50) & 0xFF
            if key in config.RESTART_KEYS:
                return True
            if key in config.MENU_KEYS or key == config.QUIT_KEY:
                return False
            if cv2.getWindowProperty(config.WINDOW_TITLE, cv2.WND_PROP_VISIBLE) < 1:
                return False  # window closed with the X button

    def _save_score(self):
        score = self.world.score
        self._new_best = score > self.best
        if self._new_best:
            self.best = score
            highscore.save(score)
