import paho.mqtt.client as mqtt
import logging


class Gateway:
    __slots__ = ['__logger', '__mqtt_client']

    def __on_heartbeat(self, client, userdata, msg):
        self.__logger.debug("saw gateway heartbeat")

    def __init__(self, mqtt_host: str, gw_name: str):
        heartbeat_topic = 'gwctrl/%s/heartbeat' % gw_name
        self.__logger = logging.getLogger('gwctrl')
        self.__mqtt_client = mqtt.Client()
        self.__mqtt_client.message_callback_add(heartbeat_topic, self.__on_heartbeat)
        self.__mqtt_client.connect(mqtt_host)
        self.__mqtt_client.subscribe(heartbeat_topic)

    def loop(self):
        self.__mqtt_client.loop_forever(retry_first_connection=True)

    def reboot(self):
        pass
