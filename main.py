import sys
import json
import threading
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect
from PyQt5.QtGui import QPixmap
from pynput import mouse

class Follower(QWidget):
    def __init__(self, sprite_data):
        super().__init__()
        self.sprite_data = sprite_data
        self.current_action = "following"

        # --- UI Setup ---
        self.label = QLabel(self)
        self.load_sprite(self.current_action)

        # --- Make window frameless and transparent ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Important: click-through!

        # --- Movement setup ---
        self.current_pos = self.pos()
        self.timer = QTimer()
        self.timer.timeout.connect(self.follow_cursor)
        self.timer.start(16)  # ~60 FPS

    def load_sprite(self, action):
        path = self.sprite_data['sprites'].get(action)
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
        if self.current_action in ("following", "mousedown"):
            mouse_pos = QApplication.instance().desktop().cursor().pos()
            self.current_pos += (mouse_pos - self.current_pos) * 0.1
            self.move(self.current_pos)
        # If idle: stay at current position (do nothing)


    def set_idle(self, idle_zone_rect):
        """Place sprite at center of idle zone."""
        center = idle_zone_rect.center()
        half_size = QPoint(self.width() // 2, self.height() // 2)
        new_pos = center - half_size
        self.move(new_pos)
        self.current_action = "idle"
        self.load_sprite(self.current_action)

    def wake_up(self):
        self.current_action = "following"
        self.load_sprite(self.current_action)
        self.show()  # Bring follower back to front after waking

    def change_action(self, action):
        if action in self.sprite_data['sprites']:
            self.current_action = action
            self.load_sprite(self.current_action)
        else:
            print(f"Warning: Action '{action}' not available for this sprite.")


class IdleZone(QWidget):
    def __init__(self, follower):
        super().__init__()
        self.follower = follower

        # --- UI Setup ---
        self.label = QLabel(self)
        pixmap = QPixmap('sprites/cat_idle_zone.png')
        if pixmap.isNull():
            print(f"Error: Could not load idle zone sprite.")
            sys.exit(1)

        self.label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

        # --- Place on right side, vertically centered ---
        screen = QApplication.desktop().screenGeometry()
        self.move(screen.width() - self.width(), (screen.height() - self.height()) // 2)

        # --- Window settings ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.show()

    def rect_global(self):
        """Return the rectangle of the IdleZone in global screen coordinates."""
        return QRect(self.mapToGlobal(self.rect().topLeft()), self.rect().size())

    def on_click(self, x, y, button, pressed):
        """Global mouse click detected."""
        if pressed:
            if self.rect_global().contains(QPoint(x, y)):
                if self.follower.current_action == "following":
                    self.follower.set_idle(self.rect_global())
                elif self.follower.current_action == "idle":
                    self.follower.wake_up()
            else:
                # Clicked somewhere else on screen
                if self.follower.current_action == "following":
                    self.follower.change_action('mousedown')
        else:
            # Mouse released
            if self.follower.current_action == "mousedown":
                self.follower.change_action('following')


def start_mouse_listener(idle_zone):
    """Start a thread that listens for global mouse clicks."""
    listener = mouse.Listener(
        on_click=idle_zone.on_click
    )
    listener.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # --- Load sprite data ---
    with open('sprites.json', 'r') as f:
        all_sprites = json.load(f)

    sprite_data = all_sprites['cat']

    # --- Create follower (Kitty) ---
    follower = Follower(sprite_data)
    follower.show()

    # --- Create idle zone ---
    idle_zone = IdleZone(follower)

    # --- Start global mouse listener ---
    threading.Thread(target=start_mouse_listener, args=(idle_zone,), daemon=True).start()
    follower.show()  # Force bring to front properly

    sys.exit(app.exec_())
