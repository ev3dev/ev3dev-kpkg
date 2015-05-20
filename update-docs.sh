#!/bin/bash

set -e

: ${KERNEL:=kernel}
: ${WEBSITE:=ev3dev.github.io}

rm -f ${WEBSITE}/docs/drivers/*.markdown
./kernel-doc-text-to-markdown.py ${KERNEL} ${WEBSITE} \
	drivers/lego/brickpi/brickpi_{ld,i2c_sensor}.c \
	drivers/lego/core/lego_port_class.c \
	drivers/lego/ev3/legoev3_motor_core.c \
	drivers/lego/ev3/legoev3_ports_core.c \
	drivers/lego/motors/{dc,servo,tacho}_motor_class.c \
	drivers/lego/motors/rcx_{led,motor}.c \
	drivers/lego/sensors/{ev3,nxt}_analog_sensor_core.c \
	drivers/lego/sensors/ev3_uart_sensor_ld.c \
	drivers/lego/sensors/ht_nxt_smux_i2c_sensor.c \
	drivers/lego/sensors/lego_sensor_class.c \
	drivers/lego/sensors/nxt_i2c_sensor_core.c

rm -f ${WEBSITE}/docs/sensors/*.markdown
./sensor-defs-to-markdown.py \
	--kernel ${KERNEL} \
	--website ${WEBSITE} \
	--header-files \
		drivers/lego/sensors/ev3_analog_sensor.h \
		drivers/lego/sensors/ev3_uart_sensor.h \
		drivers/lego/sensors/nxt_analog_sensor.h \
		drivers/lego/sensors/nxt_i2c_sensor.h \
	--source-files \
		drivers/lego/sensors/*_defs.c \
		drivers/lego/wedo/wedo_{hub,sensor}.c

rm -f ${WEBSITE}/docs/ports/*.markdown
./port-defs-to-markdown.py ${KERNEL} ${WEBSITE} \
	drivers/lego/brickpi/brickpi_ports_{in,out}.c \
	drivers/lego/ev3/legoev3_ports_{in,out}.c \
	drivers/lego/sensors/{ht_nxt_smux,ms_ev3_smux}.c \
	drivers/lego/wedo/wedo_port.c
