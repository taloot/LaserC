#!/usr/bin/python
import os
import sys
import hal
import time
import serial
import codecs

header          = 'BFFB'
address         = 'FF'
cmdRead         = '01'
cmdSet          = '02'
reservedFirst   = '00'
reservedSecond  = '000000'
databitsforRead = '00000000'
alarmbitsforCmd = '00000000'
started         = False
errorCount      = 0
c_sensor        = '7C'
c_laserstatus   = '15'
c_laserpower    = '21'
c_laseronoff    = '22'
c_laserconmode  = '24'
c_eparttemp     = '28'
c_eparthumd     = '29'
c_opcooltemp    = '2B'
c_reflecdaval   = '3D'
c_drivbodvol1   = '50'
c_drivbodvol2   = '51'
c_machinedate   = '47'
c_machinetime   = '48'
c_regcodeassign = '71'
c_unknown       = '7F'

# create laser232 component
laser232 = hal.component('laser232')
laser232.newpin('laser_power_set', hal.HAL_FLOAT, hal.HAL_IN)               # set laser output power
laser232.newpin('laser_control_mode_set', hal.HAL_FLOAT, hal.HAL_IN)        # set laser control mode
laser232.newpin('laser_onoff_set', hal.HAL_BIT, hal.HAL_IN)                 # set laser ON/OFF 
laser232.newpin('registration_code_assign_set', hal.HAL_FLOAT, hal.HAL_IN)  # set registration code assignment
laser232.newpin('enable', hal.HAL_BIT, hal.HAL_IN)                          # enabler
    # temperature of sensors
laser232.newpin('temperature_sensor1', hal.HAL_S32, hal.HAL_OUT)
laser232.newpin('temperature_sensor2', hal.HAL_S32, hal.HAL_OUT)
laser232.newpin('temperature_sensor3', hal.HAL_S32, hal.HAL_OUT)
laser232.newpin('temperature_sensor4', hal.HAL_S32, hal.HAL_OUT)
laser232.newpin('temperature_sensor5', hal.HAL_S32, hal.HAL_OUT)

#/*--- both

laser232.newpin('laser_start_status', hal.HAL_BIT, hal.HAL_OUT)             # Laser start status
hal.connect('laser232.laser_start_status', 'laser232:laser-start-status')
laser232.newpin('laser_en_status', hal.HAL_BIT, hal.HAL_OUT)                # Laser enable status
hal.connect('laser232.laser_en_status', 'laser232:laser-en-status')

#laser232.newpin('laser_start_en_status', hal.HAL_BIT, hal.HAL_OUT)               # both link to laser start and enable 
#hal.connect('laser232.laser_start_en_status', 'laser232:laser-start-en-status')
#---*/
laser232.newpin('laser_pwm_status', hal.HAL_BIT, hal.HAL_OUT)               # Laser enable status
laser232.newpin('laser_power_read', hal.HAL_S32, hal.HAL_OUT)               # output laser power
laser232.newpin('laser_on_off', hal.HAL_BIT, hal.HAL_OUT)                   # laser On/Off
laser232.newpin('laser_control_mode', hal.HAL_S32, hal.HAL_OUT)             # laser control mode
laser232.newpin('electrical_part_temperature', hal.HAL_S32, hal.HAL_OUT)    # electrical part temperature
laser232.newpin('electrical_part_humidness', hal.HAL_S32, hal.HAL_OUT)      # electrical part humidness
laser232.newpin('temperature_ocool_plate', hal.HAL_S32, hal.HAL_OUT)        # temperature of optical part cooling plate
laser232.newpin('reflective_laser_daval', hal.HAL_S32, hal.HAL_OUT)         # reflective laser DA value
laser232.newpin('driver_board_voltage1', hal.HAL_S32, hal.HAL_OUT)          # driver board voltage value 1
laser232.newpin('driver_board_voltage2', hal.HAL_S32, hal.HAL_OUT)          # driver board voltage value 2
laser232.newpin('machine_date_year', hal.HAL_S32, hal.HAL_OUT)              # machine date
laser232.newpin('machine_date_month', hal.HAL_S32, hal.HAL_OUT)             # machine 
laser232.newpin('machine_date_day', hal.HAL_S32, hal.HAL_OUT)               # machine date
laser232.newpin('machine_time_hour', hal.HAL_S32, hal.HAL_OUT)              # machine time
laser232.newpin('machine_time_minute', hal.HAL_S32, hal.HAL_OUT)            # machine time
laser232.newpin('machine_time_second', hal.HAL_S32, hal.HAL_OUT)            # machine time
laser232.newpin('alarm_status', hal.HAL_S32, hal.HAL_IN)                    # Alarm status
laser232.ready()
enabled = laser232.enable
laserstatus = 0

