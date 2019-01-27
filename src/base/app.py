from ..gui.kivy_gui.gui_app import GuiApp
from ..data.video import AbstractVideo


class App:
    def __init__(self):
        self.gui = GuiApp()

    def start(self):
        temp_vid_path = '/Users/petioptrv/Documents/Programming/Python/movement_detector/videos/CamR01_13Dec2018_11-03-49.wmv'
        self.gui.load_video(AbstractVideo(temp_vid_path))
        self.gui.run()
