import os
from pathlib import Path
from typing import List


def get_project_path() -> Path:
    """Get the path to the project's root directory.

    Returns
    -------
    project_path : Path
        The path to the root directory of the project.
    """
    file_dir = os.path.dirname(os.path.realpath(__file__))
    dir_path = Path(file_dir)
    project_path = dir_path.parent
    return project_path


def check_vid_path(vid_path):
    vid_path = os.path.realpath(vid_path)
    videos_path = str(get_project_path() / 'videos')
    valid = True
    if len(vid_path) < len(videos_path):
        valid = False
    elif vid_path[:len(videos_path)] != videos_path:
        valid = False
    elif not os.path.isfile(vid_path):
        valid = False
    if not valid:
        raise ValueError(f'Invalid video path {vid_path}.')


def get_video_mapped_path(vid_path, dir_suffix, file_extension):
    check_vid_path(vid_path=vid_path)
    vid_path = os.path.realpath(vid_path)
    videos_path = get_project_path() / 'videos'
    vid_relative_path = vid_path[len(str(videos_path)):]
    data_path = get_project_path() / f'{dir_suffix}{vid_relative_path}'
    data_path = data_path.with_suffix(file_extension)
    return data_path


def get_video_paths() -> List[Path]:
    videos_path = get_project_path() / 'videos'
    vid_paths = []
    for root, dirs, files in os.walk(videos_path):
        for file in files:
            path = os.path.join(root, file)
            if _is_video_file(path=path):
                vid_paths.append(path)
    return vid_paths


def _is_video_file(path) -> bool:
    path = str(path)
    valid = True
    if not os.path.isfile(path):
        valid = False
    elif not (path.endswith(('.mp4', '.wmv'))):
        valid = False
    return valid
