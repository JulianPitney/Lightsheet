from CameraController import *
from ArduinoController import *
from GUI import *
from PS4Controller import *
from multiprocessing import Process, Queue
from time import sleep
import PySpin
import os



SCAN_DEPTH = None
STEP_SIZE = None
SCAN_NAME = None
SCAN_STEP_SPEED = 60
SERIAL_PORT_PATH = "COM3"
BAUDRATE = 9600
EXPOSURE = 100000
GAIN = 25




def performScan():

	global SCAN_DEPTH, STEP_SIZE, SCAN_NAME, SCAN_STEP_SPEED
	global EXPOSURE, GAIN, BAUDRATE, SERIAL_PORT_PATH

	cameraController = CameraController(Queue(), EXPOSURE, GAIN)
	arduinoController = ArduinoController(Queue(), SERIAL_PORT_PATH, BAUDRATE)

	camList, system = cameraController.init_spinnaker()
	camera = camList.GetByIndex(0)
	cameraController.init_camera(camera, False, 'SingleFrame')

	incrementCommand = "MOVE S2 " + str(STEP_SIZE) + " " + str(SCAN_STEP_SPEED) + "\n"
	incrementCommand = incrementCommand.encode('UTF-8')

	path = os.getcwd() + '\\..\\scans\\' + SCAN_NAME

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
		print("WAIT: 0.5s")
		sleep(0.5)


	camera.DeInit()
	del camera
	camList.Clear()
	system.ReleaseInstance()





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

	global SCAN_DEPTH, STEP_SIZE, SCAN_NAME

	functionIndex = msg[1]

	if(functionIndex == 0):
		SCAN_DEPTH = int(msg[2][0])
		print("SCAN_DEPTH=" + str(msg[2][0]))
	elif(functionIndex == 1):
		STEP_SIZE = int(msg[2][0])
		print("STEP_SIZE=" + str(msg[2][0]))
	elif(functionIndex == 2):
		SCAN_NAME = msg[2][0]
		print("SCAN_NAME=" + str(msg[2][0]))
	elif(functionIndex == 3):
		print("Starting scan...")
		performScan()


cameraQueue = Queue(0)
arduinoQueue = Queue(0)
ps4Queue = Queue(0)
guiQueue = Queue(0)


def main():

	global cameraQueue, arduinoQueue, ps4Queue, guiQueue, EXPOSURE, GAIN
	camProc = launch_camera_process(cameraQueue, EXPOSURE, GAIN)
	ardProc = None #launch_arduino_process(arduinoQueue, SERIAL_PORT_PATH, BAUDRATE)
	ps4Proc = None #slaunch_ps4_process(ps4Queue)
	guiProc = launch_gui_process(guiQueue)

	while True:
		if not cameraQueue.empty():
			route_message(cameraQueue.get())
		if not arduinoQueue.empty():
			route_message(arduinoQueue.get())
		if not ps4Queue.empty():
			route_message(ps4Queue.get())
		if not guiQueue.empty():
			route_message(guiQueue.get())

		# This delay is preventing deadlock caused by the queues shared by main and ps4process.
		# No idea why but don't remove it.
		sleep(0.03)

if __name__ == '__main__':
	main()
