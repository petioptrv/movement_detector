from abc import ABC, abstractmethod

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.video import Image

from src.data.video import AbstractVideo, OpenCvVideo


class GuiLayout(GridLayout):
    pass


class VideoPlayer(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def load_video(self, video: AbstractVideo):
        pass

    @abstractmethod
    def play_video(self):
        pass

    @abstractmethod
    def stop_video(self):
        pass

    @abstractmethod
    def trigger_video(self):
        pass


class OpenCvVideoPlayer(VideoPlayer, Image):
    """OpenCV video player.

    Designed to interface with OpenCvVideo objects.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def load_video(self, video: OpenCvVideo):
        pass

    def play_video(self):
        pass

    def stop_video(self):
        pass

    def trigger_video(self):
        pass


class GuiApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_player = OpenCvVideoPlayer()
        self.gui_layout = GuiLayout()

    def build(self):
        self.gui_layout.add_widget(self.video_player)
        return self.gui_layout

    def load_video(self, video: AbstractVideo):
        self.video_player.load_video(video)
