import serial




class ArduinoController(object):


	def __init__(self, queue, mainQueue):


		# Process objects
		self.queue = queue
		self.mainQueue = mainQueue
		self.LOG_PREFIX = "ArduinoController: "



		# Motor configuration
		self.SEEK_SPEED = 1600
		self.JOG_MIN_SPEED = 800
		self.JOG_MAX_SPEED = 2000
		self.MICROMETERS_PER_STEP = 0.15625

		# Hardware interface
		SERIAL_PORT_PATH = "COM4"
		BAUDRATE = 115200
		self.serialInterface = self.open_serial_interface(SERIAL_PORT_PATH, BAUDRATE)
		self.wait_for_arduino_confirmation()



	def __del__(self):
		if self.serialInterface != None:
			self.serialInterface.close()


	def open_serial_interface(self, SERIAL_PORT_PATH, BAUDRATE):

		# Try to open serial connection until it works
		while(1):
			serialInterface = serial.Serial(SERIAL_PORT_PATH, BAUDRATE, timeout=3)
			if serialInterface.is_open:
				print(self.LOG_PREFIX + "Serial connection successfully established (" + SERIAL_PORT_PATH + "," + str(BAUDRATE) + ")")
				return serialInterface
			else:
				print(self.LOG_PREFIX + "Failed to open serial connection (" + SERIAL_PORT_PATH + "," + str(BAUDRATE) + ")")


	def wait_for_arduino_confirmation(self):

		# Wait for arduino to say it's ready
		while(1):
			confirmation = self.serialInterface.readline().decode()
			if confirmation == "ARDUINO READY\n":
				print(self.LOG_PREFIX + "Arduino ready!")
				return 0
			else:
				print(self.LOG_PREFIX + "Arduino failed to respond!")


	def convert_um_to_steps(self, um):

		# ensure request is a whole number multiple of <MICROMETERS_PER_STEP>
		if um % self.MICROMETERS_PER_STEP != 0:
			print(self.LOG_PREFIX + " ERROR=Motor can only provide movement in whole number multiples of <MICROMETERS_PER_STEP>!")
			return 0
		else:
			steps = um / self.MICROMETERS_PER_STEP
			return steps

	def map_analog_to_discrete_range(self, value, leftMin, leftMax, rightMin, rightMax):

		leftSpan = leftMax - leftMin
		rightSpan = rightMax - rightMin
		valueScaled = float(value - leftMin) / float(leftSpan)
		return int(rightMin + (valueScaled * rightSpan))

	def toggle_coarse_jog(self):

		command = "TOGGLE_COARSE_JOG\n"
		self.serialInterface.write(command.encode('UTF-8'))
		response = self.serialInterface.readline().decode()
		print(self.LOG_PREFIX + "COMMAND_CONFIRMATION=" + response)

	def toggle_laser(self):

		command = "TOGGLE_LASER\n"
		self.serialInterface.write(command.encode('UTF-8'))
		response = self.serialInterface.readline().decode()
		print(self.LOG_PREFIX + "COMMAND_CONFIRMATION=" + response)

	def toggle_solenoid(self):

		command = "TOGGLE_SHUTTER\n"
		self.serialInterface.write(command.encode('UTF-8'))
		response = self.serialInterface.readline().decode()
		print(self.LOG_PREFIX + "COMMAND_CONFIRMATION=" + response)

	def toggle_led(self):

		command ="TOGGLE_LED\n"
		self.serialInterface.write(command.encode('UTF-8'))
		response = self.serialInterface.readline().decode()
		print(self.LOG_PREFIX + "COMMAND_CONFIRMATION=" + response)


	def set_motor_speed(self, motorIndex, speed):

		speed = int(speed)
		command = "SET S" + str(motorIndex) + " " + "SPEED" + " " + str(speed) + "\n"
		self.serialInterface.write(command.encode('UTF-8'))
		response = self.serialInterface.readline().decode()
		print(self.LOG_PREFIX + "COMMAND_CONFIRMATION=" + response)

	def set_motor_acceleration(self, motorIndex, acceleration):

		acceleration = int(acceleration)
		command = "SET S" + str(motorIndex) + " " + "ACCELERATION" + " " + str(acceleration) + "\n"
		self.serialInterface.write(command.encode('UTF-8'))
		response = self.serialInterface.readline().decode()
		print(self.LOG_PREFIX + "COMMAND_CONFIRMATION=" + response)


	def move_motor_micrometers(self, motorIndex, um, scanMode):

		steps = self.convert_um_to_steps(um)
		if(steps == 0):
			return 0
		else:
			self.move_motor_steps(motorIndex, steps, scanMode)

	def move_motor_steps(self, motorIndex, steps, scanMode):

		command = "MOVE S" + str(motorIndex) + " " + str(steps) + " " + str(self.SEEK_SPEED) + "\n"
		self.serialInterface.write(command.encode('UTF-8'))
		response = self.serialInterface.readline().decode()
		#print(self.LOG_PREFIX + "COMMAND_CONFIRMATION=" + response)

		if scanMode:
			self.mainQueue.put([5, -1, [2]])


	def jog_motor(self, motorInputs):

		speeds = []

		for motorInput in motorInputs:

			if motorInput > 0.3:
				speed = self.map_analog_to_discrete_range(motorInput, 0.3, 1, self.JOG_MIN_SPEED, self.JOG_MAX_SPEED)
			elif motorInput < -0.3:
				speed = self.map_analog_to_discrete_range(motorInput, -0.3, -1, -self.JOG_MIN_SPEED, -self.JOG_MAX_SPEED)
			else:
				speed = 0

			speeds.append(speed)

		command = "JOG " + str(speeds[0]) + " " + str(speeds[1]) + " " + str(speeds[2]) + "\n"
		self.serialInterface.write(command.encode('UTF-8'))
		#response = self.serialInterface.readline().decode()
		#print(self.LOG_PREFIX + "COMMAND_CONFIRMATION=" + response)


	def process_msg(self, msg):

		funcIndex = msg[1]

		if funcIndex == 0:
			self.toggle_laser()
		elif funcIndex == 1:
			self.set_motor_speed(msg[2][0], msg[2][1])
		elif funcIndex == 2:
			self.set_motor_acceleration(msg[2][0], msg[2][1])
		elif funcIndex == 3:
			self.move_motor_steps(msg[2][0], msg[2][1], msg[2][2])
		elif funcIndex == 4:
			self.jog_motor(msg[2])
		elif funcIndex == 5:
			self.toggle_coarse_jog()
		elif funcIndex == 6:
			self.move_motor_micrometers(msg[2][0], msg[2][1], msg[2][2])
		elif funcIndex == 7:
			self.toggle_solenoid()
		elif funcIndex == 8:
			self.toggle_led()

	def mainloop(self):
		while True :
			if not self.queue.empty():
				self.process_msg(self.queue.get())


def launch_arduino_controller(queue, mainQueue):

	ac = ArduinoController(queue, mainQueue)
	print("Arduino Process: Initialization complete")
	ac.mainloop()
