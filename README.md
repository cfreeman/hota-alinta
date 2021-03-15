# HOTA-alinta

This python application uses a webcam and tensorflow to detect
the prescence of people. It turns a rasperry pi into an activity sensor that uses relays to trigger other electronic systems.


## DEVELOPMENT
Command to start sensor application:
* python3 sensor.py --model=/home/pi/alinta-sensor/detect.tflite --labels=/home/pi/alinta-sensor/coco_labels.txt


## TODO
* ~~Two relays instead of one.~~
* ~~Script / instructions of everything you need to install to get it working.~~
* ~~Test each of the sensors:~~
	* ~~Make sure they boot correctly.~~
	* ~~Copy across python test code.~~
	* ~~Test to make sure they trigger the encoder correctly.~~
* ~~Tidy up the sensor code.~~
	* ~~Define a hotspot region. Only trigger when someone is within a region wihtin the middle of the frame.~~
	* ~~When someone is detected, have a configurable delay before the relays are turned off.~~
	* ~~When the application boots up, save the first frame as a debug for configuration purposes.~~
	* ~~Hang the sensor off my deck and work out how big that region needs to be (for a hooler hoop).~~
	* ~~Start on raspberry pi boot. systemd.~~
* ~~Configure the PI to be an access point.~~
* ~~Label ports.~~
* ~~Test to make sure no wifi clashses or anything when all six
are powered up at the same time.~~
* ~~Requesting the keys in Alinta's application be updated: x, c, j, k, i, w~~
* ~~Set everything up in the mac-mini and test it for a long time.~~
* ~~Test that the encoder connection with the sensors is all working.~~
* Test to make sure that the system resets correctly on power failure.
* Test long duration (8+ hours)

## CONFIG
### SD CARD
$ diskutil list
$ diskutil unmountDisk /dev/diskN
$ sudo dd bs=1m if=path_of_your_image.img of=/dev/rdiskN; sync
$ cd /Volume/boot
$ vim ssh

### SENSORS
1. Boot the pi for the first time:
* Set the location.
* Set the keyboard
* Set the password to one used for HOTA-sensor
* Wait for the pi to run package setup.

2. Open a terminal:
* sudo raspi-config
* Enable camera: 3 - Interface options, P1 Camera, enable
* reboot

3. Install application dependancies:
* pip3 install virtualenv Pillow numpy pygame
* pip3 install https://github.com/google-coral/pycoral/releases/download/release-frogfish/tflite_runtime-2.5.0-cp37-cp37m-linux_armv7l.whl

4. Setup ssh keys:
* mkdir .ssh
* chmod 700 .ssh
* sudo apt-get install vim
* cd .ssh
* vim authorized_keys

5. copy code across.

6. Configure networking
* ./network.sh

7. Setup sensor to run as a systemd service
* cd alinta-sensor
* sudo cp sensor.service /lib/systemd/system/sensor.service
* sudo systemctl enable sensor.service
* sudo systemctl start sensor.service
* sudo systemctl status sensor.service

### MAC MINI
* Notifications - Do Not Disturb - Always On.
* Users & Groups - Login Options - Automatic login.
* Users * Groups - hota-cg1 - login items - add startup app.
* Dock & Menu Bar - automatically hide and show the dock.
* Energy Saver - Never turn display off.
* Energy Saver - Start up automatically after a power failiure.
* Desktop & Screen Saver - Screen Saver - Start after - never.
* Desktop & Screen Saver - Desktop - Colours - black.
* ?? Configure the mini so that it reboots each night. ??


## FAILURE MODES
* If the screensaver kicks in, the keyboard becomes unresponsive in Alinta's application.
* Maybe have a script that checks the content of the python app on boot. If it's corrupted, copy across from a backup.


## TROUBLESHOOTING

TBD.


## LICENSE
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
