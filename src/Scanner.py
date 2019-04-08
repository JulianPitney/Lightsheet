from time import sleep


class Scanner(object):


    def __init__(self, queue):

        self.queue = queue
        self.Z_STEP_SIZE = 10
        self.STACK_SIZE = 10
        self.SCAN_STEP_SPEED = 50
        self.SCAN_NAME = "default"
        self.SLEEP_DURATION_AFTER_CAPTURE_S = 0.5
        self.SLEEP_DURATION_AFTER_MOVEMENT_S = 0.5

    def set_z_step_size(self, step_size):
        self.Z_STEP_SIZE = step_size

    def set_stack_size(self, stack_size):
        self.STACK_SIZE = stack_size

    def set_scan_step_speed(self, step_speed):
        self.SCAN_STEP_SPEED = step_speed

    def set_scan_name(self, scan_name):
        self.SCAN_NAME = scan_name

    def set_sleep_duration_after_movement(self, duration_S):
        self.SLEEP_DURATION_AFTER_MOVEMENT_S = duration_S

    def set_sleep_duration_after_capture(self, duration_S):
        self.SLEEP_DURATION_AFTER_CAPTURE_S = duration_S

    def scan_stack(self):

        # Put camera in scan mode
        self.queue.put([1, 3, [self.SCAN_NAME]])
        sleep(5)


        for i in range(0, self.STACK_SIZE):
            self.queue.put([1, 4, ["CAPTURE"]])
            sleep(self.SLEEP_DURATION_AFTER_CAPTURE_S)
            self.queue.put([2, 3, [2, self.Z_STEP_SIZE]])
            sleep(self.SLEEP_DURATION_AFTER_MOVEMENT_S)

        self.queue.put([1, 4, ["STOP"]])
        #TODO: The process will put the message into it's own queue, then immediately when
        # the function exits, mainloop -> process_msg will read the message back out of it's queue....the
        # sleep function here gives the main process a chance to read the message first (and route it appropriately
        # to the camera process. I didn't know about this behavior with interprocess queues.....find a less hacky
        # solution to this.....NOTE: This might explain the deadlock between main and ps4Proc...investigate...
        sleep(3)


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

def launch_scanner(queue):

    scanner = Scanner(queue)
    scanner.mainloop()