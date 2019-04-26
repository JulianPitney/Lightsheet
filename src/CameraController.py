import PySpin
import cv2
from multiprocessing import Process, Queue
import tifffile as tif
import numpy as np
import time


class TriggerType:
	SOFTWARE = 1
	HARDWARE = 2
CHOSEN_TRIGGER = TriggerType.SOFTWARE


class CameraController(object):


	def __init__(self, queue, mainQueue):

		# Process objects
		self.queue = queue
		self.mainQueue = mainQueue
		self.LOG_PREFIX = "CameraController: "

		# Preview window subprocess objects
		self.displayPreview = False
		self.previewProcQueue = Queue()
		self.previewProc = None

		# Acquisition config
		self.EXPOSURE = 30000
		self.GAIN = 23
		self.FPS = 60.00
		self.WIDTH = 1440
		self.HEIGHT = 1080

		self.test_camera_initialization()


	def test_camera_initialization(self):

		camList, system = self.init_spinnaker()
		camera = camList.GetByIndex(0)
		self.init_camera(camera, configureTrigger=True, acquisitionMode="Continuous")
		nodemap = camera.GetNodeMap()
		self.set_camera_pixel_format(nodemap)
		self.set_camera_exposure(camera)
		self.set_camera_gain(camera)
		camera.BeginAcquisition()


		camera.EndAcquisition()
		self.reset_trigger(nodemap)
		camera.DeInit()
		del camera
		camList.Clear()
		system.ReleaseInstance()


	def init_spinnaker(self):

		system = PySpin.System.GetInstance()
		camList = system.GetCameras()

		if camList.GetSize() == 0:
			camList.Clear()
			system.ReleaseInstance()
			print(self.LOG_PREFIX + "No cameras were found")
			return None, None
		else:
			print(self.LOG_PREFIX + str(camList.GetSize()) + " cameras detected")
			return camList, system




	def init_camera(self, camera, configureTrigger, acquisitionMode):

		camera.Init()
		nodemap = camera.GetNodeMap()

		# In order to access the node entries, they have to be casted to a pointer type (CEnumerationPtr here)
		node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
		if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
			print(self.LOG_PREFIX + "Unable to access acquisition mode of camera")

		node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName(acquisitionMode)
		if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
			print(self.LOG_PREFIX + "Unable to set acquisition mode of camera")

		acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
		node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

		if configureTrigger:
			self.configure_trigger(camera)







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

		#print('*** CONFIGURING TRIGGER ***\n')

		if CHOSEN_TRIGGER == TriggerType.SOFTWARE:
			pass
		elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
			pass

		try:
			# Ensure trigger mode off
			# The trigger must be disabled in order to configure whether the source
			# is software or hardware.
			nodemap = cam.GetNodeMap()
			node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
			if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
				print(self.LOG_PREFIX + 'Unable to access camera trigger mode')
				return False

			node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
			if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
				print(self.LOG_PREFIX + 'Unable to disable camera trigger mode')
				# return False

			node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())

			# Select trigger source
			# The trigger source must be set to hardware or software while trigger
			# mode is off.
			node_trigger_source = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerSource'))
			if not PySpin.IsAvailable(node_trigger_source) or not PySpin.IsWritable(node_trigger_source):
				print(self.LOG_PREFIX + 'Unable to access camera trigger source')
				return False

			if CHOSEN_TRIGGER == TriggerType.SOFTWARE:
				node_trigger_source_software = node_trigger_source.GetEntryByName('Software')
				if not PySpin.IsAvailable(node_trigger_source_software) or not PySpin.IsReadable(
						node_trigger_source_software):
					print(self.LOG_PREFIX + 'Unable to set camera trigger source')
					return False
				node_trigger_source.SetIntValue(node_trigger_source_software.GetValue())

			elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
				node_trigger_source_hardware = node_trigger_source.GetEntryByName('Line0')
				if not PySpin.IsAvailable(node_trigger_source_hardware) or not PySpin.IsReadable(
						node_trigger_source_hardware):
					print(self.LOG_PREFIX + 'Unable to set camera trigger source')
					return False
				node_trigger_source.SetIntValue(node_trigger_source_hardware.GetValue())

			# Turn trigger mode on
			# Once the appropriate trigger source has been set, turn trigger mode
			# on in order to retrieve images using the trigger.
			node_trigger_mode_on = node_trigger_mode.GetEntryByName('On')
			if not PySpin.IsAvailable(node_trigger_mode_on) or not PySpin.IsReadable(node_trigger_mode_on):
				print(self.LOG_PREFIX + 'Unable to enable camera trigger mode')
				return False

			node_trigger_mode.SetIntValue(node_trigger_mode_on.GetValue())

		except PySpin.SpinnakerException as ex:
			print(self.LOG_PREFIX + 'Error=%s' % ex)
			return False

		return result



	def reset_trigger(self, nodemap):


		try:
			result = True
			node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
			if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
				print(self.LOG_PREFIX + 'Unable to disable camera trigger mode')
				return False

			node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
			if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
				print(self.LOG_PREFIX + 'Unable to disable camera trigger mode')
				return False

			node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())

		except PySpin.SpinnakerException as ex:
			print(self.LOG_PREFIX + 'Error=%s' % ex)
			result = False

		return result




	def grab_next_image_by_trigger(self, nodemap, cam):

		try:
			result = True

			if CHOSEN_TRIGGER == TriggerType.SOFTWARE:

				# Execute software trigger
				node_softwaretrigger_cmd = PySpin.CCommandPtr(nodemap.GetNode('TriggerSoftware'))
				if not PySpin.IsAvailable(node_softwaretrigger_cmd) or not PySpin.IsWritable(node_softwaretrigger_cmd):
					print(self.LOG_PREFIX + 'Unable to execute camera trigger')
					return False

				node_softwaretrigger_cmd.Execute()


			elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
				print(self.LOG_PREFIX + 'Camera hardware trigger selected')

		except PySpin.SpinnakerException as ex:
			print(self.LOG_PREFIX + 'Error=%s' % ex)
			return False

		return result






	def toggle_preview(self):


		self.displayPreview = not self.displayPreview

		if(self.displayPreview):
			print(self.LOG_PREFIX + "Starting preview window")
			while not self.previewProcQueue.empty():
				self.previewProcQueue.get()
			p = Process(target=self.display_preview, args=(self.previewProcQueue,))
			p.start()
			self.previewProc = p
		else:
			print(self.LOG_PREFIX + "Closing preview window")
			self.previewProcQueue.put([-1, -1, ["False"]])
			self.previewProc.join()
			self.previewProc = None



	# TODO: This desperately needs refactoring
	def display_preview(self, inputQueue):

		keepAlive = "True"
		camList, system = self.init_spinnaker()
		camera = camList.GetByIndex(0)
		self.init_camera(camera, False, 'Continuous')
		nodemap = camera.GetNodeMap()

		# Boolean node
		enableAcquisitionFrameRateNode = PySpin.CBooleanPtr(nodemap.GetNode("AcquisitionFrameRateEnable"))
		if enableAcquisitionFrameRateNode.GetAccessMode() != PySpin.RW:
			print(self.LOG_PREFIX + "Unable to enable camera acquistion frame rate control")
		else:
			enableAcquisitionFrameRateNode.SetValue(True)

		frameRateNode = PySpin.CFloatPtr(nodemap.GetNode("AcquisitionFrameRate"))
		if frameRateNode.GetAccessMode() != PySpin.RW:
			print(self.LOG_PREFIX + "Unable to set camera acquisition frame rate")
		else:
			frameRateNode.SetValue(self.FPS)


		cv2.namedWindow('image',cv2.WINDOW_NORMAL)
		cv2.resizeWindow('image',640,480)


		# set exposure
		if camera.ExposureAuto.GetAccessMode() != PySpin.RW:
			print(self.LOG_PREFIX + 'Unable to disable camera automatic exposure')
			return False
		else:
			camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)

		if camera.ExposureTime.GetAccessMode() != PySpin.RW:
			print(self.LOG_PREFIX + 'Unable to set camera exposure')
			return False
		else:
			# Ensure desired exposure time does not exceed the maximum
			self.EXPOSURE = min(camera.ExposureTime.GetMax(), self.EXPOSURE)
			camera.ExposureTime.SetValue(self.EXPOSURE)

		# set gain
		if camera.GainAuto.GetAccessMode() != PySpin.RW:
			print(self.LOG_PREFIX + "Unable to disable camera automatic gain")
			return False
		else:
			camera.GainAuto.SetValue(PySpin.GainAuto_Off)

		if camera.Gain.GetAccessMode() != PySpin.RW:
			print(self.LOG_PREFIX + "Unable to set camera gain")
			return False
		else:
			self.GAIN
			self.GAIN = min(camera.Gain.GetMax(), self.GAIN)
			camera.Gain.SetValue(self.GAIN)


		fpsCounter = 0
		start = time.time()


		camera.BeginAcquisition()
		while(keepAlive == "True"):



			if(not inputQueue.empty()):
				msg = inputQueue.get()

				if msg[2][0] == "False":
					break
				elif msg[2][0] == "EXPOSURE":
					self.EXPOSURE = int(msg[2][1])

					if camera.ExposureTime.GetAccessMode() != PySpin.RW:
						print(self.LOG_PREFIX + 'Unable to set camera exposure')
						return False
					else:
						# Ensure desired exposure time does not exceed the maximum
						self.EXPOSURE = min(camera.ExposureTime.GetMax(), self.EXPOSURE)
						camera.ExposureTime.SetValue(self.EXPOSURE)

						# Update FPS too.
						enableAcquisitionFrameRateNode = PySpin.CBooleanPtr(
							nodemap.GetNode("AcquisitionFrameRateEnable"))
						if enableAcquisitionFrameRateNode.GetAccessMode() != PySpin.RW:
							print(self.LOG_PREFIX + "Unable to enable camera acquistion frame rate control")
						else:
							enableAcquisitionFrameRateNode.SetValue(True)

						frameRateNode = PySpin.CFloatPtr(nodemap.GetNode("AcquisitionFrameRate"))
						if frameRateNode.GetAccessMode() != PySpin.RW:
							print(self.LOG_PREFIX + "Unable to set camera acquisition frame rate")
						else:
							frameRateNode.SetValue(self.FPS)


				elif msg[2][0] == "GAIN":
					self.GAIN = int(msg[2][1])

					if camera.Gain.GetAccessMode() != PySpin.RW:
						print(self.LOG_PREFIX + "Unable to set camera gain")
						return False
					else:
						self.GAIN
						self.GAIN = min(camera.Gain.GetMax(), self.GAIN)
						camera.Gain.SetValue(self.GAIN)

			image_result = camera.GetNextImage()
			if image_result.IsIncomplete():
				print(self.LOG_PREFIX + "Camera image incomplete with image status=%d" % image_result.GetImageStatus())
			else:
				image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
				cvMatOriginalFrame = image_converted.GetNDArray()
				cvMatPaintedFrame = cvMatOriginalFrame.copy()
				#TODO: Replace the rectanlge bounds with Rayleigh bounding box once we have that info
				cv2.rectangle(cvMatPaintedFrame,(520,340),(920,740),150,3)
				cv2.addWeighted(cvMatPaintedFrame, 0.1, cvMatOriginalFrame, 1, 0, cvMatOriginalFrame)
				cv2.imshow('image', cvMatOriginalFrame)
				cv2.waitKey(1)
				image_result.Release()
				fpsCounter += 1

			if ((time.time() - start) >= 1):
				fpsCounter = 0
				start = time.time()

		camera.EndAcquisition()
		camera.DeInit()
		del camera
		camList.Clear()
		system.ReleaseInstance()
		return 0




	def set_exposure(self, exposure):
		self.EXPOSURE = int(exposure)
		self.previewProcQueue.put([-1, -1, ["EXPOSURE",self.EXPOSURE]])
		print(self.LOG_PREFIX + "EXPOSURE=" + str(self.EXPOSURE) + "us")

	def set_gain(self, gain):
		self.GAIN = int(gain)
		self.previewProcQueue.put([-1, -1, ["GAIN",self.GAIN]])
		print(self.LOG_PREFIX + "GAIN=" + str(self.GAIN) + "dB")


	def set_camera_gain(self, camera):

		if camera.GainAuto.GetAccessMode() != PySpin.RW:
			print(self.LOG_PREFIX + "Unable to disable camera automatic gain")
			return False
		else:
			camera.GainAuto.SetValue(PySpin.GainAuto_Off)

		if camera.Gain.GetAccessMode() != PySpin.RW:
			print(self.LOG_PREFIX + "Unable to set camera gain")
			return False
		else:
			self.GAIN = min(camera.Gain.GetMax(), self.GAIN)
			camera.Gain.SetValue(self.GAIN)


	def set_camera_exposure(self, camera):

		if camera.ExposureAuto.GetAccessMode() != PySpin.RW:
			print(self.LOG_PREFIX + 'Unable to disable camera automatic exposure')
			return False
		else:
			camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)

		if camera.ExposureTime.GetAccessMode() != PySpin.RW:
			print(self.LOG_PREFIX + 'Unable to set camera exposure')
			return False
		else:
			# Ensure desired exposure time does not exceed the maximum
			self.EXPOSURE = min(camera.ExposureTime.GetMax(), self.EXPOSURE)
			camera.ExposureTime.SetValue(self.EXPOSURE)




	def set_camera_pixel_format(self, nodemap):

		node_pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode('PixelFormat'))
		if PySpin.IsAvailable(node_pixel_format) and PySpin.IsWritable(node_pixel_format):

			# Retrieve the desired entry node from the enumeration node
			node_pixel_format_mono16 = PySpin.CEnumEntryPtr(node_pixel_format.GetEntryByName('Mono16'))
			if PySpin.IsAvailable(node_pixel_format_mono16) and PySpin.IsReadable(node_pixel_format_mono16):

				# Retrieve the integer value from the entry node
				pixel_format_mono16 = node_pixel_format_mono16.GetValue()
				# Set integer as new value for enumeration node
				node_pixel_format.SetIntValue(pixel_format_mono16)
				print(self.LOG_PREFIX + "PIXEL_FORMAT=%s" % node_pixel_format.GetCurrentEntry().GetSymbolic())
			else:
				print(self.LOG_PREFIX + "Camera pixel format mono 16 not available")
		else:
			print(self.LOG_PREFIX + "Camera pixel format not available")



	def scan(self, SCAN_NAME, metadata, path):

		# If the preview process is open, close it.
		if(self.displayPreview):
			self.toggle_preview()


		camList, system = self.init_spinnaker()
		camera = camList.GetByIndex(0)
		self.init_camera(camera, True, 'Continuous')
		nodemap = camera.GetNodeMap()

		self.set_camera_pixel_format(nodemap)
		self.set_camera_exposure(camera)
		self.set_camera_gain(camera)
		camera.BeginAcquisition()


		keepAlive = True
		frames = []
		# Tell the scanner the camera is ready to go
		self.mainQueue.put([5, -1, [1]])

		while keepAlive:

			msg = self.queue.get()

			if msg[2][0] == "CAPTURE":

				self.grab_next_image_by_trigger(nodemap, camera)
				image_result = camera.GetNextImage()

				if image_result.IsIncomplete():
					print(self.LOG_PREFIX + "Image incomplete with image status=%d" % image_result.GetImageStatus())
				else:
					frames.append(image_result)
					# Send confirmation of capture to scanner
					self.mainQueue.put([5, -1, [1]])

			elif msg[2][0] == "STOP":
				keepAlive = False


		imageStack = []
		for i in range(0, len(frames)):
			imageConverted = frames[i].Convert(PySpin.PixelFormat_Mono16, PySpin.HQ_LINEAR)
			imageStack.append(imageConverted.GetNDArray())
			frames[i].Release()

		filename = path + "\\" + SCAN_NAME + ".tif"
		imageStack = np.asarray(imageStack)

		metadata_dict = {}
		for item in metadata:
			metadata_dict.update({item[0] : item[1]})
		tif.imwrite(filename, imageStack, imagej=True, metadata = metadata_dict)

		"""
		snippet for reading metadata back out of imagej tiff stacks 
		
		with tif.TiffFile(filename) as stack:
			imagejHyperstack = stack.asarray()
			imagejMetadata = stack.imagej_metadata
			print(imagejHyperstack.shape)
			print(imagejMetadata['title'])
		"""



		camera.EndAcquisition()
		self.reset_trigger(nodemap)
		camera.DeInit()
		del camera
		camList.Clear()
		system.ReleaseInstance()


	def process_msg(self, msg):

		functionIndex = msg[1]

		if functionIndex == 0:
			self.toggle_preview()
		elif functionIndex == 1:
			self.set_exposure(msg[2][0])
		elif functionIndex == 2:
			self.set_gain(msg[2][0])
		elif functionIndex == 3:
			self.scan(msg[2][0], msg[2][1], msg[2][2])


	def mainloop(self):
		while True:
			if not self.queue.empty():
				self.process_msg(self.queue.get())


def launch_camera(queue, mainQueue):

	cc = CameraController(queue, mainQueue)
	print("Camera Process: Initialization complete")
	cc.mainloop()
