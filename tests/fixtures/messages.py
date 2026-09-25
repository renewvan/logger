"""Fixture van-bus (topic, payload) pairs, JSON-encoded scalars per the
driver publisher convention (see hub/driver-tank/driver_tank/driver.py:
`publisher.publish(topic, json.dumps(value))`).
"""

# Logged tank fields.
TANK_LEVEL_PCT = ("van/tank/fresh/level_pct", "63.5")
TANK_STATUS = ("van/tank/grey/status", '"open_circuit"')

# Excluded tank identity fields — static config, not time-series history.
TANK_FLUID_TYPE = ("van/tank/fresh/fluid_type", '"fresh_water"')
TANK_CAPACITY_L = ("van/tank/fresh/capacity_l", "95")

# Relay.
RELAY_STATE_ON = ("van/relay/lights/state", "true")
RELAY_STATE_OFF = ("van/relay/fan/state", "false")

# Battery.
BATTERY_SOC_PCT = ("van/battery/house/soc_pct", "87.2")
BATTERY_VOLTAGE_V = ("van/battery/house/voltage_v", "13.1")
BATTERY_CURRENT_A = ("van/battery/house/current_a", "-4.6")
BATTERY_POWER_W = ("van/battery/house/power_w", "-60.3")
BATTERY_TEMPERATURE_C = ("van/battery/house/temperature_c", "21.5")
BATTERY_CHARGE_STATE = ("van/battery/house/charge_state", '"absorption"')

# Unrecognized domain/topic shape.
UNKNOWN_DOMAIN = ("van/climate/cabin/temperature_c", "22.0")
MALFORMED_TOPIC = ("van/tank/fresh", "1")
