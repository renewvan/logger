"""Config sourced entirely from environment variables — matches `hub`'s
`docker-compose-truenas.yml` `logger:` service block, the single contract
between this repo and the deployment manifest.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class MqttConfig:
    host: str
    port: int
    username: str | None
    password: str | None


@dataclass(frozen=True)
class InfluxConfig:
    url: str
    token: str
    org: str
    bucket: str


@dataclass(frozen=True)
class AppConfig:
    mqtt: MqttConfig
    influx: InfluxConfig


def load_config() -> AppConfig:
    return AppConfig(
        mqtt=MqttConfig(
            host=os.environ.get("MQTT_HOST", "mosquitto"),
            port=int(os.environ.get("MQTT_PORT", "1883")),
            username=os.environ.get("MQTT_USERNAME") or None,
            password=os.environ.get("MQTT_PASSWORD") or None,
        ),
        influx=InfluxConfig(
            url=os.environ["INFLUXDB_URL"],
            token=os.environ["INFLUXDB_TOKEN"],
            org=os.environ["INFLUXDB_ORG"],
            bucket=os.environ["INFLUXDB_BUCKET"],
        ),
    )
