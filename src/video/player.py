from abc import ABC, abstractmethod

from src.video.video import AbstractVideo


class AbstractVideoPlayer(ABC):
    def __init__(self):
        super().__init__()
        self.playing = False

    @abstractmethod
    def load_video(self, video: AbstractVideo):
        pass

    @abstractmethod
    def play_video(self):
        pass

    @abstractmethod
    def stop_video(self):
        pass

    def trigger_video(self):
        if self.playing:
            self.stop_video()
        else:
            self.play_video()

    @abstractmethod
    def reset_video(self):
        pass
