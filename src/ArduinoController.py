import serial


class ArduinoController(object):


	def __init__(self, queue, mainQueue):

		self.COARSE_JOG = False
		self.SEEK_SPEED = 1600
		self.JOG_INCREMENT = 5
		self.JOG_MIN_SPEED = 1000
		self.JOG_MAX_SPEED = 1500
		self.MICROMETERS_PER_STEP = 0.15625
		self.SERIAL_PORT_PATH = "COM4"
		self.BAUDRATE = 57600
		self.serialInterface = serial.Serial(self.SERIAL_PORT_PATH, self.BAUDRATE)
		self.queue = queue
		self.mainQueue = mainQueue
		# Wait for Arduino server to say it's ready
		confirmation = self.serialInterface.readline().decode()
		print(confirmation)


	def __del__(self):
		print("destroying arduino proc")
		self.serialInterface.__del__()


	def convert_um_to_steps(self, um):

		# ensure request is a whole number multiple of <MICROMETERS_PER_STEP>
		if um % self.MICROMETERS_PER_STEP != 0:
			print("ERROR: Motor can only provide movement in whole number multiples of <MICROMETERS_PER_STEP>!")
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

		if(self.JOG_INCREMENT == 5):
			self.JOG_INCREMENT = 20
			print("COARSE JOG=ON")
		else:
			self.JOG_INCREMENT = 5
			print("COARSE JOG=OFF")

	def toggle_laser(self):

		command = "TOGGLE_LASER\n"
		self.serialInterface.write(command.encode('UTF-8'))
		print("wrote:",command)
		response = self.serialInterface.readline().decode()
		print(response)

	def set_motor_speed(self, motorIndex, speed):

		speed = int(speed)
		command = "SET S" + str(motorIndex) + " " + "SPEED" + " " + str(speed) + "\n"
		self.serialInterface.write(command.encode('UTF-8'))
		print("wrote:",command)
		response = self.serialInterface.readline().decode()
		print(response)

	def set_motor_acceleration(self, motorIndex, acceleration):

		acceleration = int(acceleration)
		command = "SET S" + str(motorIndex) + " " + "ACCELERATION" + " " + str(acceleration) + "\n"
		self.serialInterface.write(command.encode('UTF-8'))
		print("wrote:",command)
		response = self.serialInterface.readline().decode()
		print(response)


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

		if scanMode:
			self.mainQueue.put([5, -1, [2]])

	def jog_motor(self, motorIndex, speed, dir):

		steps = self.JOG_INCREMENT
		if(dir):
			speed = self.map_analog_to_discrete_range(speed, 0.1, 1, self.JOG_MIN_SPEED, self.JOG_MAX_SPEED)
			steps *= -1
		else:
			speed = self.map_analog_to_discrete_range(speed, -0.1, -1, self.JOG_MIN_SPEED, self.JOG_MAX_SPEED)

		command = "MOVE S" + str(motorIndex) + " " + str(steps) + " " + str(speed) + "\n"
		self.serialInterface.write(command.encode('UTF-8'))
		response = self.serialInterface.readline().decode()
		print(response)



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
			self.jog_motor(msg[2][0], msg[2][1], msg[2][2])
		elif funcIndex == 5:
			self.toggle_coarse_jog()
		elif funcIndex == 6:
			self.move_motor_micrometers(msg[2][0], msg[2][1], msg[2][2])

	def mainloop(self):
		while True :
			if not self.queue.empty():
				self.process_msg(self.queue.get())


def launch_arduino_controller(queue, mainQueue):

	ac = ArduinoController(queue, mainQueue)
	ac.mainloop()
