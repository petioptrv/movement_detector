from kivy.app import App
from kivy.graphics import Rectangle
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.video import Video

from src.data.video import AbstractVideo


class AppButton(Button):
    font_size = 32


class GuiLayout(GridLayout):
    def __init__(self, **kwargs):
        super(GuiLayout, self).__init__(**kwargs)

        with self.canvas.before:
            self.rect = Rectangle(size=(2000, 600), pos=self.pos)

        self.cols = 2
        self.rows = 1
        self.spacing = 10
        self.padding = 10


class VideoPlayer(Video):
    def __init__(self, video: AbstractVideo = None, **kwargs):
        super(VideoPlayer, self).__init__(**kwargs)
        self.video: AbstractVideo = video

    def load_video(self):
        if self.video is not None:
            self.source = self.video.file_path
            self.play = False

    def play_video(self):
        self.play = True

    def stop_video(self):
        self.play = False

    def trigger_video(self):
        self.play = not self.play


class GuiApp(App):
    def __init__(self, **kwargs):
        super(GuiApp, self).__init__(**kwargs)
        self.video_player = VideoPlayer()

    def build(self):
        return GuiLayout()

    def load_video(self, video: AbstractVideo):
        self.video_player.video = video
        self.video_player.load_video()
