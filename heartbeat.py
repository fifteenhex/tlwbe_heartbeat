#!/usr/bin/env python3

import argparse
import serial
from rak811 import Rak811
import asyncio
from tlwbe import Tlwbe


async def send_ping():
    counter = 0
    while True:
        rak811.send(1, bytearray('%08x' % counter, 'utf-8'))
        counter += 1
        await asyncio.sleep(30)


async def check_ping(tlwbe: Tlwbe):
    while True:
        msg = await tlwbe.queue_uplinks.get()


async def main():
    tlwbe = Tlwbe(args.mqtthost)
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, tlwbe.loop)

    appeui = args.appeui
    if appeui is None:
        appeui = tlwbe.get_app_by_name(args.appname)

    deveui = args.deveui
    if deveui is None:
        tlwbe.get_dev_by_name(args.devname)

    assert appeui is not None and deveui is not None

    tlwbe.listen_for_joins(appeui, deveui)
    tlwbe.listen_for_uplinks(appeui, deveui, 1)

    rak811.join()
    msg = await asyncio.wait_for(tlwbe.queue_joins.get(), timeout=30)
    print(msg)

    await asyncio.gather(send_ping(), check_ping(tlwbe))


parser = argparse.ArgumentParser()
parser.add_argument('--serialport', type=str, required=True)
parser.add_argument('--mqtthost', type=str, required=True)
parser.add_argument('--appname', type=str)
parser.add_argument('--appeui', type=str)
parser.add_argument('--devname', type=str)
parser.add_argument('--deveui', type=str)

args = parser.parse_args()

if args.appname is None and args.appeui is None:
    print("name the app name or eui")
    exit(1)

if args.devname is None and args.deveui is None:
    print("name the dev name or eui")
    exit(1)

ser = serial.Serial(args.serialport, 115200, timeout=30)  # open serial port
rak811 = Rak811(ser)

rak811.get_version()

asyncio.run(main())

ser.close()  # close port
