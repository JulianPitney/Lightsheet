# Lightsheet

This repository contains everything needed to build and run the Bergeron Lab lightsheet microscope system.

The system is an "end-to-end solution". This means that we provide:

* Optics (Modified OpenSPIM design).
* Mounting Hardware.
* Stage Control System.
* Laser Control System.
* Camera Control System.
* Specimen Chamber.
* Easy to use GUI and PS4 Controller interface.
* Stack, Tiled and Time-lapse scan functions.

The goal of this system is to provide a low-cost, high-quality alternative to commercial lightsheet systems.
Our philosophy was "Do a small number of things really well". The goal was to make it very easy to take high quality scans while leaving any processing or analysis to other tools.
# Table of Contents
* [Installation](#installation)
* [Usage](#usage)
* [Contributing](#contributing)
* [Credits](#credits)
* [License](#license)


# Installation

**Hardware:**<br/>
[Parts List](https://docs.google.com/spreadsheets/d/18pRoh0PZBaclofkvuCLl1aGt24ObCIeX1hrV7fQlwLQ/edit?usp=sharing)


**Dependencies**

Name | Version
------------ | -------------
[Windows 10](https://www.microsoft.com/en-ca/windows/get-windows-10) | Latest Version
[Anaconda](https://www.anaconda.com/) | Latest Version
Python | 3.6.9
[Spinnaker SDK](https://drive.google.com/file/d/1ekqroxbpQbD4XAP_PvaEMywXw5San4l4/view?usp=sharing) | 1.20.0.15
[Spinnaker Python](https://drive.google.com/drive/folders/1aErW7o_pc7jhp2hj4MuVE-I-7R72fGmS?usp=sharing) | 1.20.0.15
[Arduino IDE](https://www.arduino.cc/en/main/OldSoftwareReleases) | 1.6.9
OpenCV | 4.1.1.26
PySerial | 3.4
tifffile | 2018.10.18
pillow | 6.1.0
dask | 2.5.0
pygame | 1.9.6
scikit-image | 0.15.0

**Installation Step-By-Step**

1. Start with a computer with Windows 10.
1. Download and install the most recent version of Anaconda from [here](https://www.anaconda.com/).
2. Download and install the Arduino IDE from [here](https://www.arduino.cc/en/main/OldSoftwareReleases).
5. Install the Spinnaker SDK using the executable installer provided [here](https://drive.google.com/file/d/1ekqroxbpQbD4XAP_PvaEMywXw5San4l4/view?usp=sharing). **Note:** If you don't want to trust this binary, you can email Flir and request the installer from them. Ask for the version specified in the dependencies table above.
5. Open Anaconda Prompt and create a virtual environment using this command ```conda create -n lightsheet python=3.6 ```
6. Enter the newly created environment using this command ```conda activate lightsheet```
7. Install OpenCV using the command ```pip install opencv-python```
8. Install PySerial using the command ```pip install pyserial```
9. Install tifffile using the command ```pip install tifffile```
10. Install pillow using the command ```pip install pillow```
11. Install dask[array] using the command ```pip install dask[array]```
12. Install pygame using the command ```pip install pygame```
13. Install scikit-image using the command ```pip install scikit-image```
14. Install the Spinnaker Python API by downloading [this]() folder and following the instructions in the README.txt contained within.
15. Upload ```./arduino/arduinoServer/arduinoServer.ino``` to your arduino mega.
16. If everything above worked correctly, navigate to ```./Lightsheet/src/``` and try to start the system with the command ```python main.py```

# Usage
1. Open a terminal and type ``conda activate flir-env``
2. Type ``python kinarena.py``
3. Select ``[2] New Trial`` to record a trial. For every trial a folder will be generated under ``~/anipose/experiments/<trial_name>``. 
4. At any time, you can select ``[3] Analyze Trials`` to automatically analyze all trials that have not yet been analyzed. Analysis takes a long time so don't do this until you're done recording and ready to walk away for the day.

# Contributing
Not ready for outside contribution.
# Credits
* [DeepLabCut authors](http://www.mousemotorlab.org/deeplabcut)
* [anipose authors](https://github.com/lambdaloop)
* [Boyang Wang](jwang149@gmail.com)
* [Bergeron Lab](jwang149@gmail.com)
* [Julian Pitney](www.julianpitney.com)

# License
Legal stuff

