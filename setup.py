from os import path
from pathlib import Path
import re

from setuptools import setup, find_packages

NAME = 'movement-detector'
VERSION = 'v0.2.4'
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
INTERFACE_PACKAGES = [
    'pygame==1.9.6',
]
DEV_PACKAGES = [
    'PyYAML>=5.1',
    'pytest==5.4.1',
    'sphinx==2.4.4',
    'sphinx_rtd_theme==0.4.3',
    'numpydoc==0.9.2',
    'sphinxcontrib-napoleon==0.7',
    'twine',
    'bumpversion',
]
APP = ['main.py']
DATA_FILES = []
OPTIONS = {}


def fix_readme(txt):
    return re.sub(r'\.\. PYPI-BEGIN([\r\n]|.)*?PYPI-END', '', txt, re.DOTALL)


with open(THIS_DIR / 'README.md', encoding='utf-8') as f:
    LONG_DESCRIPTION = fix_readme(f.read())

with open(THIS_DIR / 'LICENSE.txt', encoding='utf-8') as f:
    LICENSE = f.read()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    # url={'Documentation': '', 'Source': ''},
    author='Petio Petrov',
    license=LICENSE,
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
        'dev': DEV_PACKAGES,
        'interface': INTERFACE_PACKAGES,
    },
    # package_dir={'': ''},
    packages=find_packages(
        include=['movement_detector', 'movement_detector.*'],
    ),
    url='https://github.com/petioptrv/movement_detector',
)
