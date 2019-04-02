import serial




class ArduinoController(object):


	def __init__(self, queue, SERIAL_PORT_PATH, BAUDRATE):

		self.COARSE_JOG = False
		self.JOG_INCREMENT = 15
		self.SEEK_SPEED = 1600
		self.SERIAL_PORT_PATH = SERIAL_PORT_PATH
		self.BAUDRATE = BAUDRATE
		self.serialInterface = None #serial.Serial(SERIAL_PORT_PATH, BAUDRATE)
		self.queue = queue
		# Wait for Arduino server to say it's ready
		#confirmation = self.serialInterface.readline().decode()
		#print(confirmation)


	def __del__(self):
		print("destroying arduino proc")
		#self.serialInterface.__del__()

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

		command = "MOVE S" + str(motorIndex) + " " + str(steps) + " " + str(self.SEEK_SPEED) + "\n"
		self.serialInterface.write(command.encode('UTF-8'))
		print("wrote:",command)
		response = self.serialInterface.readline().decode()
		print(response)


	def jog_motor(self, motorIndex, speed, dir):

		steps = self.JOG_INCREMENT
		if(dir):
			pass
		else:
			steps *= -1

		command = "MOVE S" + str(motorIndex) + " " + str(steps) + " " + str(speed) + "\n"
		self.serialInterface.write(command.encode('UTF-8'))
		#response = self.serialInterface.readline().decode()



	def process_msg(self, msg):

		funcIndex = msg[1]

		if funcIndex == 0:
			self.toggle_laser()
		elif funcIndex == 1:
			self.set_motor_speed(msg[2][0], msg[2][1])
		elif funcIndex == 2:
			self.set_motor_acceleration(msg[2][0], msg[2][1])
		elif funcIndex == 3:
			self.move_motor(msg[2][0], msg[2][1])
		elif funcIndex == 4:
			print("arduino process launching jog")
			#self.jog_motor(msg[2][0], msg[2][1], msg[2][2])


	def mainloop(self):
		while True :
			if not self.queue.empty():
				self.process_msg(self.queue.get())


def launch_arduino_controller(queue, SERIAL_PORT_PATH, BAUDRATE):

	ac = ArduinoController(queue, SERIAL_PORT_PATH, BAUDRATE)
	ac.mainloop()
