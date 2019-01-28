import os
os.environ['GST_PLUGIN_PATH'] = os.path.abspath('.')

from src.gui.kivy_gui.gui_app import GuiApp
from src.data.video import OpenCvVideo


class App:
    def __init__(self):
        self.gui = GuiApp()

    def start(self):
        temp_vid_path = '/Users/petioptrv/Documents/Programming/Python/movement_detector/videos/demo_video.mp4'
        self.gui.load_video(OpenCvVideo(temp_vid_path))
        self.gui.run()
