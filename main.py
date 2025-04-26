import sys
import json
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap

class Follower(QWidget):
    def __init__(self):
        super().__init__()

        # --- Load sprite data from JSON ---
        with open('sprites.json', 'r') as f:
            self.all_sprites = json.load(f)

        # --- Set which creature we are using ---
        self.current_creature = "cat"  # Could be dynamic later
        self.creature_data = self.all_sprites[self.current_creature]
        self.current_action = "following"  # Start by following

        # --- Initialize UI ---
        self.label = QLabel(self)
        self.load_sprite(self.current_action)

        # --- Window settings ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # --- Movement setup ---
        self.current_pos = self.pos()
        self.timer = QTimer()
        self.timer.timeout.connect(self.follow_cursor)
        self.timer.start(16)  # ~60 FPS

    def load_sprite(self, action):
        """Loads the sprite based on the current action."""
        path = self.creature_data['sprites'].get(action)
        if not path:
            print(f"Error: No sprite path defined for action '{action}'.")
            sys.exit(1)

        pixmap = QPixmap(path)
        if pixmap.isNull():
            print(f"Error: Could not load image at '{path}'.")
            sys.exit(1)

        self.label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

    def follow_cursor(self):
        mouse_pos = QApplication.instance().desktop().cursor().pos()
        self.current_pos += (mouse_pos - self.current_pos) * 0.1
        self.move(self.current_pos)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    follower = Follower()
    follower.show()
    sys.exit(app.exec_())