# connection setup
comPort = sys.argv[1]
try:
    comms = serial.Serial(comPort,
                        baudrate = 115200,
                        bytesize = 8,
                        parity = 'N',
                        stopbits = 1,
                        timeout = 0.1
                        )
except:
    print('\nCould not open {} for Laser communications\n'.format(comPort))
    raise SystemExit

# Alarm
def alarm(alarmbits):
    laser232.alarm_status = int(codecs.encode(alarmbits, "hex"))

# Set parameters
def cmd_set(ordercode, databits):
    data = '{}{}{}{}{}{}{}{}'.format(header, address, cmdSet, ordercode, databits,
                                reservedFirst, alarmbitsforCmd, reservedSecond)
    if len(data) == 34:
        packet = bytearray.fromhex(data)
        reply = ''
        comms.write(packet)
        reply = comms.readline()
        log = open('/home/tal/12.log', 'a')
        log.write('read : \n packet:' + codecs.encode(packet, 'hex') + '\n' + 'reply:' + codecs.encode(reply,'hex') + '\n')
        log.close()
        if reply:
            if reply[10:14]:
                alarm(reply[10:14])
            if reply == packet:
                return 1
    return 0

# Read parameters
def cmd_read(ordercode):
    data = '{}{}{}{}{}{}{}{}'.format(header, address, cmdRead, ordercode, databitsforRead,
                                reservedFirst, alarmbitsforCmd, reservedSecond)
    if len(data) == 34:
        packet = bytearray.fromhex(data)
        reply = ''
        comms.write(packet)
        reply = comms.readline()
        if reply:
            if len(reply) == 17 and reply[0:5] == bytearray.fromhex('{}{}{}{}'.format(header, address, cmdRead, ordercode)):
                if reply[10:14]:
                    alarm(reply[10:14])
                return reply[5:9]
    return 0

# set machine to closerelax
    # cmd_set(c_unknown,  codecs.encode(bytearray.fromhex('{:08X}'.format(int(1)))[::-1], 'hex'))
    # if not cmd_set(c_laserpower, '{:08X}'.format(int(laser232.laser_power_set))):
    #     errorCount = errorCount + 1
    # if not cmd_set(c_laseronoff, '{:08X}'.format(1)):
    #     errorCount = errorCount + 1
    if errorCount:
        errorCount = 0
        return 0
    return 1

