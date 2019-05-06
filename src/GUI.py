from tkinter import *

class GUI(object):

	def __init__(self, queue, mainQueue):

		# Process objects
		self.queue = queue
		self.mainQueue = mainQueue
		self.LOG_PREFIX = "GUI: "

		# GUI Init
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

		deconvolutionState = BooleanVar()
		deconvolutionButton = Checkbutton(scanConfigFrame, text="Perform Deconvolution After Scan", variable=deconvolutionState, command=lambda: self.button_push_callback(5, 15, [deconvolutionState.get()]))

		refractiveIndexImmersion = DoubleVar()
		refractiveIndexImmersionScale = Scale(scanConfigFrame, variable=refractiveIndexImmersion, orient=HORIZONTAL, showvalue=0, label="Refractive Index Immersion", length=200,from_=0.1,to=2.0, resolution=0.01, command=self.update_scale_bar_refrarive_index_immersion)
		self.refractiveIndexImmersionLabel = Label(scanConfigFrame, text="1.33")
		refractiveIndexImmersionScale.set(1.33)


		numericalApertureCollection = DoubleVar()
		numericalApertureCollectionScale = Scale(scanConfigFrame, variable=numericalApertureCollection, orient=HORIZONTAL, showvalue=0, label="Numerical Aperture Collection", length=200,from_=0.1,to=2.0, resolution=0.05, command=self.update_scale_bar_numerical_aperture_collection)
		self.numericalApertureCollectionLabel = Label(scanConfigFrame, text="0.5")
		numericalApertureCollectionScale.set(0.5)


		wavelengthEmmision = IntVar()
		wavelengthEmmisionScale = Scale(scanConfigFrame, variable=wavelengthEmmision, orient=HORIZONTAL, showvalue=0, label="Emission Wavelength(nm)", length=200,from_=200,to=1000, resolution=1, command=self.update_scale_bar_wavelength_emmision)
		self.wavelengthEmmisionLabel = Label(scanConfigFrame, text="530nm")
		wavelengthEmmisionScale.set(530)

		nanometersPerPixel = IntVar()
		nanometersPerPixelScale = Scale(scanConfigFrame, variable=nanometersPerPixel, orient=HORIZONTAL, showvalue=0, label="Nanometers Per Pixel", length=200,from_=10,to=2000, resolution=1, command=self.update_scale_bar_nanometers_per_pixel)
		self.nanometersPerPixelLabel = Label(scanConfigFrame, text="177")
		nanometersPerPixelScale.set(177)

		richardsonLucyIterations = IntVar()
		richardsonLucyIterationsScale = Scale(scanConfigFrame, variable=richardsonLucyIterations, orient=HORIZONTAL, showvalue=0, label="Deconvolution Iterations", length=200,from_=1,to=500, resolution=1, command=self.update_scale_bar_richardson_lucy_iterations)
		self.richardsonLucyIterationsLabel = Label(scanConfigFrame, text="1")
		richardsonLucyIterationsScale.set(1)


		self.magnification = IntVar()
		self.magnification.set(20)  # set the default option
		magnifications = {5, 10, 20, 40, 63}
		magnificationLabel = Label(scanConfigFrame, text="Imaging Objective Magnification",)
		magnificationDropdown = OptionMenu(scanConfigFrame, self.magnification, *magnifications)

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
		refractiveIndexImmersionScale.pack()
		self.refractiveIndexImmersionLabel.pack()
		numericalApertureCollectionScale.pack()
		self.numericalApertureCollectionLabel.pack()
		wavelengthEmmisionScale.pack()
		self.wavelengthEmmisionLabel.pack()
		nanometersPerPixelScale.pack()
		self.nanometersPerPixelLabel.pack()
		richardsonLucyIterationsScale.pack()
		self.richardsonLucyIterationsLabel.pack()
		magnificationLabel.pack()
		magnificationDropdown.pack()
		self.magnification.trace('w', self.update_magnification_dropdown)

		scanNameEntry.pack(pady=(10,0))
		setScanName.pack(pady=(0,10))
		scanButton.pack()
		scanTimelapseButton.pack()
		deconvolutionButton.pack()

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

	def update_scale_bar_refrarive_index_immersion(self, refractiveIndexImmersion):

		self.refractiveIndexImmersionLabel.config(text=str(refractiveIndexImmersion))
		self.button_push_callback(5, 10, [refractiveIndexImmersion])

	def update_scale_bar_numerical_aperture_collection(self, numericalApertureCollection):

		self.numericalApertureCollectionLabel.config(text=str(numericalApertureCollection))
		self.button_push_callback(5, 11, [numericalApertureCollection])

	def update_scale_bar_wavelength_emmision(self, wavelengthEmmision):

		self.wavelengthEmmisionLabel.config(text=str(wavelengthEmmision) + "nm")
		self.button_push_callback(5, 12, [wavelengthEmmision])

	def update_scale_bar_nanometers_per_pixel(self, nanometersPerPixel):

		self.nanometersPerPixelLabel.config(text=str(nanometersPerPixel))
		self.button_push_callback(5, 13, [nanometersPerPixel])

	def update_scale_bar_richardson_lucy_iterations(self, iterations):

		self.richardsonLucyIterationsLabel.config(text=str(iterations))
		self.button_push_callback(5, 14, [iterations])

	def update_magnification_dropdown(self, *args):
		self.button_push_callback(1, 4, [int(self.magnification.get())])

def launch_gui(queue, mainQueue):

	gui = GUI(queue, mainQueue)
	print("GUI Process: Initialization complete")
	gui.master.mainloop()
