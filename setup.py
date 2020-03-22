from setuptools import setup, find_packages

NAME = 'movement-detector'
VERSION = '0.1.0'
DESCRIPTION = 'Detect movement in videos.'
INSTALL_PACKAGES = [
    'numpy==1.18.1',
    'pandas==1.0.1',
    'scipy==1.4.1',
    'opencv-python==4.1.0.25',
    'moviepy==1.0.1',
    'imageio==2.6.1',
    'pygame==1.9.6',
    'PyYAML>=5.1',
]
DEV_PACKAGES = [
    'pytest',
    'sphinx',
    'sphinx_rtd_theme',
    'numpydoc',
]
APP = ['main.py']
DATA_FILES = []
OPTIONS = {}


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    # url={'Documentation': '', 'Source': ''},
    author='Petio Petrov',
    license='GNU GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python 3.6',
        'Programming Language :: Python 3.7',
        'Programming Language :: Python 3.8',
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
        include=['movement_detector', 'movement_detector.*']
    ),
)
