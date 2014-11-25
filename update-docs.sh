#!/bin/bash

set -e

: ${KERNEL:=kernel}
: ${WEBSITE:=ev3dev.github.io}

drivers_docs_source="
	drivers/legoev3/dc_motor_class.c
	drivers/legoev3/ev3_analog_host.c
	drivers/legoev3/ev3_analog_sensor_core.c
	drivers/legoev3/ev3_input_port.c
	drivers/legoev3/ev3_output_port.c
	drivers/legoev3/ev3_tacho_motor.c
	drivers/legoev3/ev3_uart_host.c
	drivers/legoev3/ht_smux_i2c_host.c
	drivers/legoev3/ht_smux_i2c_sensor.c
	drivers/legoev3/ht_smux_input_port.c
	drivers/legoev3/legoev3_ports.c
	drivers/legoev3/legoev3_uart.c
	drivers/legoev3/nxt_analog_host.c
	drivers/legoev3/nxt_analog_sensor_core.c
	drivers/legoev3/msensor_class.c
	drivers/legoev3/nxt_i2c_host.c
	drivers/legoev3/nxt_i2c_sensor_core.c
	drivers/legoev3/rcx_led.c
	drivers/legoev3/rcx_motor.c
	drivers/legoev3/servo_motor_class.c
	drivers/legoev3/tacho_motor_class.c
	drivers/usb/misc/wedo/wedo_hub.c
"
drivers_docs_dest=${WEBSITE}/docs/drivers

rm -f ${drivers_docs_dest}/*.markdown

for in_file in ${drivers_docs_source}; do
	in_file=${KERNEL}/${in_file}
	out_file=${in_file##*/}
	out_file=${out_file//_core/}
	out_file=${out_file//_/-}
	out_file=${drivers_docs_dest}/${out_file/.*/.markdown}
	${KERNEL}/scripts/kernel-doc -text -function website ${in_file} | \
		./kernel-doc-text-to-markdown.py > ${out_file}
done

rm -f ${WEBSITE}/docs/sensors/*.markdown
./sensor-defs-to-markdown.py ${KERNEL}/drivers/legoev3/*_defs.c \
	${KERNEL}/drivers/usb/misc/wedo/wedo_sensor.c ${WEBSITE}
