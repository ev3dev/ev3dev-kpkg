#!/bin/bash

set -e

: ${KERNEL:=kernel}
: ${WEBSITE:=ev3dev.github.io}

drivers_docs_source="
	drivers/lego/core/lego_port_class.c
	drivers/lego/ev3/legoev3_ports_core.c
	drivers/lego/ev3/legoev3_ports_in.c
	drivers/lego/ev3/legoev3_ports_out.c
	drivers/lego/motors/dc_motor_class.c
	drivers/lego/motors/ev3_tacho_motor.c
	drivers/lego/motors/rcx_led.c
	drivers/lego/motors/rcx_motor.c
	drivers/lego/motors/servo_motor_class.c
	drivers/lego/motors/tacho_motor_class.c
	drivers/lego/sensors/ev3_analog_sensor_core.c
	drivers/lego/sensors/ev3_uart_sensor_ld.c
	drivers/lego/sensors/ht_nxt_smux.c
	drivers/lego/sensors/ht_nxt_smux_i2c_sensor.c
	drivers/lego/sensors/lego_sensor_class.c
	drivers/lego/sensors/ms_ev3_smux.c
	drivers/lego/sensors/nxt_analog_sensor_core.c
	drivers/lego/sensors/nxt_i2c_sensor_core.c
	drivers/lego/wedo/wedo_hub.c
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
./sensor-defs-to-markdown.py ${KERNEL}/drivers/lego/sensors/*_defs.c \
	${KERNEL}/drivers/lego/wedo/wedo_{hub,sensor}.c ${WEBSITE}

rm -f ${WEBSITE}/docs/ports/*.markdown
./port-defs-to-markdown.py ${KERNEL}/drivers/lego/ev3/legoev3_ports_{in,out}.c \
	${KERNEL}/drivers/lego/sensors/{ht_nxt_smux,ms_ev3_smux}.c \
	${KERNEL}/drivers/lego/wedo/wedo_port.c ${WEBSITE}
