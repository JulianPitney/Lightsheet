import PySpin
import cv2
import tifffile as tif
import numpy as np
import os
import random


class TriggerType:
    SOFTWARE = 1
    HARDWARE = 2


CHOSEN_TRIGGER = TriggerType.SOFTWARE


class CameraController(object):

    def __init__(self, queue, mainQueue, guiVideoQueue, guiLogQueue):

        # Process objects
        self.queue = queue
        self.mainQueue = mainQueue
        self.guiVideoQueue = guiVideoQueue
        self.guiLogQueue = guiLogQueue
        self.LOG_PREFIX = "CameraController: "

        # Image Parameters
        self.imagingObjectiveMagnification = 5
        self.umPerPixel_5x = 0.714
        self.umPerPixel_10x = 0.345
        self.umPerPixel_20x = 0.181
        self.umPerPixel_40x = 0.090
        self.umPerPixel_63x = 0.059
        # Acquisition config
        self.EXPOSURE = 30000
        self.GAIN = 23
        self.FPS = 20.00
        self.WIDTH = 2448
        self.HEIGHT = 2048
        # Spinnaker Initialization
        self.camList, self.system = self.init_spinnaker()
        self.cameras = []
        self.nodemaps = []
        self.lastFrame = []
        for i in range(0, len(self.camList)):
            camera, nodemap = self.init_video_stream(i)
            self.cameras.append(camera)
            self.nodemaps.append(nodemap)


        self.guiLogQueue.put(self.LOG_PREFIX + "Initialization complete")

#--------------------------------------------------------------------------------------------#
#                               SPINNAKER CONFIG START                                       #
#--------------------------------------------------------------------------------------------#
    def init_spinnaker(self):

        system = PySpin.System.GetInstance()
        camList = system.GetCameras()

        if camList.GetSize() == 0:
            camList.Clear()
            system.ReleaseInstance()
            self.guiLogQueue.put(self.LOG_PREFIX + "No cameras were found")
            return None, None
        else:
            self.guiLogQueue.put(self.LOG_PREFIX + str(camList.GetSize()) + " cameras detected")
            return camList, system
#--------------------------------------------------------------------------------------------#
#                               SPINNAKER CONFIG END                                         #
#--------------------------------------------------------------------------------------------#