# get parameters
def get_parameters():
    # get temperature of sensors
    cparam = cmd_read(c_sensor)
    if cparam:
        temp_param = int(codecs.encode(cparam[0:3][::-1],'hex'), 16)
        sensor_param = int(codecs.encode(cparam[3][::-1],'hex'), 16)
        if (sensor_param == 16):
            laser232.temperature_sensor1 = temp_param
        elif (sensor_param == 32):
            laser232.temperature_sensor2 = temp_param
        elif (sensor_param == 48):
            laser232.temperature_sensor3 = temp_param
        elif (sensor_param == 64):
            laser232.temperature_sensor4 = temp_param
        elif (sensor_param == 80):
            laser232.temperature_sensor5 = temp_param
        
    # get laser start status
    cparam = cmd_read(c_laserstatus)
    if cparam:
        laserstatus = int(codecs.encode(cparam[0:4][::-1],'hex'), 16)
        #if (laserstatus & 1):
        #    laser232.laser_start_status = True
        # else:
        #    laser232.laser_start_status = False
        #if (laserstatus & 4):
        #    laser232.laser_en_status = True
        #else:
        #    laser232.laser_en_status = False
        #/*--- both
        if (laserstatus & 16):
            laser232.laser_start_en_both = True
        else:
            laser232.laser_start_en_both = False
        #---*/    
        if (laserstatus & 2):
            laser232.laser_pwm_status = True
        else:
            laser232.laser_pwm_status = False

    # get output laser power
    cparam = cmd_read(c_laserpower)
    if cparam:
        laser232.laser_power_read = int(codecs.encode(cparam[0:4][::-1], "hex"), 16)

    # get laser on/off
    cparam = cmd_read(c_laseronoff)
    if cparam:
        if int(codecs.encode(cparam[0], "hex"), 16):
            laser232.laser_on_off = True
        else:
            laser232.laser_on_off = False

    # get laser control mode
    cparam = cmd_read(c_laserconmode)
    if cparam:
        laser232.laser_control_mode = int(codecs.encode(cparam[0:4][::-1], "hex"), 16)
    else:
        laser232.laser_control_mode = 3

    # get electrical part temperature
    cparam = cmd_read(c_eparttemp)
    if cparam:
        laser232.electrical_part_temperature = int(codecs.encode(cparam[0:4][::-1], "hex"), 16)

    # get electrical part humidness
    cparam = cmd_read(c_eparthumd)
    if cparam:
        laser232.electrical_part_humidness = int(codecs.encode(cparam[0:4][::-1], "hex"), 16)

    # get reflective laser DA value.
    cparam = cmd_read(c_reflecdaval)
    if cparam:
        laser232.reflective_laser_daval = int(codecs.encode(cparam[0:4][::-1], "hex"), 16)
        
    # get driver board voltage value 1.
    cparam = cmd_read(c_drivbodvol1)
    if cparam:
        laser232.driver_board_voltage1 = int(codecs.encode(cparam[0:4][::-1], "hex"), 16)

    # get driver board voltage value 2.
    cparam = cmd_read(c_drivbodvol2)
    if cparam:
        laser232.driver_board_voltage2 = int(codecs.encode(cparam[0:4][::-1], "hex"), 16)
        
    # get machine date
    cparam = cmd_read(c_machinedate)
    if cparam:
        laser232.machine_date_year = int(codecs.encode(cparam[2:4][::-1], "hex"), 16)
        laser232.machine_date_month = int(codecs.encode(cparam[1][::-1], "hex"), 16)
        laser232.machine_date_day = int(codecs.encode(cparam[0][::-1], "hex"), 16)

    # get machine time
    cparam = cmd_read(c_machinetime)
    if cparam:
        laser232.machine_time_second = int(codecs.encode(cparam[2][::-1], "hex"), 16)
        laser232.machine_time_minute = int(codecs.encode(cparam[1][::-1], "hex"), 16)
        laser232.machine_time_hour = int(codecs.encode(cparam[0][::-1], "hex"), 16)
        
    return True

# main loop
try:
    while 1:
        if hal.component_exists('lasercomp'):
            if enabled != laser232.enable:
                enabled = laser232.enable
                if not enabled:
                    close_machine()
                    comms.close()
                    started = False
            if enabled:
                if not started:
                    if not comms.isOpen():
                        comms.open()
                    if open_machine():
                        started = True
                    if started and get_parameters():
                        started = True
                    else:
                        started = False
                else:                    
                    get_parameters()

                    # set laser power
                    if laser232.laser_power_set != laser232.laser_power_read:
                        param = cmd_set(c_laserpower,  codecs.encode(bytearray.fromhex('{:08X}'.format(int(laser232.laser_power_set)))[::-1], 'hex'))
                        if param:
                            laser232.laser_power_read = laser232.laser_power_set

                    # set laser control mode
                    # if laser232.laser_control_mode_set != laser232.laser_control_mode:
                    #     param = cmd_set(c_laserconmode,  codecs.encode(bytearray.fromhex('{:08X}'.format(int(laser232.laser_control_mode_set)))[::-1], 'hex'))
                    #     if param:
                    #         laser232.laser_control_mode = laser232.laser_control_mode_set
                    # # get laser control mode
                    # else:
                    #     param_val = cmd_read(c_laserconmode)
                    #     if param_val:
                    #         laser232.laser_control_mode = float(int(codecs.encode(param_val[0:4][::-1], "hex"), 16))
                    
                    # set laser on/of
                    if laser232.laser_onoff_set != laser232.laser_on_off:
                        param =  cmd_set(c_laseronoff,  codecs.encode(bytearray.fromhex('{:08X}'.format(int(laser232.laser_onoff_set)))[::-1], 'hex'))
                        if param:
                            laser232.laser_on_off = laser232.laser_onoff_set
                    
except:
    print('Shutting down laser 232 communications')
    if started:
        if not comms.isOpen():
            comms.open()
        close_machine()
        comms.close()