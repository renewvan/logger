"""Fixture renewvan-bus (topic, payload) pairs, JSON-encoded scalars per the
driver publisher convention (see hub/driver-tank/driver_tank/driver.py:
`publisher.publish(topic, json.dumps(value))`).
"""

# Logged tank fields.
TANK_LEVEL_PCT = ("renewvan/tank/fresh/level_pct", "63.5")
TANK_STATUS = ("renewvan/tank/grey/status", '"open_circuit"')

# Excluded tank identity fields — static config, not time-series history.
TANK_FLUID_TYPE = ("renewvan/tank/fresh/fluid_type", '"fresh_water"')
TANK_CAPACITY_L = ("renewvan/tank/fresh/capacity_l", "95")

# Relay.
RELAY_STATE_ON = ("renewvan/relay/lights/state", "true")
RELAY_STATE_OFF = ("renewvan/relay/fan/state", "false")

# Battery.
BATTERY_SOC_PCT = ("renewvan/battery/house/soc_pct", "87.2")
BATTERY_VOLTAGE_V = ("renewvan/battery/house/voltage_v", "13.1")
BATTERY_CURRENT_A = ("renewvan/battery/house/current_a", "-4.6")
BATTERY_POWER_W = ("renewvan/battery/house/power_w", "-60.3")
BATTERY_TEMPERATURE_C = ("renewvan/battery/house/temperature_c", "21.5")
BATTERY_CHARGE_STATE = ("renewvan/battery/house/charge_state", '"absorption"')

# Unrecognized domain/topic shape.
UNKNOWN_DOMAIN = ("renewvan/climate/cabin/temperature_c", "22.0")
MALFORMED_TOPIC = ("renewvan/tank/fresh", "1")
