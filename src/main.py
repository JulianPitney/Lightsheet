from CameraController import *
from ArduinoController import *
from GUI import *
from PS4Controller import *
from multiprocessing import Process, Queue
from time import sleep
import PySpin
import os
import pprint



SCAN_DEPTH = None
STEP_SIZE = None
SCAN_NAME = None
SERIAL_PORT_PATH = "COM3"
BAUDRATE = 57600
EXPOSURE = 10000
GAIN = 25




def performScan(cameraController, arduinoController):

	global SCAN_DEPTH, STEP_SIZE, SCAN_NAME

	camList, system = cameraController.init_spinnaker()
	camera = camList.GetByIndex(0)
	cameraController.init_camera(camera, False, 'SingleFrame')

	incrementCommand = "MOVE S2 " + str(STEP_SIZE) + "\n"
	incrementCommand = incrementCommand.encode('UTF-8')

	path = os.getcwd() + '\\' + SCAN_NAME

	try:
		os.mkdir(path)
	except OSError:
		print ("Creation of the directory %s failed" % path)
	else:
		print ("Successfully created the directory %s " % path)




	# set exposure
	if camera.ExposureAuto.GetAccessMode() != PySpin.RW:
		print('Unable to disable automatic exposure. Aborting...')
		return False
	else:
		camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)

	if camera.ExposureTime.GetAccessMode() != PySpin.RW:
		print('Unable to set exposure time. Aborting...')
		return False
	else:
		# Ensure desired exposure time does not exceed the maximum
		cameraController.EXPOSURE = min(camera.ExposureTime.GetMax(), cameraController.EXPOSURE)
		camera.ExposureTime.SetValue(cameraController.EXPOSURE)

		# set gain
	if camera.GainAuto.GetAccessMode() != PySpin.RW:
		print("Unable to disable automatic gain. Aborting...")
		return False
	else:
		camera.GainAuto.SetValue(PySpin.GainAuto_Off)

	if camera.Gain.GetAccessMode() != PySpin.RW:
		print("Unable to set gain. Aborting...")
		return False
	else:
		cameraController.GAIN = min(camera.Gain.GetMax(), cameraController.GAIN)
		camera.Gain.SetValue(cameraController.GAIN)



	# Acquisition Start
	for i in range(0,SCAN_DEPTH):
		camera.BeginAcquisition()
		# This will hang until an image is available in the camera buffer.
		# The camera will acquire an image after receiving a signal on Line0
		image_result = camera.GetNextImage()
		if image_result.IsIncomplete():
			print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
		else:
			image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
			filename = path + "\\" + str(i) + ".jpg"
			image_converted.Save(filename)
			image_result.Release()
			print("FRAME CAPTURED")
		camera.EndAcquisition()
		arduinoController.serialInterface.write(incrementCommand)
		response = arduinoController.serialInterface.readline().decode()
		print(response)


	camera.DeInit()
	del camera
	camList.Clear()
	system.ReleaseInstance()




"""
	button_data[0]  SQUARE
	button_data[1]  X
	button_data[2]  CIRCLE
	button_data[3]  TRIANGLE
	button_data[4]  L1
	button_data[5]  R1
	button_data[6]  L2
	button_data[7]  R2
	button_data[8]  SHARE
	button_data[9]  OPTIONS
	button_data[10]  L3
	button_data[11]  R3
	button_data[12]  PS
	button_data[13]  TRACKPAD
"""








def launch_arduino_process(queue, SERIAL_PORT_PATH, BAUDRATE):

	ardProc = Process(target=launch_arduino_controller, args=(queue, SERIAL_PORT_PATH, BAUDRATE,))
	ardProc.start()
	return ardProc

def launch_camera_process(queue, EXPOSURE, GAIN):

	camProc = Process(target=launch_camera, args=(queue, EXPOSURE, GAIN))
	camProc.start()
	return camProc

def launch_gui_process(queue):

	guiProc = Process(target=launch_gui, args=(queue,))
	guiProc.start()
	return guiProc

def launch_ps4_process(queue):

	ps4Proc = Process(target=launch_ps4_controller, args=(queue,))
	ps4Proc.start()
	return ps4Proc


def route_message(msg):

	global cameraQueue, arduinoQueue, ps4Queue, guiQueue
	proc_index = msg[0]

	if(proc_index == 0):
		process_msg(msg)
	elif(proc_index == 1):
		cameraQueue.put(msg)
	elif(proc_index == 2):
		arduinoQueue.put(msg)
	elif(proc_index == 3):
		ps4Queue.put(msg)
	elif(proc_index == 4):
		guiQueue.put(msg)


def process_msg(msg):

	global SCAN_DEPTH, SCAN_STEP_SIZE, SCAN_NAME

	functionIndex = msg[1]

	if(functionIndex == 0):
		SCAN_DEPTH = msg[2][0]
	elif(functionIndex == 1):
		SCAN_STEP_SIZE = msg[2][0]
	elif(functionIndex == 2):
		SCAN_NAME = msg[2][0]
	elif(functionIndex == 3):
		print("perform scan!")


cameraQueue = Queue(0)
arduinoQueue = Queue(0)
ps4Queue = Queue(0)
guiQueue = Queue(0)


def main():
	ps4msgs = 0

	global cameraQueue, arduinoQueue, ps4Queue, guiQueue
	camProc = launch_camera_process(cameraQueue, EXPOSURE, GAIN)
	ardProc = launch_arduino_process(arduinoQueue, SERIAL_PORT_PATH, BAUDRATE)
	ps4Proc = launch_ps4_process(ps4Queue)
	guiProc = launch_gui_process(guiQueue)

	while True:
		if not cameraQueue.empty():
			route_message(cameraQueue.get())
		if not arduinoQueue.empty():
			route_message(arduinoQueue.get())
		if not ps4Queue.empty():
			print(str(ps4msgs))
			ps4msgs += 1
			route_message(ps4Queue.get())
		if not guiQueue.empty():
			route_message(guiQueue.get())

		print("MAINPROC: " + str(ps4Queue.qsize()))
		sleep(0.001)

if __name__ == '__main__':
    main()