#--------------------------------------------------------------------------------------------#
#                               CAMERA CONFIG START                                          #
#--------------------------------------------------------------------------------------------#
    def init_video_stream(self, cameraIndex):

        camera = self.camList.GetByIndex(cameraIndex)
        nodemap = self.initialize_camera(camera, True, 'Continuous')
        camera.BeginAcquisition()
        return camera, nodemap



    def initialize_camera(self, camera, configureTrigger, acquisitionMode):

        camera.Init()
        nodemap = camera.GetNodeMap()

        self.set_camera_pixel_format(nodemap)
        self.set_camera_exposure(camera, 30000)
        self.set_camera_gain(camera, 24)

        # In order to access the node entries, they have to be casted to a pointer type (CEnumerationPtr here)
        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            self.guiLogQueue.put(self.LOG_PREFIX + "Unable to access acquisition mode of camera")

        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName(acquisitionMode)
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                node_acquisition_mode_continuous):
            self.guiLogQueue.put(self.LOG_PREFIX + "Unable to set acquisition mode of camera")

        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        if configureTrigger:
            self.configure_trigger(camera)

        return nodemap

    def deinitialize_camera(self, camera, nodemap):

        camera.EndAcquisition()
        self.reset_trigger(nodemap)
        camera.DeInit()
        del camera



    def set_camera_fps(self, nodemap):

        enableAcquisitionFrameRateNode = PySpin.CBooleanPtr(nodemap.GetNode("AcquisitionFrameRateEnable"))
        if enableAcquisitionFrameRateNode.GetAccessMode() != PySpin.RW:
            self.guiLogQueue.put(self.LOG_PREFIX + "Unable to enable camera acquistion frame rate control")
        else:
            enableAcquisitionFrameRateNode.SetValue(True)

        frameRateNode = PySpin.CFloatPtr(nodemap.GetNode("AcquisitionFrameRate"))
        if frameRateNode.GetAccessMode() != PySpin.RW:
            self.guiLogQueue.put(self.LOG_PREFIX + "Unable to set camera acquisition frame rate")
        else:
            frameRateNode.SetValue(self.FPS)



    def set_camera_gain(self, camera, gain):

        if camera.GainAuto.GetAccessMode() != PySpin.RW:
            self.guiLogQueue.put(self.LOG_PREFIX + "Unable to disable camera automatic gain")
            return False
        else:
            camera.GainAuto.SetValue(PySpin.GainAuto_Off)

        if camera.Gain.GetAccessMode() != PySpin.RW:
            self.guiLogQueue.put(self.LOG_PREFIX + "Unable to set camera gain")
            return False
        else:
            gain = min(camera.Gain.GetMax(), gain)
            camera.Gain.SetValue(gain)
            self.guiLogQueue.put(self.LOG_PREFIX + "GAIN=" + str(gain))

    def set_camera_exposure(self, camera, exposure):

        if camera.ExposureAuto.GetAccessMode() != PySpin.RW:
            self.guiLogQueue.put(self.LOG_PREFIX + 'Unable to disable camera automatic exposure')
            return False
        else:
            camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)

        if camera.ExposureTime.GetAccessMode() != PySpin.RW:
            self.guiLogQueue.put(self.LOG_PREFIX + 'Unable to set camera exposure')
            return False
        else:
            # Ensure desired exposure time does not exceed the maximum
            exposure = min(camera.ExposureTime.GetMax(), exposure)
            camera.ExposureTime.SetValue(exposure)
            self.guiLogQueue.put(self.LOG_PREFIX + "EXPOSURE=" + str(exposure))

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
                self.guiLogQueue.put(self.LOG_PREFIX + "PIXEL_FORMAT=%s" % node_pixel_format.GetCurrentEntry().GetSymbolic())
            else:
                self.guiLogQueue.put(self.LOG_PREFIX + "Camera pixel format mono 16 not available")
        else:
            self.guiLogQueue.put(self.LOG_PREFIX + "Camera pixel format not available")



    def configure_trigger(self, camera):

        result = True

        if CHOSEN_TRIGGER == TriggerType.SOFTWARE:
            pass
        elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
            pass

        try:
            # Ensure trigger mode off
            # The trigger must be disabled in order to configure whether the source
            # is software or hardware.
            nodemap = camera.GetNodeMap()
            node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
            if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
                self.guiLogQueue.put(self.LOG_PREFIX + 'Unable to access camera trigger mode')
                return False

            node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
            if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
                self.guiLogQueue.put(self.LOG_PREFIX + 'Unable to disable camera trigger mode')
            # return False

            node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())

            # Select trigger source
            # The trigger source must be set to hardware or software while trigger
            # mode is off.
            node_trigger_source = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerSource'))
            if not PySpin.IsAvailable(node_trigger_source) or not PySpin.IsWritable(node_trigger_source):
                self.guiLogQueue.put(self.LOG_PREFIX + 'Unable to access camera trigger source')
                return False

            if CHOSEN_TRIGGER == TriggerType.SOFTWARE:
                node_trigger_source_software = node_trigger_source.GetEntryByName('Software')
                if not PySpin.IsAvailable(node_trigger_source_software) or not PySpin.IsReadable(
                        node_trigger_source_software):
                    self.guiLogQueue.put(self.LOG_PREFIX + 'Unable to set camera trigger source')
                    return False
                node_trigger_source.SetIntValue(node_trigger_source_software.GetValue())

            elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
                node_trigger_source_hardware = node_trigger_source.GetEntryByName('Line0')
                if not PySpin.IsAvailable(node_trigger_source_hardware) or not PySpin.IsReadable(
                        node_trigger_source_hardware):
                    self.guiLogQueue.put(self.LOG_PREFIX + 'Unable to set camera trigger source')
                    return False
                node_trigger_source.SetIntValue(node_trigger_source_hardware.GetValue())

            # Turn trigger mode on
            # Once the appropriate trigger source has been set, turn trigger mode
            # on in order to retrieve images using the trigger.
            node_trigger_mode_on = node_trigger_mode.GetEntryByName('On')
            if not PySpin.IsAvailable(node_trigger_mode_on) or not PySpin.IsReadable(node_trigger_mode_on):
                self.guiLogQueue.put(self.LOG_PREFIX + 'Unable to enable camera trigger mode')
                return False

            node_trigger_mode.SetIntValue(node_trigger_mode_on.GetValue())

        except PySpin.SpinnakerException as ex:
            self.guiLogQueue.put(self.LOG_PREFIX + 'Error=%s' % ex)
            return False

        return result



    def reset_trigger(self, nodemap):

        try:
            result = True
            node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
            if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
                self.guiLogQueue.put(self.LOG_PREFIX + 'Unable to disable camera trigger mode')
                return False

            node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
            if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
                self.guiLogQueue.put(self.LOG_PREFIX + 'Unable to disable camera trigger mode')
                return False

            node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())

        except PySpin.SpinnakerException as ex:
            self.guiLogQueue.put(self.LOG_PREFIX + 'Error=%s' % ex)
            result = False

        return result
#--------------------------------------------------------------------------------------------#
#                               CAMERA CONFIG END                                            #
#--------------------------------------------------------------------------------------------#









#--------------------------------------------------------------------------------------------#
#                               CAMERA CONTROL START                                         #
#--------------------------------------------------------------------------------------------#
    def grab_next_image_by_trigger(self, nodemap):

        try:
            result = True

            if CHOSEN_TRIGGER == TriggerType.SOFTWARE:

                # Execute software trigger
                node_softwaretrigger_cmd = PySpin.CCommandPtr(nodemap.GetNode('TriggerSoftware'))
                if not PySpin.IsAvailable(node_softwaretrigger_cmd) or not PySpin.IsWritable(node_softwaretrigger_cmd):
                    self.guiLogQueue.put(self.LOG_PREFIX + 'Unable to execute camera trigger')
                    return False

                node_softwaretrigger_cmd.Execute()


            elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
                self.guiLogQueue.put(self.LOG_PREFIX + 'Camera hardware trigger selected')

        except PySpin.SpinnakerException as ex:
            self.guiLogQueue.put(self.LOG_PREFIX + 'Error=%s' % ex)
            return False

        return result


    def retrieve_next_image(self, cameraIndex):

        self.grab_next_image_by_trigger(self.nodemaps[cameraIndex])
        image_result = self.cameras[cameraIndex].GetNextImage()
        if image_result.IsIncomplete():
            self.guiLogQueue.put(self.LOG_PREFIX + "Image incomplete with image status=%d" % image_result.GetImageStatus())
            self.lastFrame = []
            return False
        else:
            image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
            image_converted = image_converted.GetNDArray()
            self.lastFrame = image_converted
            self.guiVideoQueue.put([4, -1, [self.lastFrame]])
            return True






#--------------------------------------------------------------------------------------------#
#                               CAMERA CONTROL END                                           #
#--------------------------------------------------------------------------------------------#






#--------------------------------------------------------------------------------------------#
#                               OpenCV UTILITY                                               #
#--------------------------------------------------------------------------------------------#

    def set_scalebar_size(self, imagingObjectiveMagnification):
        self.imagingObjectiveMagnification = imagingObjectiveMagnification
        self.guiLogQueue.put(self.LOG_PREFIX + "MAGNIFICATION=" + str(self.imagingObjectiveMagnification) + "x")

    def paint_scalebar(self, frame):

        umPixelsRatio = self.umPerPixel_5x

        if self.imagingObjectiveMagnification == 5:
            umPixelsRatio = self.umPerPixel_5x
        elif self.imagingObjectiveMagnification == 10:
            umPixelsRatio = self.umPerPixel_10x
        elif self.imagingObjectiveMagnification == 20:
            umPixelsRatio = self.umPerPixel_20x
        elif self.imagingObjectiveMagnification == 40:
            umPixelsRatio = self.umPerPixel_40x
        elif self.imagingObjectiveMagnification == 63:
            umPixelsRatio = self.umPerPixel_63x

        height, width = frame.shape[:2]
        # Figure out how many pixels represent 10um
        lineLengthPixels = int(10 / umPixelsRatio)
        p1 = (50, height - 50)
        p2 = (50 + lineLengthPixels, height - 50)
        cv2.line(frame, p1, p2, (255, 255, 255), 2)

        cp1 = ((50 + int(lineLengthPixels / 2)), (height - 40))
        cp2 = ((50 + int(lineLengthPixels / 2)), (height - 60))
        cv2.line(frame, cp1, cp2, (255, 255, 255), 2)

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, '10um', ((int(lineLengthPixels / 2)), (height - 80)), font, 1, (255, 255, 255), 2,
                    cv2.LINE_AA)

        return frame



    def paint_fps(self, frame, fps):

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, str(fps) + " FPS", (20, 40), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
        return frame
#--------------------------------------------------------------------------------------------#
#                               OpenCV UTILITY END                                           #
#--------------------------------------------------------------------------------------------#



    def scan(self, SCAN_NAME, metadata, path, cameraIndex):


        keepAlive = True
        imageStack = []
        # Tell the scanner the camera is ready to go
        self.mainQueue.put([5, -1, [1]])

        while keepAlive:

            msg = self.queue.get()

            if msg[2][0] == "CAPTURE":

                if self.retrieve_next_image(0):
                    image_result = self.lastFrame
                    imageStack.append(image_result)
                    # Send confirmation of capture to scanner
                    self.mainQueue.put([5, -1, [1]])
                else:
                    self.guiLogQueue.put(self.LOG_PREFIX + "Scanner was unable to retrieve frame from camera")

            elif msg[2][0] == "STOP":
                keepAlive = False



        filename = path + "\\" + SCAN_NAME + ".tif"
        imageStack = np.asarray(imageStack, dtype=np.uint16)

        metadata_dict = {}
        for item in metadata:
            metadata_dict.update({item[0]: item[1]})

        # Make sure we don't overwrite anything
        while os.path.exists(filename):
            self.guiLogQueue.put(self.LOG_PREFIX + "An attempt was made to overwrite an existing file. This attempt has been blocked.")
            self.guiLogQueue.put(self.LOG_PREFIX + "The current scan has had a random number appended to the filename.")
            randomSuffix = str(random.randint(100000, 900000))
            filename = os.path.splitext(filename)[0]
            filename += randomSuffix + ".tif"

        self.guiLogQueue.put(self.LOG_PREFIX + "Saving stack to disk...")
        tif.imwrite(filename, imageStack, imagej=False, metadata=metadata_dict)
        self.guiLogQueue.put(self.LOG_PREFIX + "Stack saved successfully!")
        self.mainQueue.put([5, -1, [1]])

    def process_msg(self, msg):

        functionIndex = msg[1]

        if functionIndex == 0:
            pass
        elif functionIndex == 1:
            self.set_camera_exposure(self.cameras[0], msg[2][0])
        elif functionIndex == 2:
            self.set_camera_gain(self.cameras[0], msg[2][0])
        elif functionIndex == 3:
            self.scan(msg[2][0], msg[2][1], msg[2][2], msg[2][3])
        elif functionIndex == 4:
            self.set_scalebar_size(msg[2][0])

    def mainloop(self):
        while True:
            if not self.queue.empty():
                self.process_msg(self.queue.get())

            self.retrieve_next_image(0)

def launch_camera(queue, mainQueue, guiVideoQueue, guiLogQueue):
    cc = CameraController(queue, mainQueue, guiVideoQueue, guiLogQueue)
    cc.mainloop()
