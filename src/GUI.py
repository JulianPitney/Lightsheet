from tkinter import *
import tkinter.scrolledtext as tkst
from PIL import ImageTk, Image
import cv2
import threading
import imutils
import os


class GUI(object):

    def __init__(self, queue, mainQueue):
        # Process objects
        self.queue = queue
        self.mainQueue = mainQueue
        self.LOG_PREFIX = "GUI: "

        # GUI Init
        self.master = Tk()
        self.master.geometry("2560x1440")
        self.gen_widgets()
        self.micrometersPerStep = 0.15625
        self.micrometersPerPush = 10

        # Video Stream
        self.lastFrame = []
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

    def videoLoop(self):

        # keep looping over frames until we are instructed to stop
        while not self.stopEvent.is_set():
            # grab the frame from the video stream and resize it to
            # have a maximum width of 300 pixels
            frameAvailable = self.IPC_request_frame_from_camera()
            if frameAvailable:
                #self.lastFrame = imutils.resize(self.lastFrame, width=300)
                # OpenCV represents images in BGR order; however PIL
                # represents images in RGB order, so we need to swap
                # the channels, then convert to PIL and ImageTk format
                image = cv2.cvtColor(self.lastFrame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)
                self.videoWindow.configure(image=image)
                self.videoWindow.image = image




    def IPC_request_frame_from_camera(self, ):

        self.mainQueue.put([1, 5, [0, 4, -1]])
        msg = self.queue.get()
        functionIndex = msg[1]
        if functionIndex == -1:
            frameAvailable = msg[2][1]
            if frameAvailable:
                frame = msg[2][0]
                self.lastFrame = frame
                return True

        return False


    def gen_widgets(self):
        logFrame = Frame(self.master, borderwidth=2, relief=RIDGE)
        logBox = tkst.ScrolledText(master=logFrame, wrap=WORD, height=16, bg="black", fg="RoyalBlue1")
        logFrame.pack(side=BOTTOM, fill="both", expand="yes", padx=5)
        logBox.pack(fill="both", expand="yes", padx=4)
        logBox.insert(INSERT, "THIS BOX WILL CONTAIN LOG INFORMATION AND STATUS UPDATES\n")
        logBox.insert(INSERT, "CameraProcess: INFO= TEST LOG MESSAGE!\n")
        logBox.insert(INSERT, "ArduinoProcess: INFO= TEST LOG MESSAGE!\n")
        logBox.insert(INSERT, "PS4Process: INFO= TEST LOG MESSAGE!\n")
        logBox.insert(INSERT, "ScannerProcess: INFO= TEST LOG MESSAGE!\n")

        hardwareControlFrame = Frame(self.master, borderwidth=2, relief=RIDGE)
        movementButtonsFrame = Frame(hardwareControlFrame)
        controllerPictureFrame = Frame(hardwareControlFrame)
        self.controllerImg = ImageTk.PhotoImage(Image.open("C:/Users/Lightsheet/Desktop/ps4Controller.png"))
        imgPanel = Label(controllerPictureFrame, image=self.controllerImg)
        y_inc = Button(movementButtonsFrame, text="y+", font=20, width=4, height=2, bg="slate gray",
                       activebackground="dark slate gray", bd=2, relief=GROOVE,
                       command=lambda: self.button_push_callback(2, 3,
                                                                 [1, self.micrometersPerPush / self.micrometersPerStep,
                                                                  False]))
        y_dec = Button(movementButtonsFrame, text="y-", font=20, width=4, height=2, bg="slate gray",
                       activebackground="dark slate gray", bd=2, relief=GROOVE,
                       command=lambda: self.button_push_callback(2, 3,
                                                                 [1, -self.micrometersPerPush / self.micrometersPerStep,
                                                                  False]))
        x_inc = Button(movementButtonsFrame, text="x+", font=20, width=4, height=2, bg="slate gray",
                       activebackground="dark slate gray", bd=2, relief=GROOVE,
                       command=lambda: self.button_push_callback(2, 3,
                                                                 [3, self.micrometersPerPush / self.micrometersPerStep,
                                                                  False]))
        x_dec = Button(movementButtonsFrame, text="x-", font=20, width=4, height=2, bg="slate gray",
                       activebackground="dark slate gray", bd=2, relief=GROOVE,
                       command=lambda: self.button_push_callback(2, 3,
                                                                 [3, -self.micrometersPerPush / self.micrometersPerStep,
                                                                  False]))
        z_inc = Button(movementButtonsFrame, text="z+", font=20, width=4, height=2, bg="slate gray",
                       activebackground="dark slate gray", bd=2, relief=GROOVE,
                       command=lambda: self.button_push_callback(2, 3,
                                                                 [2, self.micrometersPerPush / self.micrometersPerStep,
                                                                  False]))
        z_dec = Button(movementButtonsFrame, text="z-", font=20, width=4, height=2, bg="slate gray",
                       activebackground="dark slate gray", bd=2, relief=GROOVE,
                       command=lambda: self.button_push_callback(2, 3,
                                                                 [2, -self.micrometersPerPush / self.micrometersPerStep,
                                                                  False]))
        stepsPerButtonPush = StringVar()
        stepsPerButtonPush.set("10")
        stepsPerButtonPushLabel = Label(movementButtonsFrame,
                                        text="Use these buttons to make the stage \nperform precise movements. The \nnumber in the box specifies how many \nmicrometers the stage will move per \nbutton push.",
                                        justify=LEFT)
        SPPEntry = Entry(movementButtonsFrame, textvariable=stepsPerButtonPush, bd=5)
        setSPP = Button(movementButtonsFrame, text="Set μm Per Push",
                        command=lambda: self.update_steps_per_push(SPPEntry.get()))
        togglePreview = Button(hardwareControlFrame, text="Toggle Live Preview",
                               command=lambda: self.button_push_callback(1, 0, []))
        hardwareControlFrame.pack(side=LEFT, fill="both", expand="yes", padx=(5,0))
        movementButtonsFrame.pack(side=BOTTOM, fill="both", pady=50, padx=(5, 0))
        controllerPictureFrame.pack(side=TOP, fill="both", expand="yes")

        imgPanel.pack(padx=(10, 0), fill="both", expand=True)
        y_inc.grid(row=1, column=7, padx=4, pady=4)
        y_dec.grid(row=3, column=7, padx=4, pady=4)
        x_inc.grid(row=2, column=8, padx=4, pady=4)
        x_dec.grid(row=2, column=6, padx=4, pady=4)
        z_inc.grid(row=1, column=10, padx=(8,0), pady=4)
        z_dec.grid(row=3, column=10, padx=(8,0), pady=4)
        stepsPerButtonPushLabel.grid(row=1, column=3, padx=(10, 10), stick=W)
        SPPEntry.grid(row=2, column=3, padx=(20, 10), stick=W)
        setSPP.grid(row=3, column=3, padx=(20, 10), stick=NW)


        scanConfigFrame = Frame(self.master, borderwidth=0)
        scanDepth = IntVar()
        scanDepthScale = Scale(scanConfigFrame, variable=scanDepth, orient=HORIZONTAL, showvalue=0,
                               label="Slices Per Stack", length=200, from_=10, to=1500, resolution=10,
                               command=self.update_scale_bar_scan_depth)
        self.scanDepthLabel = Label(scanConfigFrame, text="10 Slices")
        stepSize = IntVar()
        stepSizeScale = Scale(scanConfigFrame, variable=stepSize, orient=HORIZONTAL, showvalue=0, label="Step Size(μm)",
                              length=200, from_=1, to=64, resolution=1, command=self.update_scale_bar_step_size)
        self.stepSizeLabel = Label(scanConfigFrame, text="0.15625μm")
        timelapseN = IntVar()
        timelapseNScale = Scale(scanConfigFrame, variable=timelapseN, orient=HORIZONTAL, showvalue=0,
                                label="Timelapse Iterations", length=200, from_=1, to=100, resolution=1,
                                command=self.update_scale_bar_timelapse_n)
        self.timelapseNLabel = Label(scanConfigFrame, text="1 Iterations")
        timelapseDelayBetweenStacks = IntVar()
        timelapseDelayBetweenStacksScale = Scale(scanConfigFrame, variable=timelapseDelayBetweenStacks,
                                                 orient=HORIZONTAL, showvalue=0,
                                                 label="Timelapse Delay Between Stacks(s)", length=200, from_=10,
                                                 to=1000, resolution=1, command=self.update_scale_bar_timelapse_delay)
        self.timelapseDelayBetweenStacksLabel = Label(scanConfigFrame, text="10s")
        deconvolutionState = BooleanVar()
        deconvolutionButton = Checkbutton(scanConfigFrame, text="Perform Deconvolution After Scan",
                                          variable=deconvolutionState,
                                          command=lambda: self.button_push_callback(5, 15, [deconvolutionState.get()]))
        refractiveIndexImmersion = DoubleVar()
        refractiveIndexImmersionScale = Scale(scanConfigFrame, variable=refractiveIndexImmersion, orient=HORIZONTAL,
                                              showvalue=0, label="Refractive Index Immersion", length=200, from_=0.1,
                                              to=2.0, resolution=0.01,
                                              command=self.update_scale_bar_refrarive_index_immersion)
        self.refractiveIndexImmersionLabel = Label(scanConfigFrame, text="1.33")
        refractiveIndexImmersionScale.set(1.33)
        numericalApertureCollection = DoubleVar()
        numericalApertureCollectionScale = Scale(scanConfigFrame, variable=numericalApertureCollection,
                                                 orient=HORIZONTAL, showvalue=0, label="Numerical Aperture Imaging",
                                                 length=200, from_=0.1, to=2.0, resolution=0.01,
                                                 command=self.update_scale_bar_numerical_aperture_collection)
        self.numericalApertureCollectionLabel = Label(scanConfigFrame, text="0.5")
        numericalApertureCollectionScale.set(0.5)
        wavelengthEmmision = IntVar()
        wavelengthEmmisionScale = Scale(scanConfigFrame, variable=wavelengthEmmision, orient=HORIZONTAL, showvalue=0,
                                        label="Emission Wavelength(nm)", length=200, from_=200, to=1000, resolution=1,
                                        command=self.update_scale_bar_wavelength_emmision)
        self.wavelengthEmmisionLabel = Label(scanConfigFrame, text="530nm")
        wavelengthEmmisionScale.set(530)
        richardsonLucyIterations = IntVar()
        richardsonLucyIterationsScale = Scale(scanConfigFrame, variable=richardsonLucyIterations, orient=HORIZONTAL,
                                              showvalue=0, label="Deconvolution Iterations", length=200, from_=1,
                                              to=500, resolution=1,
                                              command=self.update_scale_bar_richardson_lucy_iterations)
        self.richardsonLucyIterationsLabel = Label(scanConfigFrame, text="1")
        richardsonLucyIterationsScale.set(1)
        self.magnification = IntVar()
        self.magnification.set(20)  # set the default option
        magnifications = {5, 10, 20, 40, 63}
        magnificationLabel = Label(scanConfigFrame, text="Imaging Objective Magnification", )
        magnificationDropdown = OptionMenu(scanConfigFrame, self.magnification, *magnifications)
        scanName = StringVar()
        scanName.set("default")
        scanNameEntry = Entry(scanConfigFrame, textvariable=scanName, bd=5)
        setScanName = Button(scanConfigFrame, text="Set Scan Name",
                             command=lambda: self.button_push_callback(5, 3, [scanNameEntry.get()]))
        scanButton = Button(scanConfigFrame, text="Scan Stack", command=lambda: self.button_push_callback(5, 0, []))
        scanTimelapseButton = Button(scanConfigFrame, text="Scan Timelapse",
                                     command=lambda: self.button_push_callback(5, 7, []))

        scanConfigFrame.pack(side=RIGHT, fill="both", expand="yes")
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
        richardsonLucyIterationsScale.pack()
        self.richardsonLucyIterationsLabel.pack()
        magnificationLabel.pack()
        magnificationDropdown.pack()
        self.magnification.trace('w', self.update_magnification_dropdown)
        scanNameEntry.pack(pady=(10, 0))
        setScanName.pack(pady=(0, 10))
        scanButton.pack()
        scanTimelapseButton.pack()
        deconvolutionButton.pack()



        cameraFeedFrame = Frame(self.master, borderwidth=2, relief=GROOVE)
        cameraFeedFrame.pack(side=LEFT, fill="both",  expand="yes")
        self.videoFeedFrame = ImageTk.PhotoImage(Image.open("C:/Users/Lightsheet/Desktop/inprogress.png"))
        self.videoWindow = Label(cameraFeedFrame, image=self.videoFeedFrame, width=1024, height=700)
        explanationLabel = Label(cameraFeedFrame, text="Lightsheet Live Feed", font=16)
        gain = IntVar()
        gainScale = Scale(cameraFeedFrame, variable=gain, orient=HORIZONTAL, showvalue=0, label="Gain", length=200,
                          from_=1, to=40, resolution=1, command=self.update_scale_bar_gain)
        self.gainLabel = Label(cameraFeedFrame, text="23dB")
        gainScale.set(23)
        exposure = DoubleVar()
        exposureScale = Scale(cameraFeedFrame, variable=exposure, orient=HORIZONTAL, showvalue=0, label="Exposure(ms)",
                              length=200, from_=5, to=100, resolution=5, command=self.update_scale_bar_exposure)
        self.exposureLabel = Label(cameraFeedFrame, text="30ms")
        exposureScale.set(30)


        explanationLabel.pack()
        self.videoWindow.pack(pady=(5, 0), side=TOP)
        gainScale.pack(padx=(0, 800))
        self.gainLabel.pack(padx=(0, 800))
        exposureScale.pack(padx=(0, 800))
        self.exposureLabel.pack(padx=(0, 800))




    def button_push_callback(self, processIndex, functionIndex, args):
        msg = [processIndex, functionIndex, args]
        self.mainQueue.put(msg)

    def update_steps_per_push(self, steps):
        self.micrometersPerPush = int(steps)

    def update_scale_bar_gain(self, gain):
        self.gainLabel.config(text=str(gain) + "dB")
        self.button_push_callback(1, 2, [int(gain)])

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
        self.button_push_callback(5, 16, [int(self.magnification.get())])


def launch_gui(queue, mainQueue):
    gui = GUI(queue, mainQueue)
    print("GUI Process: Initialization complete")
    gui.master.mainloop()
