import serial




class ArduinoController(object):





	def __init__(self, SERIAL_PORT_PATH, BAUDRATE):

		self.COARSE_JOG = False
		self.SERIAL_PORT_PATH = SERIAL_PORT_PATH
		self.BAUDRATE = BAUDRATE
		self.serialInterface = serial.Serial(SERIAL_PORT_PATH, BAUDRATE)
		# Wait for Arduino server to say it's ready
		confirmation = self.serialInterface.readline().decode()
		print(confirmation)


	def __del__(self):

		self.serialInterface.__del__()

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


	def move_motor(self, motorIndex, steps):

		if(self.COARSE_JOG):

			command = "MOVE S" + str(motorIndex) + " " + str(steps * 10) + "\n"
			self.serialInterface.write(command.encode('UTF-8'))
			print("wrote:",command)
			response = self.serialInterface.readline().decode()
			print(response)
		else:
			command = "MOVE S" + str(motorIndex) + " " + str(steps) + "\n"
			self.serialInterface.write(command.encode('UTF-8'))
			print("wrote:",command)
			response = self.serialInterface.readline().decode()
			print(response)
