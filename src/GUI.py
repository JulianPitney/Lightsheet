from tkinter import *

class GUI(object):

	def __init__(self, queue, mainQueue):

		self.queue = queue
		self.mainQueue = mainQueue
		self.master = Tk()
		self.gen_widgets()
		self.stepsPerPush = 10

	def gen_widgets(self):


		"""
		print(self.master.tk.call('tk', 'windowingsystem'))
		menubar = Menu(self.master)
		filemenu = Menu(menubar, tearoff=0)
		filemenu.add_command(label="Quit")
		"""


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
		gain = IntVar()
		gainScale = Scale(scanConfigFrame, variable=gain, orient=HORIZONTAL, showvalue=0, label="Gain", length=200,from_=1,to=40, resolution=1, command=self.update_scale_bar_gain)
		self.gainLabel = Label(scanConfigFrame, text="23dB")
		gainScale.set(23)
		exposure = DoubleVar()
		exposureScale = Scale(scanConfigFrame, variable=exposure, orient=HORIZONTAL, showvalue=0, label="Exposure(ms)", length=200,from_=5,to=100, resolution=5, command=self.update_scale_bar_exposure)
		self.exposureLabel = Label(scanConfigFrame, text="30ms")
		exposureScale.set(30)
		scanDepth = IntVar()
		scanDepthScale = Scale(scanConfigFrame, variable=scanDepth, orient=HORIZONTAL, showvalue=0, label="Slices Per Stack", length=200,from_=10,to=1500, resolution=10, command=self.update_scale_bar_scan_depth)
		self.scanDepthLabel = Label(scanConfigFrame, text="10 Slices")
		stepSize = IntVar()
		stepSizeScale = Scale(scanConfigFrame, variable=stepSize, orient=HORIZONTAL, showvalue=0, label="Step Size(um)", length=200,from_=1,to=64, resolution=1, command=self.update_scale_bar_step_size)
		self.stepSizeLabel = Label(scanConfigFrame, text="0.15625um")

		timelapseN = IntVar()
		timelapseNScale = Scale(scanConfigFrame, variable=timelapseN, orient=HORIZONTAL, showvalue=0, label="Timelapse Iterations", length=200,from_=1,to=100, resolution=1, command=self.update_scale_bar_timelapse_n)
		self.timelapseNLabel = Label(scanConfigFrame, text="1 Iterations")
		timelapseDelayBetweenStacks = IntVar()
		timelapseDelayBetweenStacksScale = Scale(scanConfigFrame, variable=timelapseDelayBetweenStacks, orient=HORIZONTAL, showvalue=0, label="Timelapse Delay Between Stacks(s)", length=200,from_=10,to=1000, resolution=1, command=self.update_scale_bar_timelapse_delay)
		self.timelapseDelayBetweenStacksLabel = Label(scanConfigFrame, text="10s")


		scanName = StringVar()
		scanName.set("default")
		scanNameEntry = Entry(scanConfigFrame, textvariable=scanName, bd=5)
		setScanName = Button(scanConfigFrame, text="Set Scan Name", command=lambda: self.button_push_callback(5, 3, [scanNameEntry.get()]))
		scanButton = Button(scanConfigFrame, text="Scan Stack", command=lambda: self.button_push_callback(5, 0, []))
		scanTimelapseButton = Button(scanConfigFrame, text="Scan Timelapse", command=lambda: self.button_push_callback(5, 7, []))


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
		gainScale.pack()
		self.gainLabel.pack()
		exposureScale.pack()
		self.exposureLabel.pack()
		scanDepthScale.pack()
		self.scanDepthLabel.pack()
		stepSizeScale.pack()
		self.stepSizeLabel.pack()
		timelapseNScale.pack()
		self.timelapseNLabel.pack()
		timelapseDelayBetweenStacksScale.pack()
		self.timelapseDelayBetweenStacksLabel.pack()



		scanNameEntry.pack(pady=(10,0))
		setScanName.pack(pady=(0,10))
		scanButton.pack()
		scanTimelapseButton.pack()


	def button_push_callback(self, processIndex, functionIndex, args):

		msg = [processIndex, functionIndex, args]
		self.mainQueue.put(msg)

	def update_steps_per_push(self, steps):

		self.stepsPerPush = int(steps)

	def update_scale_bar_gain(self, gain):

		self.gainLabel.config(text=str(gain) + "dB")
		self.button_push_callback(1, 2, [gain])

	def update_scale_bar_exposure(self, exposure):

		self.exposureLabel.config(text=str(exposure) + "ms")
		# convert to microseconds for Spinnaker
		exposure = int(exposure) * 1000
		self.button_push_callback(1, 1, [exposure])

	def update_scale_bar_scan_depth(self, scanDepth):

		self.scanDepthLabel.config(text=str(scanDepth) + " Slices")
		self.button_push_callback(5, 2, [scanDepth])

	def update_scale_bar_step_size(self, stepSize):

		stepSize = int(stepSize) * 0.15625
		self.stepSizeLabel.config(text=str(stepSize) + "um")
		self.button_push_callback(5, 1, [stepSize])

	def update_scale_bar_timelapse_n(self, timelapseN):

		self.timelapseNLabel.config(text=str(timelapseN) + " Iterations")
		self.button_push_callback(5, 8, [int(timelapseN)])

	def update_scale_bar_timelapse_delay(self, timelapseDelay):

		self.timelapseDelayBetweenStacksLabel.config(text=timelapseDelay + "s")
		self.button_push_callback(5, 9, [int(timelapseDelay)])




def launch_gui(queue, mainQueue):

	gui = GUI(queue, mainQueue)
	gui.master.mainloop()
