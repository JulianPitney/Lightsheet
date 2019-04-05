import PySpin
import cv2
import os
from multiprocessing import Process, Queue

class TriggerType:
	SOFTWARE = 1
	HARDWARE = 2
CHOSEN_TRIGGER = TriggerType.HARDWARE


class CameraController(object):


	def __init__(self, queue, EXPOSURE, GAIN):

		self.queue = queue
		self.EXPOSURE = EXPOSURE
		self.GAIN = GAIN
		self.displayPreview = False
		self.previewProcQueue = Queue()
		self.previewProc = None

	def init_spinnaker(self):

		# Make sure we have system write permissions
		try:
			test_file = open('test.txt', 'w+')
		except IOError:
			print('Unable to write to current directory. Please check permissions.')
			input('Press Enter to exit...')
			return False
		test_file.close()
		os.remove(test_file.name)

		# Retrieve singleton reference to system object
		system = PySpin.System.GetInstance()

		# Get current library version
		version = system.GetLibraryVersion()
		print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

		# Retrieve list of cameras from the system
		camList = system.GetCameras()

		num_cameras = camList.GetSize()

		print('Number of cameras detected: %d' % num_cameras)

		# Finish if there are no cameras
		if num_cameras == 0:

			# Clear camera list before releasing system
			camList.Clear()

			# Release system instance
			system.ReleaseInstance()

			print('Not enough cameras!')
			input('Done! Press Enter to exit...')
			return False


		return camList, system


	def deinit_spinnaker(self, camList, system):

		for _,cam in enumerate(camList):
			del cam

		# Clear camera list before releasing system
		camList.Clear()

		# Release system instance
		system.ReleaseInstance()



	def init_camera(self, camera, configureTrigger, acquisitionMode):

		nodemap_tldevice = camera.GetTLDeviceNodeMap()
		camera.Init()
		nodemap = camera.GetNodeMap()

		# In order to access the node entries, they have to be casted to a pointer type (CEnumerationPtr here)
		node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
		if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
			print('Unable to set acquisition mode. Aborting...')
			return False

		node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName(acquisitionMode)
		if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
			print('Unable to set acquisition mode. Aborting...')
			return False

		acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
		node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

		if(configureTrigger):
			configure_trigger(camera)





	def configure_trigger(self, cam):
		"""
		This function configures the camera to use a trigger. First, trigger mode is
		set to off in order to select the trigger source. Once the trigger source
		has been selected, trigger mode is then enabled, which has the camera
		capture only a single image upon the execution of the chosen trigger.

		 :param cam: Camera to configure trigger for.
		 :type cam: CameraPtr
		 :return: True if successful, False otherwise.
		 :rtype: bool
		"""
		result = True

		print('*** CONFIGURING TRIGGER ***\n')

		if CHOSEN_TRIGGER == TriggerType.SOFTWARE:
			print('Software trigger chosen ...')
		elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
			print('Hardware trigger chose ...')

		try:
			# Ensure trigger mode off
			# The trigger must be disabled in order to configure whether the source
			# is software or hardware.
			nodemap = cam.GetNodeMap()
			node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
			if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
				print('Unable to disable trigger mode (node retrieval). Aborting...')
				return False

			node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
			if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
				print('Unable to disable trigger mode (enum entry retrieval). Aborting...')
				# return False

			node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())

			print('Trigger mode disabled...')

			# Select trigger source
			# The trigger source must be set to hardware or software while trigger
			# mode is off.
			node_trigger_source = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerSource'))
			if not PySpin.IsAvailable(node_trigger_source) or not PySpin.IsWritable(node_trigger_source):
				print('Unable to get trigger source (node retrieval). Aborting...')
				return False

			if CHOSEN_TRIGGER == TriggerType.SOFTWARE:
				node_trigger_source_software = node_trigger_source.GetEntryByName('Software')
				if not PySpin.IsAvailable(node_trigger_source_software) or not PySpin.IsReadable(
						node_trigger_source_software):
					print('Unable to set trigger source (enum entry retrieval). Aborting...')
					return False
				node_trigger_source.SetIntValue(node_trigger_source_software.GetValue())

			elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
				node_trigger_source_hardware = node_trigger_source.GetEntryByName('Line0')
				if not PySpin.IsAvailable(node_trigger_source_hardware) or not PySpin.IsReadable(
						node_trigger_source_hardware):
					print('Unable to set trigger source (enum entry retrieval). Aborting...')
					return False
				node_trigger_source.SetIntValue(node_trigger_source_hardware.GetValue())

			# Turn trigger mode on
			# Once the appropriate trigger source has been set, turn trigger mode
			# on in order to retrieve images using the trigger.
			node_trigger_mode_on = node_trigger_mode.GetEntryByName('On')
			if not PySpin.IsAvailable(node_trigger_mode_on) or not PySpin.IsReadable(node_trigger_mode_on):
				print('Unable to enable trigger mode (enum entry retrieval). Aborting...')
				return False

			node_trigger_mode.SetIntValue(node_trigger_mode_on.GetValue())
			print('Trigger mode turned back on...')

		except PySpin.SpinnakerException as ex:
			print('Error: %s' % ex)
			return False

		return result


	def toggle_preview(self):


		self.displayPreview = not self.displayPreview

		if(self.displayPreview):
			print("Starting preview window!")
			p = Process(target=self.display_preview, args=(self.previewProcQueue,))
			p.start()
			self.previewProc = p
		else:
			print("Closing preview window!")
			self.previewProcQueue.put(["False"])
			self.previewProc.join()
			self.previewProc = None




	def display_preview(self, inputQueue):

		keepAlive = "True"
		camList, system = self.init_spinnaker()
		camera = camList.GetByIndex(0)
		self.init_camera(camera, False, 'Continuous')
		cv2.namedWindow('image',cv2.WINDOW_NORMAL)
		cv2.resizeWindow('image',1440,1080)


		# set exposure
		if camera.ExposureAuto.GetAccessMode() != PySpin.RW:
			print('Unable to disable automatic exposure. Aborting...')
			return False
		else:
			camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)

		if camera.ExposureTime.GetAccessMode() != PySpin.RW:
			print('Unable to set exposure time. Aborting...')
			return False
		else:
			# Ensure desired exposure time does not exceed the maximum
			self.EXPOSURE = min(camera.ExposureTime.GetMax(), self.EXPOSURE)
			camera.ExposureTime.SetValue(self.EXPOSURE)

		# set gain
		if camera.GainAuto.GetAccessMode() != PySpin.RW:
			print("Unable to disable automatic gain. Aborting...")
			return False
		else:
			camera.GainAuto.SetValue(PySpin.GainAuto_Off)

		if camera.Gain.GetAccessMode() != PySpin.RW:
			print("Unable to set gain. Aborting...")
			return False
		else:
			self.GAIN
			self.GAIN = min(camera.Gain.GetMax(), self.GAIN)
			camera.Gain.SetValue(self.GAIN)


		camera.BeginAcquisition()
		while(keepAlive == "True"):

			if(not inputQueue.empty()):
				keepAlive = inputQueue.get()

			image_result = camera.GetNextImage()
			if image_result.IsIncomplete():
				print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
			else:
				image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
				cv2.imshow('image', image_converted.GetNDArray())
				cv2.waitKey(1)
				image_result.Release()


		camera.EndAcquisition()
		camera.DeInit()
		del camera
		camList.Clear()
		system.ReleaseInstance()
		return 0


	def set_exposure(self, exposure):
		self.EXPOSURE = int(exposure)

	def set_gain(self, gain):
		self.GAIN = int(gain)

	def process_msg(self, msg):

		functionIndex = msg[1]

		if(functionIndex == 0):
			self.toggle_preview()
		elif(functionIndex == 1):
			self.set_exposure(msg[2][0])
		elif(functionIndex == 2):
			self.set_gain(msg[2][0])



	def mainloop(self):
		while(True):
			if(not self.queue.empty()):
				self.process_msg(self.queue.get())


def launch_camera(queue, EXPOSURE, GAIN):

	cc = CameraController(queue, EXPOSURE, GAIN)
	cc.mainloop()
