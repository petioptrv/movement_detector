from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.video import Image

from src.data.video import OpenCvVideo


class GuiLayout(GridLayout):
    pass


class OpenCvVideoPlayer(Image):
    """OpenCV video player.

    Designed to interface with OpenCvVideo objects.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.playing = False
        self.video: OpenCvVideo = None

    def load_video(self, video: OpenCvVideo):
        self.video = video

    def play_video(self):
        pass

    def stop_video(self):
        pass

    def trigger_video(self):
        if self.playing:
            self.stop_video()
        else:
            self.play_video()

    def reset_video(self):
        pass


class GuiApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_player = OpenCvVideoPlayer()
        self.gui_layout = GuiLayout()

    def build(self):
        self.gui_layout.add_widget(self.video_player)
        return self.gui_layout

    def load_video(self, video: OpenCvVideo):
        self.video_player.load_video(video)
