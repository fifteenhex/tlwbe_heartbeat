import paho.mqtt.client as mqtt
from uuid import uuid4
import json
from asyncio import Queue

TOPIC_DEV_GET = 'tlwbe/control/dev/get'
TOPIC_APP_GET = 'tlwbe/control/app/get'


class Join:
    pass


class Uplink:
    pass


class Tlwbe:
    __slots__ = ['queue_joins', 'queue_uplinks', 'mqtt_client']

    def __dump_message(self, msg):
        print(msg.topic)

    def _on_sub(self, client, userdata, mid, granted_qos):
        print("subbed")

    def __on_msg(self, client, userdata, msg):
        self.__dump_message(msg)
        print('rogue publish')

    def __on_join(self, client, userdata, msg):
        self.__dump_message(msg)
        self.queue_joins.put_nowait(msg)

    def __on_uplink(self, client, userdata, msg):
        self.__dump_message(msg)
        self.queue_uplinks.put_nowait(msg)

    def __init__(self, host: str):
        self.queue_joins = Queue()
        self.queue_uplinks = Queue()
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(host)
        self.mqtt_client.message_callback_add('tlwbe/join/+/+', self.__on_join)
        self.mqtt_client.message_callback_add('tlwbe/uplink/#', self.__on_uplink)
        self.mqtt_client.on_message = self.__on_msg
        self.mqtt_client.on_subscribe = self._on_sub
        self.mqtt_client.subscribe("tlwbe/control/result/#")

    def loop(self):
        self.mqtt_client.loop_forever(retry_first_connection=True)

    def __publish_and_wait_for_result(self, topic: str, payload: dict):
        token = str(uuid4())
        self.mqtt_client.publish("%s/%s" % (topic, token), json.dumps(payload))

    def __sub_to_topic(self, topic: str):
        print('subscribing to %s' % topic)
        self.mqtt_client.subscribe(topic)

    def get_dev_by_name(self, name: str):
        payload = {'name': name}
        self.__publish_and_wait_for_result(TOPIC_DEV_GET, payload)

    def get_dev_by_eui(self, eui: str):
        payload = {'eui': eui}
        self.__publish_and_wait_for_result(TOPIC_DEV_GET, payload)

    def get_app_by_name(self, name: str):
        payload = {'name': name}
        self.__publish_and_wait_for_result(TOPIC_APP_GET, payload)

    def get_app_by_eui(self, eui: str):
        payload = {'eui': eui}
        self.__publish_and_wait_for_result(TOPIC_APP_GET, payload)

    def listen_for_joins(self, appeui: str, deveui: str):
        self.__sub_to_topic('tlwbe/join/%s/%s' % (appeui, deveui))

    def listen_for_uplinks(self, appeui: str, deveui: str, port: int):
        self.__sub_to_topic('tlwbe/uplink/%s/%s/%d' % (appeui, deveui, port))
