from typing import Any, Callable
import sys
from multiprocessing import cpu_count
from abc import ABC, abstractmethod


class AbstractSettings(ABC):
    def __init__(self, **kwargs):
        self._settings = self._blank_settings()
        self._subscribers = []
        for setting, value in kwargs.items():
            self.set_setting(setting, value)

    @property
    def settings_dict(self) -> dict:
        settings_dict = {}
        for name, setting in self._settings.items():
            settings_dict[name] = setting['value']
        return settings_dict

    @staticmethod
    @abstractmethod
    def _blank_settings() -> dict:
        """
        Creates a settings.txt object initialized to the default values.
        The settings.txt object is a dictionary of dictionaries. Each setting
        name is associated with its setting data. The type represents the
        accepted type for this setting. The value is the current setting value.
        The default field provides the possibility to allow defaults
        re-initialization etc. The accepted field holds the acceptable values
        in the form of a slice with start and stop values in the case of a
        float-valued setting; a range with a start, stop, and step values in
        the case of an integer-valued setting; and a list of accepted string
        values in the case of a string-valued setting. An accepted field set to
        `None` means an unrestricted setting value (type checking is still
        applied). The help field contains a description of the setting.
        :return: The settings.txt dictionary of dictionaries.
        """
        pass

    def get_type(self, setting: str) -> type:
        """
        Returns the type of the specified setting.
        :param setting: The name of the setting.
        :return: The type of the setting.
        """
        return self._settings[setting]['type']

    def get_value(self, setting: str) -> Any:
        """
        Return setting value.
        :param setting: The setting name.
        :return: Current value for that setting.
        """
        return self._settings[setting]['value']

    def set_setting(self, setting: str, value: Any):
        """
        Assign new value to a setting.
        Passed-in value is checked against the accepted types and values of the
        setting.
        :param setting: The setting name.
        :param value: The value to be assigned.
        :return:
        """
        setting = self._settings[setting]
        if value is None:
            if setting['mandatory']:
                raise TypeError(
                    'This setting is mandatory. None is not a valid value.')
        else:
            if setting['type'] is float:
                try:
                    value = float(value)
                except ValueError:
                    raise ValueError(
                        f'Setting accepts either float or int values,'
                        f' but {type(value)} passed.'
                    )
            # check type
            if not isinstance(value, setting['type']):
                if value is not None or not setting['accept_none']:
                    raise TypeError(
                        'Setting accepts {} values, but {} passed.'.format(
                            setting['type'], type(value)))
            # check value
            if setting['accepted'] is not None:
                if setting['type'] is float:
                    if (
                            value < setting['accepted'].start
                            or value >= setting['accepted'].stop
                    ):
                        raise ValueError(
                            'Unsupported setting value. '
                            'Supported values are floating-point numbers from'
                            ' {} to {}, but received {}'.format(
                                setting['accepted'].start,
                                setting['accepted'].stop, value
                            )
                        )
                elif setting['type'] is int:
                    if value not in setting['accepted']:
                        raise ValueError(
                            'Unsupported setting value. '
                            'Supported values are integer numbers from {} to'
                            ' {} in step of {}, but received {}'.format(
                                setting['accepted'].start,
                                setting['accepted'].stop,
                                setting['accepted'].step, value
                            )
                        )
                else:
                    if value not in setting['accepted']:
                        raise ValueError(
                            'Unsupported setting value. Supported values'
                            ' include {}, but received {}'.format(
                                setting['accepted'], value
                            )
                        )
        setting['value'] = value
        self._update_registered()

    def register(self, func: Callable, *args, **kwargs):
        """
        Subscribes the passed in function to changes in settings.txt.
        When a changing in the settings.txt occurs, the subscribed
        function is called.
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        self._subscribers += (func, args, kwargs)

    def _update_registered(self):
        """
        Calls all functions registered for call-back when the
        settings.txt change.
        """
        for subscriber in self._subscribers:
            subscriber[0](*subscriber[1], **subscriber[2])


class AbstractAnalyzerSettings(ABC, AbstractSettings):
    @staticmethod
    @abstractmethod
    def _blank_settings() -> dict:
        return {
            'interval_start_times': {
                'type': list, 'value': [0, 150, 180], 'default': None,
                'mandatory': False,
                'accepted': None
            }
        }


class SystemSettings(AbstractSettings):
    @staticmethod
    def _blank_settings() -> dict:
        blank_settings = super()._blank_settings()
        blank_settings.update({
            'max_cpus': {
                'type': int, 'value': 1, 'default': None, 'mandatory': False,
                'accepted': range(1, cpu_count() + 1, 1),
                'help': 'Maximum CPUs the application can use. If not set, then'
                        ' the application will use'
                        '\none CPU less than the maximum available.'
            },
        })
        return blank_settings


class PixelChangeSettings(AbstractAnalyzerSettings):
    @staticmethod
    def _blank_settings() -> dict:
        """
        :return:
        """
        blank_settings = super()._blank_settings()
        blank_settings.update({
            'outlier_change_threshold': {
                'type': float, 'value': 2, 'default': 2, 'mandatory': True,
                'accepted': slice(0, sys.maxsize),
                'help': 'When detecting change contours, how many standard'
                        ' deviations above\nthe mean must a given'
                        ' change-contour area-size be to be considered'
                        ' an outlier.'
            },
            'flag_outliers_window': {
                'type': int, 'value': 8, 'default': 8, 'mandatory': True,
                'accepted': range(0, sys.maxsize),
                'help': 'Frames are marked as containing outlier changes if'
                        ' the majority of the frames in a rolling window of'
                        ' flag_outliers_window window-size contain'
                        ' outlier changes.'
            },
            'freezing_window': {
                'type': int, 'value': 5, 'default': 5, 'mandatory': True,
                'accepted': range(0, sys.maxsize),
                'help': 'Frames are marked as "freezing" if the majority of'
                        ' the frames in the window of freezing_window'
                        ' window-size lack frame-changes.'
            },
            'blur_ksize': {
                'type': int, 'value': 21, 'default': 21, 'mandatory': True,
                'accepted': range(1, sys.maxsize, 2),
                'help': 'Sets the kernel size for the Gaussian blur in the'
                        ' frame pre-processing step. Must be a positive odd'
                        ' integer. The higher the value, the more pronounced'
                        ' the blur.'
            },
        })
        return blank_settings
