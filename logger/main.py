#!/usr/bin/env python3
"""renewvan/logger entrypoint."""
from __future__ import annotations

import argparse
import logging

from logger.config import load_config
from logger.subscriber import Subscriber
from logger.writer import Writer


def main() -> None:
    parser = argparse.ArgumentParser(description="renewvan/logger: renewvan/# -> InfluxDB point writer")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
    )

    config = load_config()
    writer = Writer(config.influx)
    subscriber = Subscriber(config.mqtt, writer)
    try:
        subscriber.run_forever()
    finally:
        writer.close()


if __name__ == "__main__":
    main()
