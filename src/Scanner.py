from time import *


class Scanner(object):


    def __init__(self, queue, mainQueue):

        self.queue = queue
        self.mainQueue = mainQueue
        self.Z_STEP_SIZE_um = 0.15625
        self.STACK_SIZE = 10
        self.SCAN_STEP_SPEED = 50
        self.SCAN_NAME = "default"
        self.SLEEP_DURATION_AFTER_MOVEMENT_S = 0.5
        self.TIMELAPSE_N = 20
        self.TIMELAPSE_INTERVAL_S = 30

    def set_z_step_size(self, step_size_um):
        self.Z_STEP_SIZE_um = float(step_size_um)
        print("Scanner: Z_STEP_SIZE=" + str(step_size_um))

    def set_stack_size(self, stack_size):
        self.STACK_SIZE = int(stack_size)
        print("Scanner: STACK_SIZE=" + str(stack_size))

    def set_scan_step_speed(self, step_speed):
        self.SCAN_STEP_SPEED = int(step_speed)
        print("Scanner: SCAN_STEP_SPEED=" + str(step_speed))

    def set_scan_name(self, scan_name):
        self.SCAN_NAME = str(scan_name)
        print("Scanner: SCAN_NAME=" + str(scan_name))

    def set_sleep_duration_after_movement(self, duration_S):
        self.SLEEP_DURATION_AFTER_MOVEMENT_S = int(duration_S)
        print("Scanner: SLEEP_DURATION_AFTER_MOVEMENT_S=" + str(duration_S))



    def wait_for_confirmation(self, procIndex):

        while True:
            if not self.queue.empty():
                msg = self.queue.get()
                if msg[2][0] == procIndex:
                    break
                else:
                    pass


    def scan_stack(self, scanName):

        # Put camera in scan mode
        self.mainQueue.put([1, 3, [scanName]])
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
        print("Stack Scan Complete!")


    def scan_timelapse(self):



        for i in range(0,self.TIMELAPSE_N):

            start = time()
            # Turn laser on
            self.mainQueue.put([2, 0, []])
            # Wait 1 second for laser to power up
            sleep(1)
            # Scan stack
            self.scan_stack(self.SCAN_NAME + "_timelapse" + str(i))
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
                print("WARNING: " + "The time it takes to scan 1 stack is greater than the requested time interval between stacks!")

            # If we're on our last iteration, no need to sleep, just shutdown now.
            elif i == self.TIMELAPSE_N - 1:
                print("Timelapse Scan Complete!")
                break

            # Otherwise, sleep til' next stack is due.
            else:
                print("Time Until Next Stack Scan: " + str(timeUntilNextStackDue) + "s")
                sleep(timeUntilNextStackDue - 1)



    def mainloop(self):
        while True:
            if not self.queue.empty():
                self.process_msg(self.queue.get())


    def process_msg(self, msg):

        funcIndex = msg[1]

        if funcIndex == 0:
            self.scan_stack(self.SCAN_NAME)
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
            self.scan_timelapse()

def launch_scanner(queue, mainQueue):

    scanner = Scanner(queue, mainQueue)
    scanner.mainloop()