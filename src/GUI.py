from tkinter import *
import tkinter.scrolledtext as tkst
from PIL import ImageTk, Image
import cv2
import threading
import time
from time import sleep
import numpy as np


class GUI(object):

    def __init__(self, queue, mainQueue, videoQueue, logQueue):
        # Process objects
        self.queue = queue
        self.mainQueue = mainQueue
        self.videoQueue = videoQueue
        self.logQueue = logQueue
        self.LOG_PREFIX = "GUI: "

        # GUI Init
        self.master = Tk()
        self.master.geometry("2560x1440")
        self.dark_color = "#2E4053"
        self.light_color = "#5D6D7E"
        self.scale_trough_color = "#2E4053"
        self.scale_border_color = "#212F3C"
        self.text_colour = "#D5D8DC"
        self.frame_border_color = "#1C2833"
        self.button_focus_color = "#2E4053"
        self.gen_widgets()
        self.master.attributes("-fullscreen", True)


        self.micrometersPerStep = 0.15625
        self.micrometersPerPush = 10

        # Video Stream
        self.stopEvent = threading.Event()
        self.videoThread = threading.Thread(target=self.videoLoop, args=())
        self.logThread = threading.Thread(target=self.logLoop, args=())
        self.videoThread.start()
        self.logThread.start()

        self.logQueue.put(self.LOG_PREFIX + "Initialization complete")

    def __del__(self):
        pass

    def videoLoop(self):

        while not self.stopEvent.is_set():

            if not self.videoQueue.empty():

                frame = self.videoQueue.get()[2][0]
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = cv2.resize(image, dsize=(1024, 768), interpolation=cv2.INTER_CUBIC)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)
                self.videoWindow.configure(image=image)
                self.videoWindow.image = image





    def logLoop(self):

        while not self.stopEvent.is_set():

            while self.logQueue.empty():
                sleep(0.05)

            logMsg = " " + self.logQueue.get() + "\n"
            self.logBox.insert(INSERT, logMsg)
            self.logBox.yview_moveto(1)


    def gen_widgets(self):
        logFrame = Frame(self.master, borderwidth=2, relief=RIDGE, bg=self.dark_color, highlightbackground=self.frame_border_color, highlightcolor=self.frame_border_color)
        self.logBox = tkst.ScrolledText(master=logFrame, wrap=WORD, borderwidth=0, height=6, bg="black", fg="RoyalBlue1", relief=FLAT)
        logFrame.pack(side=BOTTOM, fill="both", expand="yes")
        self.logBox.pack(fill="both", expand="yes", padx=4)


        hardwareControlFrame = Frame(self.master, borderwidth=2, relief=RIDGE, bg=self.dark_color, highlightbackground=self.frame_border_color, highlightcolor=self.frame_border_color)
        movementButtonsFrame = Frame(hardwareControlFrame, bg=self.dark_color)
        controllerPictureFrame = Frame(hardwareControlFrame, bg=self.dark_color)
        quitButton = Button(controllerPictureFrame, text="QUIT", font=20, width=20, height=2, fg=self.text_colour, bg=self.light_color, activebackground=self.button_focus_color
                            , command=self.quit_callback)
        self.controllerImg = ImageTk.PhotoImage(Image.open("C:\\Projects\\Lightsheet\\resources\\ps4controller.png"))
        imgPanel = Label(controllerPictureFrame, image=self.controllerImg, bg=self.dark_color)
        y_inc = Button(movementButtonsFrame, text="y+", font=20, width=4, height=2, fg=self.text_colour, bg=self.light_color,
                       activebackground=self.button_focus_color,
                       command=lambda: self.button_push_callback(2, 3,
                                                                 [1, self.micrometersPerPush / self.micrometersPerStep,
                                                                  False]))
        y_dec = Button(movementButtonsFrame, text="y-", font=20, width=4, height=2, fg=self.text_colour, bg=self.light_color,
                       activebackground=self.button_focus_color,
                       command=lambda: self.button_push_callback(2, 3,
                                                                 [1, -self.micrometersPerPush / self.micrometersPerStep,
                                                                  False]))
        x_inc = Button(movementButtonsFrame, text="x+", font=20, width=4, height=2, fg=self.text_colour, bg=self.light_color,
                       activebackground=self.button_focus_color,
                       command=lambda: self.button_push_callback(2, 3,
                                                                 [3, self.micrometersPerPush / self.micrometersPerStep,
                                                                  False]))
        x_dec = Button(movementButtonsFrame, text="x-", font=20, width=4, height=2, fg=self.text_colour, bg=self.light_color,
                       activebackground=self.button_focus_color,
                       command=lambda: self.button_push_callback(2, 3,
                                                                 [3, -self.micrometersPerPush / self.micrometersPerStep,
                                                                  False]))
        z_inc = Button(movementButtonsFrame, text="z+", font=20, width=4, height=2, fg=self.text_colour, bg=self.light_color,
                       activebackground=self.button_focus_color,
                       command=lambda: self.button_push_callback(2, 3,
                                                                 [2, self.micrometersPerPush / self.micrometersPerStep,
                                                                  False]))
        z_dec = Button(movementButtonsFrame, text="z-", font=20, width=4, height=2, fg=self.text_colour, bg=self.light_color,
                       activebackground=self.button_focus_color,
                       command=lambda: self.button_push_callback(2, 3,
                                                                 [2, -self.micrometersPerPush / self.micrometersPerStep,
                                                                  False]))
        stepsPerButtonPush = StringVar()
        stepsPerButtonPush.set("10")
        stepsPerButtonPushLabel = Label(movementButtonsFrame, fg=self.text_colour,
                                        text="Use these buttons to make the stage \nperform precise movements. The \nnumber in the box specifies how many \nmicrometers the stage will move per \nbutton push.",
                                        justify=LEFT, bg=self.dark_color)
        SPPEntry = Entry(movementButtonsFrame, textvariable=stepsPerButtonPush, bd=5, fg=self.text_colour, bg=self.dark_color)
        setSPP = Button(movementButtonsFrame, text="Set μm Per Push",
                        command=lambda: self.update_steps_per_push(SPPEntry.get()), fg=self.text_colour, bg=self.light_color, highlightbackground=self.scale_border_color,)
        togglePreview = Button(hardwareControlFrame, text="Toggle Live Preview", fg=self.text_colour, bg=self.light_color, highlightbackground=self.scale_border_color,
                               command=lambda: self.button_push_callback(1, 0, []))
        hardwareControlFrame.pack(side=LEFT, fill="both", expand="yes")
        movementButtonsFrame.pack(side=BOTTOM, fill="both", pady=50, padx=(5, 0))
        controllerPictureFrame.pack(side=TOP, fill="both", expand="yes")

        imgPanel.pack(padx=(10, 0), fill="both", expand=True)
        quitButton.pack()
        y_inc.grid(row=1, column=7, padx=4, pady=(4,0), stick=S)
        y_dec.grid(row=3, column=7, padx=4, pady=4, stick=N)
        x_inc.grid(row=2, column=8, padx=4, pady=4)
        x_dec.grid(row=2, column=6, padx=4, pady=4)
        z_inc.grid(row=1, column=10, padx=(8,0), stick=S)
        z_dec.grid(row=3, column=10, padx=(8,0), stick=N)
        stepsPerButtonPushLabel.grid(row=1, column=3, padx=(10, 10), stick=W)
        SPPEntry.grid(row=2, column=3, padx=(20, 10), stick=W)
        setSPP.grid(row=3, column=3, padx=(20, 10), stick=NW)


        scanConfigFrame = Frame(self.master, borderwidth=2, relief=RIDGE, bg=self.dark_color, highlightbackground=self.frame_border_color, highlightcolor=self.frame_border_color)

        scanConfigFrameLabel = Label(scanConfigFrame, text="Scan Configuration", font=16, fg=self.text_colour, bg=self.dark_color)

        scanDepth = IntVar()
        scanDepthScale = Scale(scanConfigFrame, variable=scanDepth, orient=HORIZONTAL, showvalue=0,
                               label="Slices Per Stack", length=200, from_=10, to=1500, resolution=10,
                               command=self.update_scale_bar_scan_depth, fg=self.text_colour, bg=self.light_color, troughcolor=self.scale_trough_color, highlightbackground=self.scale_border_color)
        self.scanDepthLabel = Label(scanConfigFrame, text="10 Slices", fg=self.text_colour, bg=self.dark_color)
        stepSize = IntVar()
        stepSizeScale = Scale(scanConfigFrame, variable=stepSize, fg=self.text_colour, orient=HORIZONTAL, showvalue=0, label="Step Size(μm)",
                              length=200, from_=1, to=64, resolution=1, command=self.update_scale_bar_step_size, bg=self.light_color, troughcolor=self.scale_trough_color, highlightbackground=self.scale_border_color)
        self.stepSizeLabel = Label(scanConfigFrame, text="0.15625μm", fg=self.text_colour, bg=self.dark_color)
        timelapseN = IntVar()
        timelapseNScale = Scale(scanConfigFrame, fg=self.text_colour, variable=timelapseN, orient=HORIZONTAL, showvalue=0,
                                label="Timelapse Iterations", length=200, from_=1, to=100, resolution=1,
                                command=self.update_scale_bar_timelapse_n, bg=self.light_color,  troughcolor=self.scale_trough_color, highlightbackground=self.scale_border_color)
        self.timelapseNLabel = Label(scanConfigFrame, text="1 Iterations", fg=self.text_colour, bg=self.dark_color)
        timelapseDelayBetweenStacks = IntVar()
        timelapseDelayBetweenStacksScale = Scale(scanConfigFrame, fg=self.text_colour, variable=timelapseDelayBetweenStacks,
                                                 orient=HORIZONTAL, showvalue=0,
                                                 label="Timelapse Delay Between Stacks (s)", length=200, from_=10,
                                                 to=1000, resolution=1, command=self.update_scale_bar_timelapse_delay, bg=self.light_color, troughcolor=self.scale_trough_color, highlightbackground=self.scale_border_color)
        self.timelapseDelayBetweenStacksLabel = Label(scanConfigFrame, text="10s", fg=self.text_colour, bg=self.dark_color)
        deconvolutionState = BooleanVar()
        deconvolutionButton = Checkbutton(scanConfigFrame, text="Perform Deconvolution After Scan",
                                          variable=deconvolutionState,
                                          command=lambda: self.button_push_callback(5, 15, [deconvolutionState.get()]), fg=self.text_colour, bg=self.dark_color, highlightbackground=self.scale_border_color, selectcolor=self.light_color)
        refractiveIndexImmersion = DoubleVar()
        refractiveIndexImmersionScale = Scale(scanConfigFrame, fg=self.text_colour, variable=refractiveIndexImmersion, orient=HORIZONTAL,
                                              showvalue=0, label="Refractive Index Immersion", length=200, from_=0.1,
                                              to=2.0, resolution=0.01,
                                              command=self.update_scale_bar_refrarive_index_immersion, bg=self.light_color, troughcolor=self.scale_trough_color, highlightbackground=self.scale_border_color)
        self.refractiveIndexImmersionLabel = Label(scanConfigFrame, text="1.33", fg=self.text_colour, bg=self.dark_color)
        refractiveIndexImmersionScale.set(1.33)
        numericalApertureCollection = DoubleVar()
        numericalApertureCollectionScale = Scale(scanConfigFrame, fg=self.text_colour, variable=numericalApertureCollection,
                                                 orient=HORIZONTAL, showvalue=0, label="Imaging Objective N.A",
                                                 length=200, from_=0.1, to=2.0, resolution=0.01,
                                                 command=self.update_scale_bar_numerical_aperture_collection, bg=self.light_color, troughcolor=self.scale_trough_color, highlightbackground=self.scale_border_color)
        self.numericalApertureCollectionLabel = Label(scanConfigFrame, text="0.5", fg=self.text_colour, bg=self.dark_color)
        numericalApertureCollectionScale.set(0.5)
        wavelengthEmmision = IntVar()
        wavelengthEmmisionScale = Scale(scanConfigFrame, fg=self.text_colour, variable=wavelengthEmmision, orient=HORIZONTAL, showvalue=0,
                                        label="Emission Wavelength (nm)", length=200, from_=200, to=1000, resolution=1,
                                        command=self.update_scale_bar_wavelength_emmision, bg=self.light_color, troughcolor=self.scale_trough_color, highlightbackground=self.scale_border_color)
        self.wavelengthEmmisionLabel = Label(scanConfigFrame, text="530nm", fg=self.text_colour, bg=self.dark_color)
        wavelengthEmmisionScale.set(530)
        richardsonLucyIterations = IntVar()
        richardsonLucyIterationsScale = Scale(scanConfigFrame, fg=self.text_colour, variable=richardsonLucyIterations, orient=HORIZONTAL,
                                              showvalue=0, label="Deconvolution Iterations", length=200, from_=1,
                                              to=500, resolution=1,
                                              command=self.update_scale_bar_richardson_lucy_iterations, bg=self.light_color, troughcolor=self.scale_trough_color, highlightbackground=self.scale_border_color)
        self.richardsonLucyIterationsLabel = Label(scanConfigFrame, text="1", fg=self.text_colour, bg=self.dark_color)
        richardsonLucyIterationsScale.set(1)
        self.magnification = IntVar()
        self.magnification.set(5)  # set the default option
        magnifications = {2, 5, 10, 20, 40, 63}
        magnificationLabel = Label(scanConfigFrame, text="Imaging Objective Magnification", fg=self.text_colour, bg=self.dark_color)
        magnificationDropdown = OptionMenu(scanConfigFrame, self.magnification, *magnifications)
        magnificationDropdown.config(bg=self.light_color)
        magnificationDropdown.config(highlightbackground=self.scale_border_color)

        scanNameLabel = Label(scanConfigFrame, text="Scan Name", fg=self.text_colour, bg=self.dark_color)
        scanName = StringVar()
        scanName.set("default")
        self.scanNameEntry = Entry(scanConfigFrame, textvariable=scanName, bd=5, fg=self.text_colour, bg=self.dark_color)
        scanButton = Button(scanConfigFrame, text="Scan Stack", fg=self.text_colour, height=3, font=16, command=lambda: self.button_push_callback(5, 0, [self.scanNameEntry.get()]), bg=self.light_color, highlightbackground=self.scale_border_color,)
        scanTimelapseButton = Button(scanConfigFrame, fg=self.text_colour, height=3, font=16, text="Scan Timelapse",
                                     command=lambda: self.button_push_callback(5, 7, [self.scanNameEntry.get()]), bg=self.light_color, highlightbackground=self.scale_border_color,)
        scanTiledButton = Button(scanConfigFrame, text="Scan Tiles", fg=self.text_colour, height=3, font=16, command=lambda: self.button_push_callback(5, 17, [self.scanNameEntry.get()]), bg=self.light_color, highlightbackground=self.scale_border_color,)
        scanConfigFrame.pack(side=RIGHT, fill="both", expand="yes")
        scanConfigFrameLabel.pack(side=TOP, pady=(0,20))
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
        magnificationLabel.pack(pady=(10, 0))
        magnificationDropdown.pack()
        self.magnification.trace('w', self.update_magnification_dropdown)

        deconvolutionButton.pack(pady=(40, 0))
        richardsonLucyIterationsScale.pack()
        self.richardsonLucyIterationsLabel.pack(pady=(0, 20))

        scanTiledButton.pack(side=BOTTOM, fill=X, padx=10, pady=5)
        scanTimelapseButton.pack(side=BOTTOM, fill=X, padx=10, pady=5)
        scanButton.pack(side=BOTTOM, fill=X, padx=10, pady=5)
        self.scanNameEntry.pack(side=BOTTOM, fill=X, padx=10, pady=2)
        scanNameLabel.pack(side=LEFT, padx=(10,0))



        cameraFeedFrame = Frame(self.master, borderwidth=2, relief=RIDGE, bg=self.dark_color, highlightbackground=self.frame_border_color, highlightcolor=self.frame_border_color)
        cameraFeedFrame.pack(side=LEFT, fill="both",  expand="yes")
        self.videoFeedFrame = ImageTk.PhotoImage(Image.open("C:\\Projects\\Lightsheet\\resources\\inprogress.png"))
        self.videoWindow = Label(cameraFeedFrame, image=self.videoFeedFrame, width=1024, height=768, bg=self.dark_color)
        explanationLabel = Label(cameraFeedFrame, text="Camera Live Feed", font=16, fg=self.text_colour, bg=self.dark_color)
        gain = IntVar()
        gainScale = Scale(cameraFeedFrame, fg=self.text_colour, variable=gain, orient=HORIZONTAL, showvalue=0, label="Gain", length=200,
                          from_=1, to=40, resolution=1, command=self.update_scale_bar_gain, bg=self.light_color, troughcolor=self.scale_trough_color, highlightbackground=self.scale_border_color)
        self.gainLabel = Label(cameraFeedFrame, text="23dB", fg=self.text_colour, bg=self.dark_color)
        gainScale.set(23)
        exposure = DoubleVar()
        exposureScale = Scale(cameraFeedFrame, fg=self.text_colour, variable=exposure, orient=HORIZONTAL, showvalue=0, label="Exposure (ms)",
                              length=200, from_=5, to=100, resolution=5, command=self.update_scale_bar_exposure, bg=self.light_color, troughcolor=self.scale_trough_color, highlightbackground=self.scale_border_color)
        self.exposureLabel = Label(cameraFeedFrame, text="30ms", fg=self.text_colour, bg=self.dark_color)
        exposureScale.set(30)


        explanationLabel.pack()
        self.videoWindow.pack(pady=(5, 30), side=TOP)
        gainScale.pack(padx=(0, 800))
        self.gainLabel.pack(padx=(0, 800))
        exposureScale.pack(padx=(0, 800))
        self.exposureLabel.pack(padx=(0, 800))



    def quit_callback(self):

        print(self.LOG_PREFIX + "QUIT RECEIVED")
        msg = [-1, -1, ["QUIT"]]
        self.mainQueue.put(msg)
        exit()

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


def launch_gui(queue, mainQueue, videoQueue, logQueue):
    gui = GUI(queue, mainQueue, videoQueue, logQueue)
    gui.master.mainloop()
