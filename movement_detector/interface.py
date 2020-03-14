import pandas as pd
import cv2
import pygame
import numpy as np

from movement_detector.detectors import AbstractMovementDetector


class Interface:
    """
    This class displays the video, overlays metadata, and enables user-control.
    """

    def __init__(self, detector: AbstractMovementDetector):
        self.detector = detector
        self._play_video = False
        self._frame_index = 0
        self._playback_frame_rate = self.detector.video.frame_rate
        self._player = pygame.display.set_mode(
            self.detector.video.frame_shape[1::-1],
            pygame.RESIZABLE
        )
        self._clock = pygame.time.Clock()
        self._space_pressed = False
        self._key_repeat_buffer = 20

    def display(self, stop_keys=('N', 'P', 27)):
        vid_name = self.detector.video.vid_name
        self._play_video = False
        self._frame_index = 0
        quit_ = False
        keys = None
        key_repeat = 0
        while True:
            if self._frame_index == len(self.detector.video):
                self._play_video = False
            else:
                frame = self._build_frame()
            pygame.display.set_caption(
                f'{vid_name} - Frame {self._frame_index + 1}'
            )
            pygame.surfarray.blit_array(self._player, frame)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit_ = True
                elif event.type == pygame.KEYUP:
                    if self._space_pressed:
                        self._space_pressed = False
                    key_repeat = 0
            if quit_:
                break
            new_keys = pygame.key.get_pressed()
            if new_keys == keys:
                key_repeat += 1
            keys = new_keys
            if key_repeat == 0 or key_repeat > self._key_repeat_buffer:
                self._parse_command(keys=keys)
            self._clock.tick(self._playback_frame_rate)
            if self._play_video:
                self._frame_index += 1
        return keys

    def _build_frame(self):
        frame = self.detector.video[self._frame_index]
        meta_data = self.detector.meta(
            start=self._frame_index,
            stop=self._frame_index + 1
        )

        if pd.isna(meta_data['moving'].iloc[0]):
            colour = (0, 0, 255)
            status_text = 'Loading info'
        elif meta_data['moving'].iloc[0]:
            colour = (0, 0, 255)
            status_text = 'Moving'
        else:
            colour = (0, 255, 0)
            status_text = 'Freezing'
        cv2.putText(
            img=frame,
            text=status_text,
            org=(10, 20),
            fontFace=cv2.FONT_HERSHEY_COMPLEX,
            fontScale=.5,
            color=colour,
            thickness=2,
        )
        outlier_text = ''
        if pd.isna(meta_data['outlier'].iloc[0]):
            colour = (0, 0, 255)
            outlier_text = 'Loading info'
        elif meta_data['manual_set'].iloc[0]:
            colour = (0, 255, 0)
            outlier_text = 'User-verified'
        elif meta_data['flagged'].iloc[0]:
            colour = (0, 0, 255)
            outlier_text = 'Flagged'
        cv2.putText(
            img=frame,
            text=outlier_text,
            org=(10, 40),
            fontFace=cv2.FONT_HERSHEY_COMPLEX,
            fontScale=.5,
            color=colour,
            thickness=2
        )
        frame = np.flipud(np.rot90(frame))
        # frame = pygame.surfarray.make_surface(frame)

        return frame

    def _parse_command(self, keys):
        if not self._play_video:
            if keys[pygame.K_LEFT]:
                if self._frame_index != 0:
                    self._frame_index -= 1
            elif keys[pygame.K_RIGHT]:
                if self._frame_index != len(self.detector.video) - 1:
                    self._frame_index += 1
            elif keys[ord('f')]:
                self.detector.set_freezing(self._frame_index)
                if self._frame_index != len(self.detector.video) - 1:
                    self._frame_index += 1
            elif keys[ord('m')]:
                self.detector.set_moving(self._frame_index)
                if self._frame_index != len(self.detector.video) - 1:
                    self._frame_index += 1
            elif keys[ord('n')]:
                search_started = False
                while True:
                    if self._frame_index == len(self.detector.video) - 1:
                        break
                    meta_data = self.detector.meta(self._frame_index)
                    if pd.isna(meta_data['flagged'].iloc[0]):
                        break
                    if meta_data['flagged'].iloc[0]:
                        if search_started:
                            break
                    else:
                        search_started = True
                    self._frame_index += 1
            elif keys[ord('p')]:
                search_started = False
                while True:
                    if self._frame_index == 0:
                        break
                    meta_data = self.detector.meta(self._frame_index)
                    if pd.isna(meta_data['flagged'].iloc[0]):
                        break
                    if meta_data['flagged'].iloc[0]:
                        if search_started:
                            break
                    else:
                        search_started = True
                    self._frame_index -= 1
            elif keys[ord(' ')] and not self._space_pressed:
                self._space_pressed = True
                self._play_video = True
        else:  # video is playing
            if keys[ord(' ')] and not self._space_pressed:
                self._space_pressed = True
                self._play_video = False
            elif keys[pygame.K_UP]:
                # max_frame_rate = self.detector.video.frame_rate * 2
                # if not self._playback_frame_rate + 1 > max_frame_rate:
                self._playback_frame_rate += 1
            elif keys[pygame.K_DOWN] and self._playback_frame_rate - 1 > 0:
                self._playback_frame_rate -= 1
