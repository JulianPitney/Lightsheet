from time import *


class Scanner(object):


    def __init__(self, queue, mainQueue):

        self.queue = queue
        self.mainQueue = mainQueue
        self.Z_STEP_SIZE = 100
        self.STACK_SIZE = 16
        self.SCAN_STEP_SPEED = 50
        self.SCAN_NAME = "default"
        self.SLEEP_DURATION_AFTER_CAPTURE_S = 0.1
        self.SLEEP_DURATION_AFTER_MOVEMENT_S = 0.5

    def set_z_step_size(self, step_size):
        self.Z_STEP_SIZE = int(step_size)
        print("Scanner: Z_STEP_SIZE=" + str(step_size))

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

    def set_sleep_duration_after_capture(self, duration_S):
        self.SLEEP_DURATION_AFTER_CAPTURE_S = int(duration_S)
        print("Scanner: SLEEP_DURATION_AFTER_CAPTURE_S=" + str(duration_S))

    def scan_stack(self):

        start = time()

        # Put camera in scan mode
        self.mainQueue.put([1, 3, [self.SCAN_NAME]])
        sleep(2)

        for i in range(0, self.STACK_SIZE):
            self.mainQueue.put([1, 4, ["CAPTURE"]])
            sleep(self.SLEEP_DURATION_AFTER_CAPTURE_S)
            self.mainQueue.put([2, 3, [2, self.Z_STEP_SIZE]])
            sleep(self.SLEEP_DURATION_AFTER_MOVEMENT_S)

        self.mainQueue.put([1, 4, ["STOP"]])

        end = time()
        print("ELAPSED SCAN TIME: " + str(end - start))


    def mainloop(self):
        while True:
            if not self.queue.empty():
                self.process_msg(self.queue.get())


    def process_msg(self, msg):

        funcIndex = msg[1]

        if funcIndex == 0:
            self.scan_stack()
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

def launch_scanner(queue, mainQueue):

    scanner = Scanner(queue, mainQueue)
    scanner.mainloop()