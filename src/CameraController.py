import PySpin
import cv2
import os
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

		self.queue = queue
		self.mainQueue = mainQueue
		self.EXPOSURE = 30000
		self.GAIN = 25
		self.FPS = 60.00
		self.WIDTH = 1440
		self.HEIGHT = 1080
		self.displayPreview = False
		self.previewProcQueue = Queue()
		self.previewProc = None


	def set_exposure(self, exposure):
		self.EXPOSURE = int(exposure)
		self.previewProcQueue.put([-1, -1, ["EXPOSURE",self.EXPOSURE]])
		print("CAMERA_PROCESS: EXPOSURE=" + str(self.EXPOSURE) + "us")

	def set_gain(self, gain):
		self.GAIN = int(gain)
		self.previewProcQueue.put([-1, -1, ["GAIN",self.GAIN]])
		print("CAMERA_PROCESS: GAIN=" + str(self.GAIN) + "dB")

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
		#print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

		# Retrieve list of cameras from the system
		camList = system.GetCameras()

		num_cameras = camList.GetSize()

		#print('Number of cameras detected: %d' % num_cameras)

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
			self.configure_trigger(camera)

	def grab_next_image_by_trigger(self, nodemap, cam):
		"""
        This function acquires an image by executing the trigger node.

        :param cam: Camera to acquire images from.
        :param nodemap: Device nodemap.
        :type cam: CameraPtr
        :type nodemap: INodeMap
        :return: True if successful, False otherwise.
        :rtype: bool
        """
		try:
			result = True
			# Use trigger to capture image
			# The software trigger only feigns being executed by the Enter key;
			# what might not be immediately apparent is that there is not a
			# continuous stream of images being captured; in other examples that
			# acquire images, the camera captures a continuous stream of images.
			# When an image is retrieved, it is plucked from the stream.

			if CHOSEN_TRIGGER == TriggerType.SOFTWARE:

				# Execute software trigger
				node_softwaretrigger_cmd = PySpin.CCommandPtr(nodemap.GetNode('TriggerSoftware'))
				if not PySpin.IsAvailable(node_softwaretrigger_cmd) or not PySpin.IsWritable(node_softwaretrigger_cmd):
					print('Unable to execute trigger. Aborting...')
					return False

				node_softwaretrigger_cmd.Execute()

			# TODO: Blackfly and Flea3 GEV cameras need 2 second delay after software trigger

			elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
				print('Use the hardware to trigger image acquisition.')

		except PySpin.SpinnakerException as ex:
			print('Error: %s' % ex)
			return False

		return result






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
				print('Unable to disable trigger mode (node retrieval). Aborting...')
				return False

			node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
			if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
				print('Unable to disable trigger mode (enum entry retrieval). Aborting...')
				# return False

			node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())

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

		except PySpin.SpinnakerException as ex:
			print('Error: %s' % ex)
			return False

		return result

	def reset_trigger(self, nodemap):
		"""
        This function returns the camera to a normal state by turning off trigger mode.

        :param nodemap: Transport layer device nodemap.
        :type nodemap: INodeMap
        :returns: True if successful, False otherwise.
        :rtype: bool
        """
		try:
			result = True
			node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
			if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
				print('Unable to disable trigger mode (node retrieval). Aborting...')
				return False

			node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
			if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
				print('Unable to disable trigger mode (enum entry retrieval). Aborting...')
				return False

			node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())

		except PySpin.SpinnakerException as ex:
			print('Error: %s' % ex)
			result = False

		return result



	def toggle_preview(self):


		self.displayPreview = not self.displayPreview

		if(self.displayPreview):
			print("Starting preview window!")
			while not self.previewProcQueue.empty():
				self.previewProcQueue.get()
			p = Process(target=self.display_preview, args=(self.previewProcQueue,))
			p.start()
			self.previewProc = p
		else:
			print("Closing preview window!")
			self.previewProcQueue.put([-1, -1, ["False"]])
			self.previewProc.join()
			self.previewProc = None




	def display_preview(self, inputQueue):

		keepAlive = "True"
		camList, system = self.init_spinnaker()
		camera = camList.GetByIndex(0)
		self.init_camera(camera, False, 'Continuous')
		nodemap = camera.GetNodeMap()

		# Boolean node
		enableAcquisitionFrameRateNode = PySpin.CBooleanPtr(nodemap.GetNode("AcquisitionFrameRateEnable"))
		if enableAcquisitionFrameRateNode.GetAccessMode() != PySpin.RW:
			print("Unable to enable Acquistion Frame Rate control. Aborting...")
		else:
			enableAcquisitionFrameRateNode.SetValue(True)

		frameRateNode = PySpin.CFloatPtr(nodemap.GetNode("AcquisitionFrameRate"))
		if frameRateNode.GetAccessMode() != PySpin.RW:
			print("Unable to set Acquisition Frame Rate. Aborting...")
		else:
			frameRateNode.SetValue(self.FPS)


		cv2.namedWindow('image',cv2.WINDOW_NORMAL)
		cv2.resizeWindow('image',640,480)


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
						print('Unable to set exposure time. Aborting...')
						return False
					else:
						# Ensure desired exposure time does not exceed the maximum
						self.EXPOSURE = min(camera.ExposureTime.GetMax(), self.EXPOSURE)
						camera.ExposureTime.SetValue(self.EXPOSURE)

						# Update FPS too.
						enableAcquisitionFrameRateNode = PySpin.CBooleanPtr(
							nodemap.GetNode("AcquisitionFrameRateEnable"))
						if enableAcquisitionFrameRateNode.GetAccessMode() != PySpin.RW:
							print("Unable to enable Acquistion Frame Rate control. Aborting...")
						else:
							enableAcquisitionFrameRateNode.SetValue(True)

						frameRateNode = PySpin.CFloatPtr(nodemap.GetNode("AcquisitionFrameRate"))
						if frameRateNode.GetAccessMode() != PySpin.RW:
							print("Unable to set Acquisition Frame Rate. Aborting...")
						else:
							frameRateNode.SetValue(self.FPS)


				elif msg[2][0] == "GAIN":
					self.GAIN = int(msg[2][1])

					if camera.Gain.GetAccessMode() != PySpin.RW:
						print("Unable to set gain. Aborting...")
						return False
					else:
						self.GAIN
						self.GAIN = min(camera.Gain.GetMax(), self.GAIN)
						camera.Gain.SetValue(self.GAIN)

			image_result = camera.GetNextImage()
			if image_result.IsIncomplete():
				print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
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
				print("FPS=" + str(fpsCounter))
				fpsCounter = 0
				start = time.time()

		camera.EndAcquisition()
		camera.DeInit()
		del camera
		camList.Clear()
		system.ReleaseInstance()
		return 0



	def set_camera_gain(self, camera):

		if camera.GainAuto.GetAccessMode() != PySpin.RW:
			print("Unable to disable automatic gain. Aborting...")
			return False
		else:
			camera.GainAuto.SetValue(PySpin.GainAuto_Off)

		if camera.Gain.GetAccessMode() != PySpin.RW:
			print("Unable to set gain. Aborting...")
			return False
		else:
			self.GAIN = min(camera.Gain.GetMax(), self.GAIN)
			camera.Gain.SetValue(self.GAIN)


	def set_camera_exposure(self, camera):

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
				print('CAMERA_PROCESS: PIXEL_FORMAT=' + '%s' % node_pixel_format.GetCurrentEntry().GetSymbolic())
			else:
				print('Pixel format mono 16 not available...')
		else:
			print('Pixel format not available...')



	def scan(self, SCAN_NAME, metadata):

		# If the preview window is open, close it.
		if(self.displayPreview):
			self.toggle_preview()


		camList, system = self.init_spinnaker()
		camera = camList.GetByIndex(0)
		self.init_camera(camera, True, 'Continuous')
		nodemap = camera.GetNodeMap()

		path = os.getcwd() + '\\..\\scans\\' + SCAN_NAME
		try:
			os.mkdir(path)
		except OSError:
			print ("Creation of the directory %s failed" % path)
		else:
			#print ("Successfully created the directory %s " % path)
			pass

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
					print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
				else:
					frames.append(image_result)

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
			self.scan(msg[2][0], msg[2][1])


	def mainloop(self):
		while True:
			if not self.queue.empty():
				self.process_msg(self.queue.get())


def launch_camera(queue, mainQueue):

	cc = CameraController(queue, mainQueue)
	cc.mainloop()
