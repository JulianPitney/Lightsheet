from time import *
from Deconvolver import *
import os
import os.path

class Scanner(object):


    def __init__(self, queue, mainQueue):


        self.queue = queue
        self.mainQueue = mainQueue
        self.LOG_PREFIX = "Scanner: "


        self.Z_STEP_SIZE_um = 0.15625
        self.STACK_SIZE = 10
        self.SCAN_STEP_SPEED = 50
        self.SCAN_NAME = "default"
        self.SLEEP_DURATION_AFTER_MOVEMENT_S = 0.5
        self.TIMELAPSE_N = 1
        self.TIMELAPSE_INTERVAL_S = 10

        # Deconvolution parameters
        self.deconvolver = Deconvolver()
        self.deconvolveAfterScan = True
        self.refractiveIndexImmersion = 1.33
        self.numericalAperture = 0.5
        self.wavelength = 530
        self.nanometersPerPixel = 180
        self.sizeX = 1440
        self.sizeY = 1080
        self.richardsonLucyIterations = 2


    def set_z_step_size(self, step_size_um):
        self.Z_STEP_SIZE_um = float(step_size_um)
        print(self.LOG_PREFIX + "Z_STEP_SIZE=" + str(step_size_um))

    def set_stack_size(self, stack_size):
        self.STACK_SIZE = int(stack_size)
        print(self.LOG_PREFIX + "STACK_SIZE=" + str(stack_size))

    def set_scan_step_speed(self, step_speed):
        self.SCAN_STEP_SPEED = int(step_speed)
        print(self.LOG_PREFIX + "SCAN_STEP_SPEED=" + str(step_speed))

    def set_scan_name(self, scan_name):
        self.SCAN_NAME = str(scan_name)
        print(self.LOG_PREFIX + "SCAN_NAME=" + str(scan_name))

    def set_sleep_duration_after_movement(self, duration_S):
        self.SLEEP_DURATION_AFTER_MOVEMENT_S = int(duration_S)
        print(self.LOG_PREFIX + "SLEEP_DURATION_AFTER_MOVEMENT_S=" + str(duration_S))

    def set_timelapse_n(self, timelapseN):
        self.TIMELAPSE_N = int(timelapseN)
        print(self.LOG_PREFIX + "TIMELAPSE_N=" + str(timelapseN))

    def set_timelapse_interval_s(self, timelapseInterval):
        self.TIMELAPSE_INTERVAL_S = int(timelapseInterval)
        print(self.LOG_PREFIX + "TIMELAPSE_INTERVAL_S=" + str(timelapseInterval))

    def set_refractive_index_immersion(self, refractiveIndexImmersion):
        self.refractiveIndexImmersion = refractiveIndexImmersion
        print(self.LOG_PREFIX + "REFRACTIVE_INDEX_IMMERSION=" + str(refractiveIndexImmersion))

    def set_numerical_aperture(self, numericalAperture):
        self.numericalAperture = numericalAperture
        print(self.LOG_PREFIX + "NUMERICAL_APERTURE=" + str(numericalAperture))

    def set_wavelength(self, wavelength):
        self.wavelength = wavelength
        print(self.LOG_PREFIX + "WAVELENGTH=" + str(wavelength))

    def set_nanometers_per_pixel(self, nanometersPerPixel):
        self.nanometersPerPixel = nanometersPerPixel
        print(self.LOG_PREFIX + "NANOMETERS_PER_PIXEL=" + str(nanometersPerPixel))

    def set_richardson_lucy_iterations(self, iterations):
        self.richardsonLucyIterations = iterations
        print(self.LOG_PREFIX + "RICHARDSON_LUCY_ITERATIONS=" + str(iterations))

    def set_deconvolve_after_scan(self, deconvolveAfterScan):
        self.deconvolveAfterScan = deconvolveAfterScan
        print(self.LOG_PREFIX + "DECONVOLVE_AFTER_SCAN=" + str(deconvolveAfterScan))



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
            print(self.LOG_PREFIX + "Creation of the directory %s failed" % path)
        else:
            print(self.LOG_PREFIX + "Successfully created the directory %s " % path)
            return path


    def gen_stack_metadata(self):

        # Generate stack metadata
        metadata = []
        metadata.append(['z_step-size', self.Z_STEP_SIZE_um])
        metadata.append(['units', 'um'])
        metadata.append(['stack_size', self.STACK_SIZE])
        metadata.append(['motor_step_speed', self.SCAN_STEP_SPEED])
        metadata.append(['vibration_settle_delay', self.SLEEP_DURATION_AFTER_MOVEMENT_S])
        return metadata


    def scan(self, scanType):

        stackPaths = []

        if scanType == "stack":
            stackPaths.append(self.scan_stack(self.SCAN_NAME, self.SCAN_NAME))

        elif scanType == "timelapse":
            stackPaths = self.scan_timelapse()

        # deconvolve scan if selected
        if self.deconvolveAfterScan:
            print(self.LOG_PREFIX + "Scan deconvolution starting...")
            # generate psf for this scan
            path = stackPaths[0]
            path = os.path.dirname(path)
            path = os.path.dirname(path) + "\\"

            psfPath = self.deconvolver.gen_psf_PSFGenerator(self.refractiveIndexImmersion, self.wavelength, self.numericalAperture, self.nanometersPerPixel, self.Z_STEP_SIZE_um, self.sizeX, self.sizeY, self.STACK_SIZE, path)
            deconvolvedStackPaths = []
            for stackPath in stackPaths:
                outputPath = os.path.dirname(stackPath) +"\\"
                deconvolvedStackPaths.append(self.deconvolver.deconvolve_DeconvLab2(stackPath, psfPath, self.richardsonLucyIterations, outputPath))



    def scan_stack(self, scanName, timelapseScanName):

        metadata = self.gen_stack_metadata()
        path = self.gen_scan_directory(scanName)
        # Put camera in scan mode
        self.mainQueue.put([1, 3, [timelapseScanName, metadata, path]])
        self.wait_for_confirmation(1)

        for i in range(0, self.STACK_SIZE):

            # Capture frame
            self.mainQueue.put([1, 4, ["CAPTURE"]])
            self.wait_for_confirmation(1)
            # Move motor down z
            self.mainQueue.put([2, 6, [2, self.Z_STEP_SIZE_um, True]])
            self.wait_for_confirmation(2)
            # Wait for motor vibration to settle
            sleep(self.SLEEP_DURATION_AFTER_MOVEMENT_S)

        # Take camera out of scan mode
        self.mainQueue.put([1, 4, ["STOP"]])
        print(self.LOG_PREFIX + "Stack Scan Complete!")
        return path + "\\" + timelapseScanName + ".tif"

    def scan_timelapse(self):

        self.gen_scan_directory(self.SCAN_NAME + "_timelapse")
        stackPaths = []

        for i in range(0,self.TIMELAPSE_N):

            start = time()
            # Turn laser on
            self.mainQueue.put([2, 0, []])
            # Wait 1 second for laser to power up
            sleep(1)
            # Scan stack
            stackPaths.append(self.scan_stack(self.SCAN_NAME + "_timelapse\\" + self.SCAN_NAME + "_timelapse" + str(i), self.SCAN_NAME + "_timelapse" + str(i)))
            # Turn laser off
            self.mainQueue.put([2, 0, []])
            # Move back to top of stack
            self.mainQueue.put([2, 6, [2, -(self.STACK_SIZE * self.Z_STEP_SIZE_um), True]])
            # Wait for confirmation from arduino that we've returned to top of the stack
            self.wait_for_confirmation(2)
            end = time()

            # How long til' next stack?
            timeUntilNextStackDue = self.TIMELAPSE_INTERVAL_S - (end - start)

            # If scanning 1 stack is taking longer than the requested interval between stacks, let the user know.
            if timeUntilNextStackDue <= 0:
                print(self.LOG_PREFIX + "WARNING=The time it takes to scan 1 stack is greater than the requested time interval between stacks!")

            # If we're on our last iteration, no need to sleep, just shutdown now.
            elif i == self.TIMELAPSE_N - 1:
                print(self.LOG_PREFIX + "Timelapse Scan Complete!")
                return stackPaths
                break

            # Otherwise, sleep til' next stack is due.
            else:
                print(self.LOG_PREFIX + "Time Until Next Stack Scan: " + str(timeUntilNextStackDue) + "s")
                sleep(timeUntilNextStackDue - 1)



    def mainloop(self):
        while True:
            if not self.queue.empty():
                self.process_msg(self.queue.get())


    def process_msg(self, msg):

        funcIndex = msg[1]

        if funcIndex == 0:
            self.scan("stack")
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
            self.scan("timelapse")
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


def launch_scanner(queue, mainQueue):

    scanner = Scanner(queue, mainQueue)
    scanner.mainloop()