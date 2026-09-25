"""Thin wrapper around the InfluxDB client — the adapter half of the
mapping/adapter seam (see mapping.py). Not unit-tested; a real/dockerized
InfluxDB instance is a manual/smoke check, not a unit-test target.
"""
from __future__ import annotations

import logging

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from logger.config import InfluxConfig

logger = logging.getLogger(__name__)


class Writer:
    def __init__(self, config: InfluxConfig) -> None:
        self._bucket = config.bucket
        self._client = InfluxDBClient(url=config.url, token=config.token, org=config.org)
        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)

    def write(self, point: Point) -> None:
        self._write_api.write(bucket=self._bucket, record=point)

    def close(self) -> None:
        self._write_api.close()
        self._client.close()
