from setuptools import setup, find_packages


setup(
    name='movement_detector',
    version='0.1.0',
    description='Detect movement in videos.',
    url={'Documentation': '', 'Source': ''},
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
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
        'opencv-python',
        'pims',
    ],
    extras_require={
        'dev': [
            'pytest',
            'sphinx',
            'sphinx_rtd_theme',
            'numpydoc',
        ]
    },
    package_dir={'': ''},
    packages=find_packages(
        include=['movement_detector', 'movement_detector.*']
    ),
)
