import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap

class Follower(QWidget):
    def __init__(self):
        super().__init__()

        # --- Initialize UI ---
        self.label = QLabel(self)
        self.sprite_paths = {
            "awake": "sprites/cat.png",  # Right now only one sprite needed
            # "sleeping": "sprites/sleeping_cat.png",  # (for future)
            # "orbiting": "sprites/sparkle_orbit.png", # (for future)
        }
        self.current_state = "awake"  # Could later be 'sleeping', 'orbiting', etc.

        self.load_sprite(self.current_state)

        # --- Window settings ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # --- Movement setup ---
        self.current_pos = self.pos()
        self.timer = QTimer()
        self.timer.timeout.connect(self.follow_cursor)
        self.timer.start(16)  # ~60 FPS

    def load_sprite(self, state):
        """Loads the sprite based on the given state."""
        path = self.sprite_paths.get(state)
        if not path:
            print(f"Error: No sprite path defined for state '{state}'.")
            sys.exit(1)

        pixmap = QPixmap(path)
        if pixmap.isNull():
            print(f"Error: Could not load image at '{path}'.")
            sys.exit(1)

        self.label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

    def follow_cursor(self):
        mouse_pos = QApplication.instance().desktop().cursor().pos()
        # Smooth interpolation
        self.current_pos += (mouse_pos - self.current_pos) * 0.1
        self.move(self.current_pos)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    follower = Follower()
    follower.show()
    sys.exit(app.exec_())
