//change to components.py

from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.rect import Rect

S = 240
PAD_VEL = 2.0

class Ball:
    def __init__(self, x, y, radius, colour):
        self.radius = radius
        self.circle = Circle(x0=x, y0=y, r=radius, fill=colour, outline=colour)
        self.posx = x
        self.posy = y
        self.x_vel = 0.5
        self.y_vel = 0.5
        self._last_vy = 0.5

class Paddle:
    def __init__(self, x, y, width, height, colour):
        self.width = width
        self.height = height
        self.rect = Rect(x=x, y=y, width=width, height=height, fill=colour, outline=colour)
        self.posx = x
        self.posy = y

    def draw(self, accel):
        self.posx += accel[0] * PAD_VEL
        if self.posx < 0:
            self.posx = 0
        elif self.posx > S - self.width:
            self.posx = S - self.width
        self.rect.x = int(self.posx)
        self.rect.y = int(self.posy)

class Listener:
    def __init__(self):
        self.s = 0

    def pressed(self, button):
        if button:
            self.s = 1
            return False
        if self.s == 1:
            self.s = 0
            return True
        return False
