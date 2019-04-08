from CameraController import *
from ArduinoController import *
from GUI import *
from PS4Controller import *
from Scanner import *
from multiprocessing import Process, Queue
from time import sleep



def launch_arduino_process(queue):
	ardProc = Process(target=launch_arduino_controller, args=(queue,))
	ardProc.start()
	return ardProc

def launch_camera_process(queue):
	camProc = Process(target=launch_camera, args=(queue,))
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

def launch_scanner_process(queue):
	scannerProc = Process(target=launch_scanner, args=(queue,))
	scannerProc.start()
	return scannerProc


def route_message(msg):

	global cameraQueue, arduinoQueue, ps4Queue, guiQueue, scannerQueue
	proc_index = msg[0]

	if proc_index == 0:
		pass
	elif proc_index == 1:
		cameraQueue.put(msg)
	elif proc_index == 2:
		arduinoQueue.put(msg)
	elif proc_index == 3:
		ps4Queue.put(msg)
	elif proc_index == 4:
		guiQueue.put(msg)
	elif proc_index == 5:
		scannerQueue.put(msg)




cameraQueue = Queue(0)
arduinoQueue = Queue(0)
ps4Queue = Queue(0)
guiQueue = Queue(0)
scannerQueue = Queue(0)

def main():

	camProc = launch_camera_process(cameraQueue)
	ardProc = launch_arduino_process(arduinoQueue)
	ps4Proc = launch_ps4_process(ps4Queue)
	guiProc = launch_gui_process(guiQueue)
	scanProc = launch_scanner_process(scannerQueue)

	while True:

		if not cameraQueue.empty():
			route_message(cameraQueue.get())
		if not arduinoQueue.empty():
			route_message(arduinoQueue.get())
		if not ps4Queue.empty():
			route_message(ps4Queue.get())
		if not guiQueue.empty():
			route_message(guiQueue.get())
		if not scannerQueue.empty():
			route_message(scannerQueue.get())


		# This delay is preventing deadlock caused by the queues shared by main and ps4process.
		# No idea why but don't remove it.
		sleep(0.03)

if __name__ == '__main__':
	main()
