from tkinter import *
from multiprocessing import Process, Queue
import os
import PySpin



class GUI(object):

	SCAN_DEPTH = 50
	SCAN_STEP_SIZE = 10
	SCAN_NAME = "default"
	stepsPerPush_y_inc = 10
	stepsPerPush_y_dec = -10
	stepsPerPush_x_inc = 10
	stepsPerPush_x_dec = -10
	stepsPerPush_z_inc = 10
	stepsPerPush_z_dec = -10
	displayPreview = False
	previewProcQueue = Queue()


	def __init__(self, queue):

		self.queue = queue
		self.master = Tk()
		self.gen_widgets()





	def gen_widgets(self):

		stageAdjustFrame = Frame(self.master)
		y_inc = Button(stageAdjustFrame, text="y+", command=lambda: self.button_push_callback(2, 3, [1,self.stepsPerPush_y_inc]))
		y_dec = Button(stageAdjustFrame, text="y-", command=lambda: self.button_push_callback(2, 3, [1,self.stepsPerPush_y_dec]))
		x_inc = Button(stageAdjustFrame, text="x+", command=lambda: self.button_push_callback(2, 3, [3,self.stepsPerPush_x_inc]))
		x_dec = Button(stageAdjustFrame, text="x-", command=lambda: self.button_push_callback(2, 3, [3,self.stepsPerPush_x_dec]))
		z_inc = Button(stageAdjustFrame, text="z+", command=lambda: self.button_push_callback(2, 3, [2,self.stepsPerPush_z_inc]))
		z_dec = Button(stageAdjustFrame, text="z-", command=lambda: self.button_push_callback(2, 3, [2,self.stepsPerPush_z_dec]))
		stepsPerButtonPush = StringVar()
		stepsPerButtonPush.set("10")
		SPPEntry = Entry(stageAdjustFrame, textvariable=stepsPerButtonPush, bd=5)
		setSPP = Button(stageAdjustFrame, text="Set SPP", command=lambda: self.update_steps_per_push(SPPEntry.get()))
		togglePreview = Button(stageAdjustFrame, text="Toggle Live Preview", command=lambda: self.button_push_callback(1, 0, []))

		scanConfigFrame = Frame(self.master)
		exposure = StringVar()
		exposure.set("50000")
		exposureEntry = Entry(scanConfigFrame, textvariable=exposure, bd=5)
		setExposure = Button(scanConfigFrame, text="Set Exposure", command=lambda: self.button_push_callback(1, 1, [exposureEntry.get()]))
		gain = StringVar()
		gain.set("25")
		gainEntry = Entry(scanConfigFrame, textvariable=gain, bd=5)
		setGain = Button(scanConfigFrame, text="Set Gain", command=lambda: self.button_push_callback(1, 2, [gainEntry.get()]))
		scanDepth = StringVar()
		scanDepth.set("50")
		scanDepthEntry = Entry(scanConfigFrame, textvariable=scanDepth, bd=5)
		setScanDepth = Button(scanConfigFrame, text="Set Scan Depth", command=lambda: self.button_push_callback(5, 2, [scanDepthEntry.get()]))
		stepSize = StringVar()
		stepSize.set("32")
		stepSizeEntry = Entry(scanConfigFrame, textvariable=stepSize, bd=5)
		setStepSize = Button(scanConfigFrame, text="Set Step Size", command=lambda: self.button_push_callback(5, 1, [stepSizeEntry.get()]))
		scanName = StringVar()
		scanNameEntry = Entry(scanConfigFrame, textvariable=scanName, bd=5)
		setScanName = Button(scanConfigFrame, text="Set Scan Name", command=lambda: self.button_push_callback(5, 3, [scanNameEntry.get()]))
		scanButton = Button(scanConfigFrame, text="SCAN!", command=lambda: self.button_push_callback(5, 0, []))
		toggleLaser = Button(scanConfigFrame, text="TOGGLE LASER", command=lambda: self.button_push_callback(2, 0, []))

		stageAdjustFrame.pack(side=LEFT)
		y_inc.pack(fill=X, padx=30)
		y_dec.pack(fill=X, padx=30)
		x_inc.pack(fill=X, padx=30)
		x_dec.pack(fill=X, padx=30)
		z_inc.pack(fill=X, padx=30)
		z_dec.pack(fill=X, padx=30)
		SPPEntry.pack(fill=X, padx=30)
		setSPP.pack(padx=30)
		togglePreview.pack(fill=X, padx=30)

		scanConfigFrame.pack(side=RIGHT,padx=50)
		exposureEntry.pack()
		setExposure.pack()
		gainEntry.pack()
		setGain.pack()
		scanDepthEntry.pack()
		setScanDepth.pack()
		stepSizeEntry.pack()
		setStepSize.pack()
		scanNameEntry.pack()
		setScanName.pack()
		scanButton.pack(pady=10)
		toggleLaser.pack()






	def button_push_callback(self, processIndex, functionIndex, args):

		msg = [processIndex, functionIndex, args]
		self.queue.put(msg)


	def update_steps_per_push(self, steps):

		self.stepsPerPush_y_inc = int(steps)
		self.stepsPerPush_y_dec = -int(steps)
		self.stepsPerPush_x_inc = int(steps)
		self.stepsPerPush_x_dec = -int(steps)
		self.stepsPerPush_z_inc = int(steps)
		self.stepsPerPush_z_dec = -int(steps)
		print("SPP set to: ", steps)


def launch_gui(queue):

	gui = GUI(queue)
	gui.master.mainloop()
