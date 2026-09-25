"""Persistent MQTT subscription on `van/#`: every message received is run
through `mapping.topic_to_point` and, if it maps to a point, written
immediately — no sampling, no batching. Thin I/O adapter around paho-mqtt;
not unit-tested (see mapping.py for the tested seam).
"""
from __future__ import annotations

import logging

import paho.mqtt.client as mqtt

from logger.config import MqttConfig
from logger.mapping import topic_to_point
from logger.writer import Writer

logger = logging.getLogger(__name__)

VAN_BUS_WILDCARD = "van/#"


class Subscriber:
    def __init__(self, config: MqttConfig, writer: Writer) -> None:
        self._config = config
        self._writer = writer
        self._client = mqtt.Client(client_id="renewvan-logger", clean_session=False)
        if config.username:
            self._client.username_pw_set(config.username, config.password)
        self._client.reconnect_delay_set(min_delay=1, max_delay=30)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):  # noqa: ANN001
        if rc == 0:
            logger.info("Connected to MQTT broker %s:%s", self._config.host, self._config.port)
            client.subscribe(VAN_BUS_WILDCARD, qos=1)
        else:
            logger.error("MQTT connect failed with rc=%s", rc)

    def _on_message(self, client, userdata, msg):  # noqa: ANN001
        payload = msg.payload.decode("utf-8")
        point = topic_to_point(msg.topic, payload)
        if point is None:
            return
        try:
            self._writer.write(point)
        except Exception:
            logger.exception("InfluxDB write failed for topic=%s", msg.topic)

    def run_forever(self) -> None:
        self._client.connect(self._config.host, self._config.port)
        self._client.loop_forever()
