from time import *
from Deconvolver import *
import os
import os.path
import cv2
import numpy as np
from skimage import io
import tifffile as tif
import random

class Scanner(object):


    def __init__(self, queue, mainQueue, guiLogQueue):


        self.queue = queue
        self.mainQueue = mainQueue
        self.guiLogQueue = guiLogQueue
        self.LOG_PREFIX = "Scanner: "


        self.Z_STEP_SIZE_um = 0.15625
        self.STACK_SIZE = 10
        self.SCAN_STEP_SPEED = 50
        self.SCAN_NAME = "default"
        self.SLEEP_DURATION_AFTER_MOVEMENT_S = 0.5
        self.TIMELAPSE_N = 1
        self.TIMELAPSE_INTERVAL_S = 10
        self.TILE_SCAN_TRANSLATIONS = [[],[]]

        self.imagingObjectiveMagnification = 20
        self.umPerPixel_5x = 0.666
        self.umPerPixel_10x = 0.357
        self.umPerPixel_20x = 0.175
        self.umPerPixel_40x = 0.089
        self.umPerPixel_63x = 0.057

        # Deconvolution parameters
        self.deconvolver = Deconvolver()
        self.deconvolveAfterScan = False
        self.refractiveIndexImmersion = 1.33
        self.numericalAperture = 0.5
        self.wavelength = 530
        self.richardsonLucyIterations = 2
        self.sizeX = 1440
        self.sizeY = 1080
        self.nanometersPerPixel = 175

        self.guiLogQueue.put(self.LOG_PREFIX + "Initialization complete")

    def set_z_step_size(self, step_size_um):
        self.Z_STEP_SIZE_um = float(step_size_um)
        self.guiLogQueue.put(self.LOG_PREFIX + "Z_STEP_SIZE=" + str(step_size_um))

    def set_stack_size(self, stack_size):
        self.STACK_SIZE = int(stack_size)
        self.guiLogQueue.put(self.LOG_PREFIX + "STACK_SIZE=" + str(stack_size))

    def set_scan_step_speed(self, step_speed):
        self.SCAN_STEP_SPEED = int(step_speed)
        self.guiLogQueue.put(self.LOG_PREFIX + "SCAN_STEP_SPEED=" + str(step_speed))

    def set_scan_name(self, scan_name):
        self.SCAN_NAME = str(scan_name)
        self.guiLogQueue.put(self.LOG_PREFIX + "SCAN_NAME=" + str(scan_name))

    def set_sleep_duration_after_movement(self, duration_S):
        self.SLEEP_DURATION_AFTER_MOVEMENT_S = int(duration_S)
        self.guiLogQueue.put(self.LOG_PREFIX + "SLEEP_DURATION_AFTER_MOVEMENT_S=" + str(duration_S))

    def set_timelapse_n(self, timelapseN):
        self.TIMELAPSE_N = int(timelapseN)
        self.guiLogQueue.put(self.LOG_PREFIX + "TIMELAPSE_N=" + str(timelapseN))

    def set_timelapse_interval_s(self, timelapseInterval):
        self.TIMELAPSE_INTERVAL_S = int(timelapseInterval)
        self.guiLogQueue.put(self.LOG_PREFIX + "TIMELAPSE_INTERVAL_S=" + str(timelapseInterval))

    def set_refractive_index_immersion(self, refractiveIndexImmersion):
        self.refractiveIndexImmersion = refractiveIndexImmersion
        self.guiLogQueue.put(self.LOG_PREFIX + "REFRACTIVE_INDEX_IMMERSION=" + str(refractiveIndexImmersion))

    def set_numerical_aperture(self, numericalAperture):
        self.numericalAperture = numericalAperture
        self.guiLogQueue.put(self.LOG_PREFIX + "NUMERICAL_APERTURE_IMAGING=" + str(numericalAperture))

    def set_wavelength(self, wavelength):
        self.wavelength = wavelength
        self.guiLogQueue.put(self.LOG_PREFIX + "WAVELENGTH=" + str(wavelength))

    def set_nanometers_per_pixel(self, nanometersPerPixel):
        self.nanometersPerPixel = nanometersPerPixel
        self.guiLogQueue.put(self.LOG_PREFIX + "NANOMETERS_PER_PIXEL=" + str(nanometersPerPixel))

    def set_richardson_lucy_iterations(self, iterations):
        self.richardsonLucyIterations = iterations
        self.guiLogQueue.put(self.LOG_PREFIX + "RICHARDSON_LUCY_ITERATIONS=" + str(iterations))

    def set_deconvolve_after_scan(self, deconvolveAfterScan):
        self.deconvolveAfterScan = bool(deconvolveAfterScan)
        self.guiLogQueue.put(self.LOG_PREFIX + "DECONVOLVE_AFTER_SCAN=" + str(deconvolveAfterScan))

    def set_imaging_objective_magnification(self, magnification):

        magnification = int(magnification)
        self.imagingObjectiveMagnification = magnification

        if magnification == 5:
            self.nanometersPerPixel = 666
        elif magnification == 10:
            self.nanometersPerPixel == 357
        elif magnification == 20:
            self.nanometersPerPixel = 175
        elif magnification == 40:
            self.nanometersPerPixel = 89
        elif magnification == 63:
            self.nanometersPerPixel = 57


        self.guiLogQueue.put(self.LOG_PREFIX + "IMAGING_OBJECTIVE_MAGNIFICATION=" + str(magnification))


    def wait_for_confirmation(self, procIndex):

        while True:
            if not self.queue.empty():
                msg = self.queue.get()
                if msg[2][0] == procIndex:
                    break
                else:
                    pass


    def gen_scan_directory(self, scanName):

        path = os.getcwd() + '\\..\\scans\\' + scanName
        try:
            os.mkdir(path)
        except OSError:
            self.guiLogQueue.put(self.LOG_PREFIX + "Creation of the directory %s failed. Aborting scan." % path)
            return -1
        else:
            self.guiLogQueue.put(self.LOG_PREFIX + "Successfully created the directory %s " % path)
            return path



    def gen_stack_metadata(self):

        # Generate stack metadata
        metadata = []
        metadata.append(['z_step-size', self.Z_STEP_SIZE_um])
        metadata.append(['units', 'um'])
        metadata.append(['stack_size', self.STACK_SIZE])
        metadata.append(['motor_step_speed', self.SCAN_STEP_SPEED])
        metadata.append(['vibration_settle_delay', self.SLEEP_DURATION_AFTER_MOVEMENT_S])
        metadata.append(['timelapse_interval', self.TIMELAPSE_INTERVAL_S])
        metadata.append(['refractive_index_immersion', self.refractiveIndexImmersion])
        metadata.append(['numericalApertureCollection', self.numericalAperture])
        metadata.append(['wavelengthEmission', self.wavelength])
        metadata.append(['size_x', self.sizeX])
        metadata.append(['size_y', self.sizeY])
        metadata.append(['richardsonLucy_deconvolution_iterations', self.richardsonLucyIterations])
        return metadata

    def paint_scalebar(self, frame):

        umPixelsRatio = 10

        if self.imagingObjectiveMagnification == 5:
            umPixelsRatio = self.umPerPixel_5x
        elif self.imagingObjectiveMagnification == 10:
            umPixelsRatio = self.umPerPixel_10x
        elif self.imagingObjectiveMagnification == 20:
            umPixelsRatio = self.umPerPixel_20x
        elif self.imagingObjectiveMagnification == 40:
            umPixelsRatio = self.umPerPixel_40x
        elif self.imagingObjectiveMagnification == 63:
            umPixelsRatio = self.umPerPixel_63x


        height, width = frame.shape[:2]
        # Figure out how many pixels represent 10um
        lineLengthPixels = int(10 / umPixelsRatio)
        p1 = (50, height - 50)
        p2 = (50 + lineLengthPixels, height - 50)
        cv2.line(frame, p1, p2, (255, 255, 255), 2)

        cp1 = ((50 + int(lineLengthPixels / 2)), (height - 40))
        cp2 = ((50 + int(lineLengthPixels / 2)), (height - 60))
        cv2.line(frame, cp1, cp2, (255, 255, 255), 2)

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, '10um', ((int(lineLengthPixels / 2)), (height - 80)), font, 1, (255, 255, 255), 2,
                    cv2.LINE_AA)

        return frame


    def scan(self, scanType, scanName):

        self.set_scan_name(scanName)
        stackPaths = []

        if scanType == "stack":
            stackPath = self.scan_stack(self.SCAN_NAME, self.SCAN_NAME)
            if stackPath == -1:
                return -1
            else:
                stackPaths.append(stackPath)

        elif scanType == "timelapse":
            stackPaths = self.scan_timelapse()
            if stackPaths == -1:
                return -1

        elif scanType == "tiled":
            stackPaths = self.scan_tiles()
            if stackPaths == -1:
                return -1

        # Sleep to make sure CameraController process has time to save stacks to disk before we try to read them
        # Note: SHOULD wait for confirmation from camera process before continuing....maybe I'll get to it one day
        sleep(4)

        # deconvolve scan if selected
        if self.deconvolveAfterScan:
            self.guiLogQueue.put(self.LOG_PREFIX + "Scan deconvolution starting...")
            # generate psf for this scan
            path = stackPaths[0]
            path = os.path.dirname(path) + "\\"


            psfPath = self.deconvolver.gen_psf_PSFGenerator(self.refractiveIndexImmersion, self.wavelength, self.numericalAperture, self.nanometersPerPixel, self.Z_STEP_SIZE_um, self.sizeX, self.sizeY, self.STACK_SIZE, path)
            for stackPath in stackPaths:
                outputPath = os.path.dirname(stackPath) + "\\"
                deconvolvedStackPath = self.deconvolver.deconvolve_DeconvLab2(stackPath, psfPath, self.richardsonLucyIterations, outputPath)
                deconvolvedStack = io.imread(deconvolvedStackPath)
                deconvolvedStackMaxProj = np.max(deconvolvedStack, axis=0)
                deconvolvedStackMaxProj = self.paint_scalebar(deconvolvedStackMaxProj)
                filename = outputPath + "maxProj.tif"

                # Make sure we don't overwrite anything
                while os.path.exists(filename):
                    self.guiLogQueue.put(self.LOG_PREFIX + "An attempt was made to overwrite an existing file. This attempt has been blocked.")
                    self.guiLogQueue.put(self.LOG_PREFIX + "The current scan has had a random number appended to the filename.")
                    randomSuffix = str(random.randint(100000, 900000))
                    filename = os.path.splitext()[0]
                    filename += randomSuffix + ".tif"

                io.imsave(filename,deconvolvedStackMaxProj)

            self.guiLogQueue.put(self.LOG_PREFIX + "Scan deconvolution complete")


        else:

            maxProjections = []

            for stackPath in stackPaths:
                stack = io.imread(stackPath)
                maxProj = np.max(stack, axis=0)
                maxProjections.append(maxProj)

            maxProjStack = np.asarray(maxProjections)
            path = stackPaths[0]

            if scanType == "timelapse":
                path = os.path.dirname(path)
                path = os.path.dirname(path) + "\\"
                tif.imwrite(path + "timelapse_max_proj.tif", maxProjStack, imagej=True)

            elif scanType == "stack":
                print("attempting to run stack")
                print("path=" + path)
                path = os.path.dirname(path) + "\\"
                tif.imwrite(path + "max_proj.tif", maxProjStack, imagej=True)






    def scan_stack(self, scanName, timelapseScanName):

        metadata = self.gen_stack_metadata()
        path = self.gen_scan_directory(scanName)
        # Directory creation failed
        if path == -1:
            return -1


        # Put camera in scan mode
        self.mainQueue.put([1, 3, [timelapseScanName, metadata, path, 0]])
        self.wait_for_confirmation(1)
        # Open shutter
        self.mainQueue.put([2, 7, []])
        # Wait 1 second for shutter to open
        sleep(1)

        for i in range(0, self.STACK_SIZE):

            # Capture frame
            self.mainQueue.put([1, 4, ["CAPTURE"]])
            self.wait_for_confirmation(1)
            # Move motor down z
            self.mainQueue.put([2, 6, [2, self.Z_STEP_SIZE_um, True]])
            self.wait_for_confirmation(2)
            # Wait for motor vibration to settle
            sleep(self.SLEEP_DURATION_AFTER_MOVEMENT_S)

        # Move back to top of stack
        self.mainQueue.put([2, 6, [2, -(self.STACK_SIZE * self.Z_STEP_SIZE_um), True]])
        # Close shutter
        self.mainQueue.put([2, 7, []])
        # Wait for confirmation from arduino that we've returned to top of the stack
        self.wait_for_confirmation(2)
        # Take camera out of scan mode
        self.mainQueue.put([1, 4, ["STOP"]])
        self.guiLogQueue.put(self.LOG_PREFIX + "Stack Scan Complete!")
        return path + "\\" + timelapseScanName + ".tif"

    def scan_timelapse(self):

        timelapsePath = self.gen_scan_directory(self.SCAN_NAME + "_timelapse")
        if timelapsePath == -1:
            return -1

        stackPaths = []

        for i in range(0,self.TIMELAPSE_N):

            start = time()
            # Scan stack
            stackPath = self.scan_stack(self.SCAN_NAME + "_timelapse\\" + self.SCAN_NAME + "_timelapse" + str(i), self.SCAN_NAME + "_timelapse" + str(i))
            if stackPath == -1:
                # Close shutter
                self.mainQueue.put([2, 7, []])
                return -1
            else:
                stackPaths.append(stackPath)

            end = time()
            # How long til' next stack?
            timeUntilNextStackDue = self.TIMELAPSE_INTERVAL_S - (end - start)

            # If scanning 1 stack is taking longer than the requested interval between stacks, let the user know.
            if timeUntilNextStackDue <= 0:
                self.guiLogQueue.put(self.LOG_PREFIX + "WARNING=The time it takes to scan 1 stack is greater than the requested time interval between stacks!")

            # If we're on our last iteration, no need to sleep, just shutdown now.
            elif i == self.TIMELAPSE_N - 1:
                self.guiLogQueue.put(self.LOG_PREFIX + "Timelapse Scan Complete!")
                return stackPaths

            # Otherwise, sleep til' next stack is due.
            else:
                self.guiLogQueue.put(self.LOG_PREFIX + "Time Until Next Stack Scan: " + str(timeUntilNextStackDue) + "s")
                sleep(timeUntilNextStackDue - 1)


    def scan_tiles(self):

        tiledScanPath = self.gen_scan_directory(self.SCAN_NAME + "_tiled")
        if tiledScanPath == -1:
            return -1

        stackPaths = []

        for i in range(0, len(self.TILE_SCAN_TRANSLATIONS[0]) + 2):

            stackPath = self.scan_stack(self.SCAN_NAME + "_tiled\\" + self.SCAN_NAME + "_tiled" + str(i), self.SCAN_NAME + "_tiled" + str(i))

            if stackPath == -1:
                # Close shutter
                self.mainQueue.put([2, 7, []])
                return -1
            else:
                stackPaths.append(stackPath)


            # perform stage translations here
            self.TILE_SCAN_TRANSLATIONS = []


        self.guiLogQueue.put(self.LOG_PREFIX + "Tiled Scan Complete!")
        return stackPaths




    def mainloop(self):
        while True:
            if not self.queue.empty():
                self.process_msg(self.queue.get())


    def process_msg(self, msg):

        funcIndex = msg[1]

        if funcIndex == 0:
            self.scan("stack", msg[2][0])
        elif funcIndex == 1:
            self.set_z_step_size(msg[2][0])
        elif funcIndex == 2:
            self.set_stack_size(msg[2][0])
        elif funcIndex == 3:
            self.set_scan_name(msg[2][0])
        elif funcIndex == 4:
            self.set_scan_step_speed(msg[2][0])
        elif funcIndex == 5:
            self.set_sleep_duration_after_movement(msg[2][0])
        elif funcIndex == 6:
            self.set_sleep_duration_after_capture(msg[2][0])
        elif funcIndex == 7:
            self.scan("timelapse", msg[2][0])
        elif funcIndex == 8:
            self.set_timelapse_n(msg[2][0])
        elif funcIndex == 9:
            self.set_timelapse_interval_s(msg[2][0])
        elif funcIndex == 10:
            self.set_refractive_index_immersion(msg[2][0])
        elif funcIndex == 11:
            self.set_numerical_aperture(msg[2][0])
        elif funcIndex == 12:
            self.set_wavelength(msg[2][0])
        elif funcIndex == 13:
            self.set_nanometers_per_pixel(msg[2][0])
        elif funcIndex == 14:
            self.set_richardson_lucy_iterations(msg[2][0])
        elif funcIndex == 15:
            self.set_deconvolve_after_scan(msg[2][0])
        elif funcIndex == 16:
            self.set_imaging_objective_magnification(msg[2][0])
        elif funcIndex == 17:
            self.scan("tiled", msg[2][0])

def launch_scanner(queue, mainQueue, guiLogQueue):

    scanner = Scanner(queue, mainQueue, guiLogQueue)
    scanner.mainloop()