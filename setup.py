from os import path
from pathlib import Path

from setuptools import setup, find_packages

NAME = 'movement-detector'
VERSION = 'v0.1.11'
DESCRIPTION = 'Detect movement in videos.'
THIS_DIR = Path(path.abspath(path.dirname(__file__)))
INSTALL_PACKAGES = [
    'numpy==1.18.1',
    'pandas==1.0.1',
    'scipy==1.4.1',
    'opencv-python==4.1.2.30',
    'moviepy==1.0.1',
    'imageio==2.6.1',
]
DEV_PACKAGES = [
    'PyYAML>=5.1',
    'pygame==1.9.6',
    'pytest==5.4.1',
    'twine',
]

with open(THIS_DIR / 'docs' / 'requirements.txt', encoding='utf-8') as f:
    DOCS_REQUIREMENTS = f.read().split('\n')

DEV_PACKAGES.extend(DOCS_REQUIREMENTS)
APP = ['main.py']
DATA_FILES = []
OPTIONS = {}

with open(THIS_DIR / 'README.md', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    # url={'Documentation': '', 'Source': ''},
    author='Petio Petrov',
    license='GNU GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='movement detection freezing behavioural behaviour behavioral'
             'behavior research',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=INSTALL_PACKAGES,
    extras_require={
        'dev': DEV_PACKAGES
    },
    # package_dir={'': ''},
    packages=find_packages(
        include=['movement_detector', 'movement_detector.*'],
    ),
    url='https://github.com/petioptrv/movement_detector',
    download_url=f'https://github.com/petioptrv/movement_detector/archive/{VERSION}.tar.gz',
)
