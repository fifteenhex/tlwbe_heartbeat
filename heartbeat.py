#!/usr/bin/env python3

import argparse
import serial
from tlwpy.rak811 import Rak811
import asyncio
from tlwpy.tlwbe import Tlwbe, Uplink, Result
from tlwpy.gwctrl import Gateway
from tlwpy.pktfwdbr import PacketForwarder
import logging
from daemonize import Daemonize

HEARTBEAT_INTERVAL = 5 * 30
UPLINK_TIMEOUT = 20
RETRY_INTERVAL = 10


async def send_ping(tlwbe: Tlwbe, app_eui: str, dev_eui: str):
    counter = 0
    failures = 0
    while True:
        rak811.get_frame_counters()
        rak811.get_status()
        logger.info('sending heartbeat')
        rak811.send(1, bytearray('%08x' % counter, 'utf-8'))
        counter += 1
        try:
            msg: Uplink = await asyncio.wait_for(tlwbe.queue_uplinks.get(), UPLINK_TIMEOUT)
            failures = 0
            logger.info('got uplink for heartbeat; rssi was %s' % msg.rfparams.get('rssi'))

            try:
                await tlwbe.send_downlink(app_eui, dev_eui, 1, b'hello')
            except asyncio.futures.TimeoutError:
                pass

            await asyncio.sleep(HEARTBEAT_INTERVAL)
        except asyncio.futures.TimeoutError:
            failures += 1
            logger.info('didn\'t see uplink from tlwbe, failed %d times so far, will try again in %ds'
                        % (failures, RETRY_INTERVAL))
            await asyncio.sleep(RETRY_INTERVAL)


async def main():
    tlwbe = Tlwbe(args.mqtthost)
    gwctrl = Gateway(args.mqtthost, args.gateway)
    pktfwdr = PacketForwarder(args.mqtthost)

    await tlwbe.wait_for_connection()
    await gwctrl.wait_for_connection()
    await pktfwdr.wait_for_connection()

    appeui = args.appeui
    if appeui is None:
        appeui = tlwbe.get_app_by_name(args.appname)

    deveui = args.deveui
    if deveui is None:
        tlwbe.get_dev_by_name(args.devname)

    assert appeui is not None and deveui is not None

    tlwbe.listen_for_joins(appeui, deveui)
    tlwbe.listen_for_uplinks(appeui, deveui, 1)

    logger.info('joining...')
    rak811.join()
    try:
        msg = await asyncio.wait_for(tlwbe.queue_joins.get(), timeout=30)
    except asyncio.futures.TimeoutError:
        logger.warning('join failed')
        return
    logger.info('joined')
    rak811.get_signal()

    rak811.get_channel_list()

    result: Result = await tlwbe.get_dev_by_eui(deveui)
    logger.debug('dev address is %s' % result.result)

    await asyncio.gather(send_ping(tlwbe, appeui, deveui))


parser = argparse.ArgumentParser()
parser.add_argument('--serialport', type=str, required=True)
parser.add_argument('--mqtthost', type=str, required=True)
parser.add_argument('--gateway', type=str, required=True)
parser.add_argument('--appname', type=str)
parser.add_argument('--appeui', type=str)
parser.add_argument('--devname', type=str)
parser.add_argument('--deveui', type=str)
parser.add_argument('--daemonize', action='store_true', default=False)

args = parser.parse_args()

if args.appname is None and args.appeui is None:
    print("need the app name or eui")
    exit(1)

if args.devname is None and args.deveui is None:
    print("need the dev name or eui")
    exit(1)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('heartbeat')

ser = serial.Serial(args.serialport, 115200, timeout=10)  # open serial port
rak811 = Rak811(ser)

rak811.reset()
rak811.get_version()
rak811.get_rx1_delay()
rak811.get_rx2()

pid = '/var/run/heartbeat/heartbeat.pid'


def entry():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('dying..')
    ser.close()


if args.daemonize:
    daemon = Daemonize(app="heartbeat", pid=pid, action=entry)
    daemon.start()
else:
    entry()
