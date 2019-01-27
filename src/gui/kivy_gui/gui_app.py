import numpy as np

from kivy.app import App
from kivy.graphics import Rectangle
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button


class AppButton(Button):
    font_size = 32


class GuiLayout(GridLayout):
    def __init__(self, **kwargs):
        super(KivyGuiLayout, self).__init__(**kwargs)

        with self.canvas.before:
            self.rect = Rectangle(size=(2000, 600), pos=self.pos)

        self.cols = 2
        self.rows = 1
        self.spacing = 10
        self.padding = 10


class VideoPlayer:
    def __init__(self, video: np.ndarray = None):
        self.video = video


class GuiApp(App):
    def __init__(self, **kwargs):
        super(GuiApp, self).__init__(**kwargs)
        self.video

    def build(self):
        return KivyGuiLayout()
