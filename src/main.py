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
		return false
	else:
		camera.GainAuto.SetValue(PySpin.GainAuto_Off)

	if camera.Gain.GetAccessMode() != PySpin.RW:
		print("Unable to set gain. Aborting...")
		return false
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



def map_analog_to_discrete_range(value, leftMin, leftMax, rightMin, rightMax):

    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    valueScaled = float(value - leftMin) / float(leftSpan)
    return rightMin + (valueScaled * rightSpan)


def handle_ps4_event(msg, cameraController, arduinoController):

	button_data = msg[0]
	axis_data = msg[1]
	hat_data = msg[2]

	LS_HORIZONTAL = axis_data.get(0)
	LS_VERTICAL = axis_data.get(1)
	RS_HORIZONTAL = axis_data.get(2)
	RS_VERTICAL = axis_data.get(3)

	if(LS_VERTICAL == None):
		LS_VERTICAL = 0
	if(RS_VERTICAL == None):
		RS_VERTICAL = 0



	if(button_data[3] == True):
		cameraController.toggle_preview()
		sleep(1)

	elif(button_data[0] == True):
		arduinoController.COARSE_JOG = not arduinoController.COARSE_JOG
		print("COARSE_JOG set to: ",arduinoController.COARSE_JOG)
		sleep(1)

	elif(LS_VERTICAL > 0.3):
		arduinoController.move_motor(1,-100)

	elif(LS_VERTICAL < -0.3):
		arduinoController.move_motor(1,100)

	elif(RS_VERTICAL > 0.3):
		arduinoController.move_motor(2,-100)

	elif(RS_VERTICAL < -0.3):
		arduinoController.move_motor(2,100)

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








def handle_gui_event(msg, cameraController, arduinoController):

	global SCAN_DEPTH, STEP_SIZE, SCAN_NAME


	functionIndex = msg[0]
	args = msg[1]

	if(functionIndex == 0):
		arduinoController.move_motor(args[0], args[1])
	elif(functionIndex == 2):
		cameraController.toggle_preview()
	elif(functionIndex == 3):
		cameraController.EXPOSURE = int(args[0])
	elif(functionIndex == 4):
		cameraController.GAIN = int(args[0])
	elif(functionIndex == 5):
		SCAN_DEPTH = int(args[0])
	elif(functionIndex == 6):
		STEP_SIZE = int(args[0])
	elif(functionIndex == 7):
		SCAN_NAME = args[0]
	elif(functionIndex == 8):
		performScan(cameraController, arduinoController)
	elif(functionIndex == 9):
		arduinoController.toggle_laser()
	else:
		print("Invalid function index received from GUI!")



def launch_gui_process(queue):

	guiProc = Process(target=launch_gui, args=(queue,))
	guiProc.start()
	return guiProc

def launch_ps4_process(queue):

	ps4Proc = Process(target=launch_ps4_controller, args=(queue,))
	ps4Proc.start()
	return ps4Proc







def main():

	cameraController = CameraController(50000, 25)
	arduinoController = ArduinoController("COM3", 9600)
	while(True):
		print(arduinoController.serialInterface.readline().decode())
"""
	ps4Queue = Queue()
	ps4Proc = launch_ps4_process(ps4Queue)

	guiQueue = Queue()
	guiProc = launch_gui_process(guiQueue)


	while(True):

		if(not ps4Queue.empty()):
			ps4msg = ps4Queue.get()
			handle_ps4_event(ps4msg, cameraController, arduinoController)
			while not ps4Queue.empty():
				ps4Queue.get()


		if(not guiQueue.empty()):
			guimsg = guiQueue.get()
			handle_gui_event(guimsg, cameraController, arduinoController)
			while not guiQueue.empty():
				guiQueue.get()

"""


if __name__ == '__main__':
    main()
