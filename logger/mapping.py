"""Pure mapping: renewvan/<domain>/<id>/<property> MQTT message -> InfluxDB point.

No network, no broker, no InfluxDB client — this is the seam the ticket's
acceptance criteria unit-test against fixture topics/payloads. The thin
MQTT/InfluxDB I/O adapters (subscriber.py, writer.py) call this and are not
unit-tested themselves (docs/porting pattern: seam is the pure function).

One InfluxDB measurement per entity type (tank/relay/battery/router), tagged by
`id` (the topic's <id> segment). Field whitelist per measurement below is
the single source of truth for what gets logged; `tank.fluid_type`/
`capacity_l` are deliberately absent — they're static identity config, not
time-series history, so a message for either property maps to no point.
"""

from __future__ import annotations

import json

from influxdb_client import Point

# measurement -> {property: value caster}. Absence from this map (wrong
# domain, wrong property, or malformed topic) means "don't log this".
_FIELDS: dict[str, dict[str, type]] = {
    "tank": {
        "level_pct": float,
        "status": str,
    },
    "relay": {
        "state": bool,
    },
    "battery": {
        "soc_pct": float,
        "voltage_v": float,
        "current_a": float,
        "power_w": float,
        "temperature_c": float,
        "charge_state": str,
    },
    "router": {
        "signal_rsrp_dbm": float,
        "signal_rsrq_db": float,
        "signal_sinr_db": float,
        "signal_rssi_dbm": float,
        "operator": str,
        "network_type": str,
        "uptime_s": float,
        "data_used_month_tx_b": float,
        "data_used_month_rx_b": float,
    },
}


def _decode(payload: str):
    """Decode an MQTT payload. Values are published JSON-encoded
    (json.dumps'd scalars, e.g. '"ok"', '12.3', 'true') per the driver
    publisher convention; fall back to the raw string for anything that
    isn't valid JSON.
    """
    try:
        return json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return payload


def topic_to_point(topic: str, payload: str) -> Point | None:
    """Map one renewvan-bus MQTT message to an InfluxDB `Point`, or `None` if
    this topic/property isn't logged (unknown domain/property, or an
    excluded tank identity field).
    """
    parts = topic.split("/")
    if len(parts) != 4 or parts[0] != "renewvan":
        return None
    _, domain, entity_id, prop = parts

    fields = _FIELDS.get(domain)
    if fields is None or prop not in fields:
        return None

    caster = fields[prop]
    value = _decode(payload)
    try:
        casted = caster(value)
    except (TypeError, ValueError):
        return None

    return Point(domain).tag("id", entity_id).field(prop, casted)
