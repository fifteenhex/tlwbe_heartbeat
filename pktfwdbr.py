import paho.mqtt.client as mqtt
import logging
import base64
import lorawan
import json
import asyncio
from mqttbase import MqttBase


class PacketForwarder(MqttBase):
    __slots__ = ['uplinks', '__logger', '__mqtt_client']

    def __on_rx(self, client, userdata, msg: mqtt.MQTTMessage):
        payload_json = json.loads(msg.payload)
        pkt_data = base64.b64decode(payload_json['data'])

        pkt_type = lorawan.get_packet_type(pkt_data)
        if pkt_type == lorawan.MHDR_MTYPE_CNFUP or pkt_type == lorawan.MHDR_MTYPE_UNCNFUP:
            self.__logger.debug('saw uplink')
            self.uplinks.put_nowait(lorawan.Uplink(pkt_data))

    def __init__(self, host: str):
        super().__init__(host)
        self.uplinks = asyncio.Queue()
        rx_topic = 'pktfwdbr/+/rx/#'
        self.__logger = logging.getLogger('pktfwdbr')
        self.mqtt_client.message_callback_add(rx_topic, self.__on_rx)
        self.mqtt_client.subscribe(rx_topic)

    def reset(self):
        pass
