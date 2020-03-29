.. movement-detector documentation master file, created by
   sphinx-quickstart on Sat Jan  4 19:13:31 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 1
   :hidden:

   self
   api

.. note::
   The Movement Detector (MD) library is in a minimal viable product (MVP) state. More usage is needed to iron-out the
   API and interface. For support or feedback, please contact petioptrv@icloud.com.

Welcome to movement-detector's documentation!
=============================================

The Movement Detector (MD) is a collection of classes enabling the detection of movement in video files. The original
purpose of the library is to enable the detection of freezing responses during behavioural experiments,
such as initially proposed by Blanchard and Blanchard 1988 [#id1]_.

However, the architecture of the classes permits the user to extend the capabilities of the library to virtually any
video-processing algorithm.

Installation
============
For Research Scientists (Mac)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The interface of MD is a work in progress, but scientists that want the most hassle-free experience can clone the
`repository <https://github.com/petioptrv/movement_detector>`_ and use the :code:`bash` script.

First, make sure you have `Python 3 <https://www.python.org/downloads/>`_ installed on your machine.

Open a Terminal window in the directory in which you wish to clone the repository. Copy and paste the following in
the terminal and hit Enter:

.. code-block:: console

   $ git clone https://github.com/petioptrv/movement_detector.git


Refer to the :ref:`research-scientists-section` section for usage details.

For Python Developers
^^^^^^^^^^^^^^^^^^^^^
For programmers who wish to use the MD's library of classes in their code, the installation can be done using :code:`pip`.

.. code-block:: console

   $ pip install movement-detector


Refer to the :ref:`API apge<api-docs>` for the full API documentation.

.. _research-scientists-section:

Research Scientists Workflow
============================
The detection algorithm used by the experimental interface of MD relies on the magnitude of the pixel-value changes
between frames to determine if there is movement in the video. Clusters of pixels with differing values from one frame
to the next are enclosed in bounding-boxes. The change value for a given frame is calculated as the ratio between the
total area of the pixel-change bounding boxes to the total area of the frame.

The GUI for MD is still in development, but an initial version is available for testing. The interactive session
consists in playing the video in the viewer to determine if the analysis was accurate or not, and manually making
adjustments in the latter case.

Viewer Setup
^^^^^^^^^^^^
#. Adjust the :ref:`settings<settings-section>`.
#. Copy the experiment videos in the "videos" folder.

   a. The videos can be arranged in a folder structure.
   b. All videos analyzed at the same time must have the same interval start and end times.

#. Open a Terminal window.
#. Drag and drop the `run.sh` file onto the terminal window.
#. Hit Enter.
#. See :ref:`controls-section` section for details on how to operate the viewer window.
#. Results are saved in the "analysis" folder and are arranged in the same folder structure as the video files.

.. _controls-section:

Viewer Controls
^^^^^^^^^^^^^^^
All key-commands, except for the space-bar, operate only while the video is on pause.

+----------+---------------------------------------------------------------------------------------+
| Key      | Setting Description                                                                   |
+==========+=======================================================================================+
| `<-`     | Previous frame.                                                                       |
+----------+---------------------------------------------------------------------------------------+
| `->`     | Next frame.                                                                           |
+----------+---------------------------------------------------------------------------------------+
| `f`      | Set current frame to "freezing" and move to next frame.                               |
+----------+---------------------------------------------------------------------------------------+
| `m`      | Set current frame to "moving" and move to next frame.                                 |
+----------+---------------------------------------------------------------------------------------+
| `n`      | Jump to the next flagged frame.                                                       |
+----------+---------------------------------------------------------------------------------------+
| `p`      | Jump to the previous flagged frame.                                                   |
+----------+---------------------------------------------------------------------------------------+
| `space`  | Play/pause video.                                                                     |
+----------+---------------------------------------------------------------------------------------+

.. _settings-section:

Settings
^^^^^^^^
Tweaking the algorithm to fit your particular video setup is crucial and can only be achieved through trial and error.
The `settings.txt` file contains all of the settings that can be optimized for the pixel-change detection algorithm.

+-----------------------------+---------------------------------------------------------------------------------------+
| Setting Name                | Setting Description                                                                   |
+=============================+=======================================================================================+
| `intervals`                 | | A list of the intervals' delimiting time-stamps. The start and end of the           |
|                             | | video are automatically included. E.g. for intervals 0-15, 15-30, and               |
|                             | | 30-45 seconds, where the video's duration is 45s, set `intervals = [15, 30]`.       |
+-----------------------------+---------------------------------------------------------------------------------------+
| `outlier_change_threshold`  | | The number of standard deviations from the mean that the pixel-change               |
|                             | | ratio must be to be considered an outlier. Outlier frames are flagged               |
|                             | | for manual review.                                                                  |
+-----------------------------+---------------------------------------------------------------------------------------+
| `flag_outliers_buffer`      | | The number of consecutive frames that must be identified as outliers in             |
|                             | | order to flag all those frames for review.                                          |
+-----------------------------+---------------------------------------------------------------------------------------+
| `movement_threshold`        | | A value between 0 and 1. The ratio of pixel-change areas relative to the            |
|                             | | area of the area of the image above which the frame will be flagged                 |
|                             | | as containing movement.                                                             |
+-----------------------------+---------------------------------------------------------------------------------------+
| `freezing_buffer`           | | The number of consecutive frames that must be identified as containing              |
|                             | | freezing in order to the `moving` field for all those frames to False.              |
+-----------------------------+---------------------------------------------------------------------------------------+
| `blur_ksize`                | | The size of the Gaussian blur filter. For more information                          |
|                             | | see `here <https://docs.opencv.org/master/d4/d13/tutorial_py_filtering.html>`_.     |
+-----------------------------+---------------------------------------------------------------------------------------+

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. rubric:: Footnotes

.. [#id1] Blanchard, D. C., & Blanchard, R. J. (1988). Experimental approaches to the biology of emotion. Annual review of psychology, 39(1), 43-68.

