from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.config import Config

import cv2


Config.set('graphics', 'resizable', 0)
Window.size = (300, 600)
Window.size = (300, 600)


class CamApp(App):

    def build(self):
        self.img1 = Image(size_hint=(1, .6))

        layout = BoxLayout(
            spacing=10,
            orientation='vertical',
            padding=[50]*4,
            minimum_width=500,
            minimum_height=500
        )
        layout.rows = 2
        self.video_trigger_btn = Button(text='Play', size_hint=(1, .2))
        self.video_trigger_btn.bind(on_press=self.video_trigger)
        self.video_reset = Button(text='Stop', size_hint=(1, .2))
        self.video_reset.bind(on_press=self.reset_video)
        layout.add_widget(self.img1)
        layout.add_widget(self.video_trigger_btn)
        layout.add_widget(self.video_reset)
        #opencv2 stuffs
        self.capture = cv2.VideoCapture('/Users/petioptrv/Documents/Programming/Python/freezing_detector/videos/demo_video.mp4')
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        # cv2.namedWindow("CV2 Image")
        return layout

    def update(self, dt):
        # display image from cam in opencv window
        ret, frame = self.capture.read()
        # cv2.imshow("CV2 Image", frame)
        # convert it to texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture1

    def video_trigger(self, something):
        if self.video_trigger_btn.text == 'Play':
            self.video_trigger_btn.text = 'Pause'
            Clock.schedule_interval(self.update, 1.0 / 29.97)
        else:
            self.video_trigger_btn.text = 'Play'
            Clock.unschedule(self.update)

    def reset_video(self, something):
        if self.video_trigger_btn.text == 'Pause':
            self.video_trigger(None)
        self.capture = cv2.VideoCapture(
            '/Users/petioptrv/Documents/Programming/Python/freezing_detector/videos/demo_video.mp4'
        )
        self.update(None)


if __name__ == '__main__':
    CamApp().run()
    cv2.destroyAllWindows()
