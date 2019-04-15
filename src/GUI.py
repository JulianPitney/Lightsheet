from tkinter import *


class GUI(object):

	def __init__(self, queue, mainQueue):

		self.queue = queue
		self.mainQueue = mainQueue
		self.master = Tk()
		self.gen_widgets()
		self.stepsPerPush = 10

	def gen_widgets(self):

		stageAdjustFrame = Frame(self.master)
		y_inc = Button(stageAdjustFrame, text="y+", command=lambda: self.button_push_callback(2, 3, [1,self.stepsPerPush, False]))
		y_dec = Button(stageAdjustFrame, text="y-", command=lambda: self.button_push_callback(2, 3, [1,-self.stepsPerPush, False]))
		x_inc = Button(stageAdjustFrame, text="x+", command=lambda: self.button_push_callback(2, 3, [3,self.stepsPerPush, False]))
		x_dec = Button(stageAdjustFrame, text="x-", command=lambda: self.button_push_callback(2, 3, [3,-self.stepsPerPush, False]))
		z_inc = Button(stageAdjustFrame, text="z+", command=lambda: self.button_push_callback(2, 3, [2,self.stepsPerPush, False]))
		z_dec = Button(stageAdjustFrame, text="z-", command=lambda: self.button_push_callback(2, 3, [2,-self.stepsPerPush, False]))
		stepsPerButtonPush = StringVar()
		stepsPerButtonPush.set("10")
		SPPEntry = Entry(stageAdjustFrame, textvariable=stepsPerButtonPush, bd=5)
		setSPP = Button(stageAdjustFrame, text="Set SPP", command=lambda: self.update_steps_per_push(SPPEntry.get()))
		togglePreview = Button(stageAdjustFrame, text="Toggle Live Preview", command=lambda: self.button_push_callback(1, 0, []))

		scanConfigFrame = Frame(self.master)
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
		var = DoubleVar()
		scale = Scale(scanConfigFrame, variable=var, orient=HORIZONTAL, label="		Exposure(ms)", length=200,from_=5,to=100, resolution=5, command=self.update_scale_bar_exposure)
		scanButton = Button(scanConfigFrame, text="SCAN!", command=lambda: self.button_push_callback(5, 0, []))
		scanTimelapseButton = Button(scanConfigFrame, text="SCAN TIMELAPSE!", command=lambda: self.button_push_callback(5, 7, []))


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
		gainEntry.pack()
		setGain.pack()
		scanDepthEntry.pack()
		setScanDepth.pack()
		stepSizeEntry.pack()
		setStepSize.pack()
		scanNameEntry.pack()
		setScanName.pack()
		scale.pack()
		scanButton.pack(pady=10)
		scanTimelapseButton.pack(pady=10)


	def button_push_callback(self, processIndex, functionIndex, args):

		msg = [processIndex, functionIndex, args]
		self.mainQueue.put(msg)

	def update_steps_per_push(self, steps):

		self.stepsPerPush = int(steps)

	def update_scale_bar_exposure(self, exposure):
		# convert to microseconds for Spinnaker
		exposure = int(exposure) * 1000
		self.button_push_callback(1, 1, [exposure])

def launch_gui(queue, mainQueue):

	gui = GUI(queue, mainQueue)
	gui.master.mainloop()
