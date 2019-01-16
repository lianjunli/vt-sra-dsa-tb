#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 gr-dsa_vt author.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import numpy
import math
import Queue
import time
from gnuradio import gr
import pmt
from gnuradio import uhd
import threading
from threading import Timer

class sensing_engine(gr.sync_block):
    """
    docstring for block sensing_engine
    """
    def __init__(self, usrp_source, epsilon_threshold):
        gr.sync_block.__init__(self,
            name="sensing_engine",
            in_sig=[numpy.float32],
            out_sig=None)
        self.usrp_source=usrp_source
        self.slot_interval=0.5
        self.sensing_duration = 0.02
        self.time_factor=1
        self.sum_slots=-1
        self.epsilon_threshold=epsilon_threshold
        self.average_power_dbm = 0.0
        self.samp_rate = 1000000
        self.N_samp = int((self.sensing_duration* self.samp_rate))
        self.magnitude_sq = []
        self.primary_user_status = {
            'no_result': 0,
            'not_detected': 1,
            'detected': 2,
        }  # 0: energy det. has no result, 1: PU not detected, 2: PU detected.
        self.energy_det_status = self.primary_user_status['no_result']
        currenttime = self.usrp_source.get_mboard_sensor("gps_time")
        self.start_time=time.time()
        self.slot_monitor()

    def slot_monitor(self):
        # self.timer.cancel()
        # del self.timer
        mm = time.time()
        self.sum_slots += 1
        # usrp_frac_time = (mm * self.time_factor - numpy.floor(mm * self.time_factor))
        self.cur_slot = self.sum_slots % 3  #int(numpy.floor(usrp_frac_time * self.num_slots))
        #print "%6f mm is %6f init time is %6f" %(self.slot_interval+self.slot_interval-mm+self.init_time,mm,self.init_time)
        self.timer = threading.Timer(self.start_time + self.slot_interval - mm, self.slot_monitor)
        self.timer.start()
        self.start_time += self.slot_interval
        time.sleep(self.sensing_duration*1.5) # wait to gather the sensing data
        if len(self.magnitude_sq) > 0:
            average_mag_sq = self.calculate_average_mag_sq()
            self.energy_det_status = self.detect_primary_user(average_mag_sq)
        print 'slot: ', self.cur_slot, ' sensing data len: ', len(self.magnitude_sq),' avg power: ',self.average_power_dbm,' sensing status: ', self.energy_det_status
        return 0

    def detect_primary_user(self, average_mag_sq):
        # Calculate the SNR.
        self.average_power_dbm = self.calculate_power_dbm(average_mag_sq)

        # If the power [dBm] is larger than epsilon [dBm], then we have detected a primary user.
        if self.average_power_dbm > self.epsilon_threshold:
            return self.primary_user_status['detected']
        else:
            return self.primary_user_status['not_detected']

    # Calculate the new average magnitude squared with the new data that has arrived.
    def calculate_average_mag_sq(self):
        return sum(self.magnitude_sq) / len(self.magnitude_sq)

    # Update the list of energy samples with the new data that has arrived.
    def set_magnitude_sq(self, mag_sq_usrp):
        len_mag_sq_usrp = len(mag_sq_usrp)

        free_space = self.N_samp - len(self.magnitude_sq)  # Amount of free space for new data.

        # If we cannot fit the entire array of new data, then we need to add as much as we can.
        if len_mag_sq_usrp > free_space:
            # print 'new data len: ', len_mag_sq_usrp
            # Clear up space for the new data. We don't have to worry about out-of-bounds range, python handles it.
            del self.magnitude_sq[0:(len_mag_sq_usrp - free_space)]

            free_space = self.N_samp - len(self.magnitude_sq)

            # The newest data is at the end of the mag_sq_usrp, resize it to fit the free space amount and append it.
            mag_sq_usrp = mag_sq_usrp[(len_mag_sq_usrp - free_space):]
            self.magnitude_sq.extend(mag_sq_usrp)
        # If we can fit the entire array of new data, just insert it.
        elif len_mag_sq_usrp <= free_space:
            self.magnitude_sq.extend(mag_sq_usrp)

    @staticmethod
    def calculate_power_dbm(magnitude_squared):
        power_watts = magnitude_squared / float(50)  # Power [Watts] = Volts^2/Ohms

        try:
            power_dbm = (10 * math.log10(power_watts)) + 30  # Power [dBm] = Power [W] + 30dB
        except ValueError:
            return 0

        return power_dbm


    def work(self, input_items, output_items):
        p0_mag_sq_usrp = input_items[0]
        # Get a new average energy level for the new data that arrived.
        self.set_magnitude_sq(p0_mag_sq_usrp)
        #self.consume_each(len(input_items[0]))
        return len(input_items[0])
