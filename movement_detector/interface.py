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
        self._key_repeat_buffer = 600

    def display(self, stop_keys=('N', 'P', 27)):
        vid_name = self.detector.video.vid_name
        self._play_video = False
        self._frame_index = 0
        time_since_last_frame = 0
        quit_ = False
        keys = None
        command_text = ''
        command_print_count = 0
        command_print_max = max(self._key_repeat_buffer, 10)
        keys_pressed = []
        time_since_key_press = 0
        while True:
            tick = self._clock.tick()
            if self._frame_index == len(self.detector.video):
                self._play_video = False
            else:
                frame = self._build_frame(action_text=command_text)
                if command_text != '':
                    command_print_count += 1
                    if command_print_count == command_print_max:
                        command_text = ''
                        command_print_count = 0
            pygame.display.set_caption(
                f'{vid_name} - Frame {self._frame_index + 1}'
            )
            pygame.surfarray.blit_array(self._player, frame)
            pygame.display.update()

            keys_pressed = pygame.key.get_pressed()
            if any(keys_pressed):
                if (time_since_key_press == 0
                        or time_since_key_press >= self._key_repeat_buffer):
                    new_command_text = self._parse_command(keys=keys_pressed)
                time_since_key_press += tick
                if new_command_text != '':
                    command_text = new_command_text
            else:
                time_since_key_press = 0
                if self._space_pressed:
                    self._space_pressed = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit_ = True
            if quit_:
                break
            if self._play_video:
                time_since_last_frame += tick
                if time_since_last_frame >= 1/self._playback_frame_rate:
                    self._frame_index += 1
                    time_since_last_frame = 0
            else:
                time_since_last_frame = 0
        return keys_pressed

    def _build_frame(self, action_text=''):
        frame = self.detector.video[self._frame_index]
        meta_data = self.detector.meta(
            start=self._frame_index,
            stop=self._frame_index + 1
        )
        self._add_moving_text(frame=frame, meta_data=meta_data)
        self._add_outlier_text(frame=frame, meta_data=meta_data)
        self._add_frame_rate_text(frame=frame)
        self._add_action_text(frame=frame, action_text=action_text)
        frame = np.flipud(np.rot90(frame))
        # frame = pygame.surfarray.make_surface(frame)

        return frame

    @staticmethod
    def _add_moving_text(frame, meta_data):
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

    @staticmethod
    def _add_outlier_text(frame, meta_data):
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
        else:
            colour = (255, 165, 0)
        cv2.putText(
            img=frame,
            text=outlier_text,
            org=(10, 40),
            fontFace=cv2.FONT_HERSHEY_COMPLEX,
            fontScale=.5,
            color=colour,
            thickness=2
        )

    def _add_frame_rate_text(self, frame):
        frame_rate = np.round(self._playback_frame_rate, decimals=2)
        frame_rate_text = f'Frame rate: {frame_rate}'
        cv2.putText(
            img=frame,
            text=frame_rate_text,
            org=(10, 60),
            fontFace=cv2.FONT_HERSHEY_COMPLEX,
            fontScale=.5,
            color=(255, 165, 0),
            thickness=2
        )

    def _add_action_text(self, frame, action_text):
        cv2.putText(
            img=frame,
            text=action_text,
            org=(10, 80),
            fontFace=cv2.FONT_HERSHEY_COMPLEX,
            fontScale=.5,
            color=(255, 165, 0),
            thickness=2
        )

    def _parse_command(self, keys):
        command_text = ''
        if not self._play_video:
            if keys[pygame.K_LEFT]:
                if self._frame_index != 0:
                    self._frame_index -= 1
                    command_text = 'Previous frame'
            elif keys[pygame.K_RIGHT]:
                if self._frame_index != len(self.detector.video) - 1:
                    self._frame_index += 1
                    command_text = 'Next frame'
            elif keys[ord('f')]:
                self.detector.set_freezing(self._frame_index)
                if self._frame_index != len(self.detector.video) - 1:
                    self._frame_index += 1
                    command_text = 'Set freezing'
            elif keys[ord('m')]:
                self.detector.set_moving(self._frame_index)
                if self._frame_index != len(self.detector.video) - 1:
                    self._frame_index += 1
                    command_text = 'Set moving'
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
                command_text = 'Found next flagged'
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
                command_text = 'Found previous flagged'
            elif keys[ord(' ')] and not self._space_pressed:
                self._space_pressed = True
                self._play_video = True
                command_text = 'Play'
        else:  # video is playing
            if keys[ord(' ')] and not self._space_pressed:
                self._space_pressed = True
                self._play_video = False
                command_text = 'Pause'
            elif keys[pygame.K_UP]:
                # max_frame_rate = self.detector.video.frame_rate * 2
                # if not self._playback_frame_rate + 1 > max_frame_rate:
                self._playback_frame_rate += 1
                command_text = 'Speed up'
            elif keys[pygame.K_DOWN] and self._playback_frame_rate - 1 > 0:
                self._playback_frame_rate -= 1
                command_text = 'Slow down'
        return  command_text
