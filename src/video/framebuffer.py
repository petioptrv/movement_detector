import cv2


class FrameBuffer:
    def __init__(self, video: cv2.VideoCapture, buffer_length=100):
        self._frames = video
        self._start = -1
        if buffer_length % 2 != 0:  # making sure the buffer_length is a multiple of 2
            buffer_length += 1
        if buffer_length < 20:
            buffer_length = 20
        self._buffer_length = buffer_length
        self._active_buffer = 1
        self._buffer = []  # TODO: maybe consider changing this to tuples and splitting each buffer into 2 parts
        self._last_request = -1  # the index of the last frame that was requested
        self._hit = True  # records if the last request was a hit or a miss

    def get_frame(self, frame_number, _update_buffer_on_miss=True):
        """
        Gets the frame at index frame_number from the frame buffer object (index relative to frame number, 0-indexed)
        If the frame isn't contained in the buffer, the frame will be fetched from disk and the buffer will be updated
        :param frame_number: the frame index to get (0 indexed)
        :param _update_buffer_on_miss: if True, the buffer will be updated if the request misses
        :return: the data of the frame at index frame_number
        """

        # if the frame is in the buffer
        if self._start <= frame_number <= (self._start + self._buffer_length):
            return self._buffer[frame_number - self._start]

        # if the frame isn't in the buffer
        else:
            self._hit = False
            self._last_request = frame_number
            if _update_buffer_on_miss:
                self._update_buffer()
            self._frames.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            return self._frames.read()

    def _update_buffer(self):
        """
        Checks if the last request was a hit or miss.
        If the last request was a complete miss (far out of range) if will completely replace the buffer
        IF the last request was close, it will load new frames in the buffer but keep frames
        that are close to the request
        :return:
        """

        # the length of the buffer is always a multiple of 2
        # so the cast to int is only a formality
        load_point = int(self._last_request - (self._buffer_length * 0.5))

        if self._last_request > (self._start + self._buffer_length):
            if self._last_request > (self._start + (self._buffer_length * 1.5)):
                # the last request is completely out of range
                self._load(load_point)

            else:
                self._lazy_load(load_point)
        elif self._last_request < self._start:
            if self._last_request < (self._start - (self._buffer_length * 0.5)):
                # the last request is completely out of range
                self._load(load_point)
            else:
                self._lazy_load(load_point)
        else:  # the request is in range, we might want to preemptively load new data

            # if the last request was close enough to the end of the buffer, we trigger a re-load
            if self._last_request > (self._start + (self._buffer_length - 10)):
                self._lazy_load(load_point)
            pass

    def _load(self, index: int):
        """
        Loads new frames into the buffer, completely overwriting the buffer.
        Doesn't check if some of the frames are already in the buffer or not
        :param index: the index in the video to start loading from
        :return:
        """
        self._buffer = []
        self._frames.set(cv2.CAP_PROP_POS_FRAMES, index)
        for i in range(self._buffer_length):
            self._buffer.append(self._frames.read()[1])

    def _lazy_load(self, index: int):
        """
        Load new frames into the buffer but checks if the frames are already in the buffer
        Uses a bit more memory than _load()
        :param index: the index in the video to start loading from
        :return:
        """

        temp_buffer = []
        self._frames.set(cv2.CAP_PROP_POS_FRAMES, index)
        buffer_used = False
        for i in range(self._buffer_length):
            if self._start <= i <= (self._start + self._buffer_length):
                temp_buffer.append(self._buffer[i - self._start])
                buffer_used = True
            elif buffer_used:
                self._frames.set(cv2.CAP_PROP_POS_FRAMES, i)
                temp_buffer.append(self._frames.read()[1])
                buffer_used = False
            else:
                temp_buffer.append(self._frames.read()[1])

            self._buffer = temp_buffer

# TODO: write some tests for the buffer object
