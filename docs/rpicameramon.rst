rpicameramon package
====================

This package provides camera security system functionality for the Raspberry Pi minicomputer.
It uses Raspberry Pi NoIR camera for the motion detection and also PIR sensor if available.

Capturing is handled by the picamera package and image processing is handled by the Pillow package.

Captured images are sent to the Google Drive storage.

Submodules
----------
Package itself consist of four submodules - config, filemanipulation, motion and telemetry.
Each of them has consist of several classes.

config module
--------------------------
Config modules is used for storing of the application configuration internally.
It consist of two classes - BaseConfig and UserConfig. UserConfig inherits from the BaseConfig class.

UserConfig class adds variables which can be loaded from the external JSON file.

.. automodule:: rpicameramon.config
    :members:
    :undoc-members:
    :show-inheritance:

rpicameramon.filemanipulation module
------------------------------------
This module consist of classes for the manipulation with files in Google Drive.

.. automodule:: rpicameramon.filemanipulation
    :members:
    :undoc-members:
    :show-inheritance:

rpicameramon.motion module
--------------------------
This module has functionality for the motion detection from the scene and also from the PIR sensor
and also SMS handler.
Optical flow method is used for the motion detection.

.. automodule:: rpicameramon.motion
    :members:
    :undoc-members:
    :show-inheritance:


rpicameramon.telemetry module
-----------------------------
This module provides functionality for sending telemetry data to the Google Sheets.

.. automodule:: rpicameramon.telemetry
    :members:
    :undoc-members:
    :show-inheritance:
