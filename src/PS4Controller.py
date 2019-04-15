#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file presents an interface for interacting with the Playstation 4 Controller
# in Python. Simply plug your PS4 controller into your computer using USB and run this
# script!
#
# NOTE: I assume in this script that the only joystick plugged in is the PS4 controller.
#       if this is not the case, you will need to change the class accordingly.
#
# Copyright © 2015 Clay L. McLeod <clay.l.mcleod@gmail.com>
#
# Distributed under terms of the MIT license.

import os
import pprint
import pygame
from time import sleep


class PS4Controller(object):
    """Class representing the PS4 controller. Pretty straightforward functionality."""

    controller = None
    axis_data = None
    button_data = None
    hat_data = None


    def __init__(self, queue, mainQueue):
        """Initialize the joystick components"""

        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()
        self.queue = queue
        self.mainQueue = mainQueue
        self.last_axis0_input = 0
        self.last_axis1_input = 0
        self.last_axis2_input = 0
        self.last_axis3_input = 0

    def listen(self):
        """Listen for events to happen"""

        if not self.axis_data:
            self.axis_data = {}

        if not self.button_data:
            self.button_data = {}
            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False

        if not self.hat_data:
            self.hat_data = {}
            for i in range(self.controller.get_numhats()):
                self.hat_data[i] = (0, 0)


        while True:

            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    self.process_axis_event(event)
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.process_button_down_event(event)
                elif event.type == pygame.JOYBUTTONUP:
                    self.process_button_up_event(event)
                elif event.type == pygame.JOYHATMOTION:
                    self.process_hat_motion_event(event)

            # TODO: Add this when we get x-axis motor. Right now the arduino
            # TODO: isn't set up to handle x-axis and will crash if it gets requests for it.
            #if(self.last_axis0_input > 0.1):
            #    msg = [2, 4, [3, self.last_axis0_input, True]]
            #    self.mainQueue.put(msg)
            #elif(self.last_axis0_input < -0.1):
            #    msg = [2, 4, [3, self.last_axis0_input, False]]
            #    self.mainQueue.put(msg)

            if self.last_axis1_input > 0.1:
                msg = [2, 4, [1, self.last_axis1_input, True]]
                self.mainQueue.put(msg)
            elif self.last_axis1_input < -0.1:
                msg = [2, 4, [1, self.last_axis1_input, False]]
                self.mainQueue.put(msg)

            if self.last_axis3_input > 0.1:
                msg = [2, 4, [2, self.last_axis3_input, True]]
                self.mainQueue.put(msg)
            elif self.last_axis3_input < -0.1:
                msg = [2, 4, [2, self.last_axis3_input, False]]
                self.mainQueue.put(msg)


			# Delay this process to control the number of messages being sent by the PS4 controller.
            # (The controller can spit out messages much faster than the arduino/motors can process/execute those
            # messages).
            sleep(0.03)



    def process_axis_event(self, event):

        if event.axis == 0:
            self.last_axis0_input = event.value
        elif event.axis == 1:
            self.last_axis1_input = event.value
        elif event.axis == 2:
            self.last_axis2_input = event.value
        elif event.axis == 3:
            self.last_axis3_input = event.value


    def process_button_down_event(self, event):

        if event.button == 0:
            # Tell arduinoController to toggle coarse jog
            self.mainQueue.put([2, 5, []])
        elif event.button == 1:
            # Tell the scanner to scan a stack
            self.mainQueue.put([5, 0, []])
        elif event.button == 2:
            # Tell arduinoController to toggle laser
            self.mainQueue.put([2, 0, []])
        elif event.button == 3:
            # Tell cameraController to toggle preview window
            self.mainQueue.put([1, 0, []])


    def process_button_up_event(self, event):
        pass

    def process_hat_motion_event(self, event):
        pass




def launch_ps4_controller(queue, mainQueue):

    ps4 = PS4Controller(queue, mainQueue)
    ps4.listen()
