"""Fixture-topic/payload tests for the MQTT-message -> InfluxDB-point
mapping — no live broker or InfluxDB instance required.
"""

from logger.mapping import topic_to_point
from tests.fixtures import messages as fx


def test_tank_level_pct_maps_to_tank_measurement():
    point = topic_to_point(*fx.TANK_LEVEL_PCT)
    line = point.to_line_protocol()
    assert line.startswith("tank,id=fresh ")
    assert "level_pct=63.5" in line


def test_tank_status_maps_with_id_tag():
    point = topic_to_point(*fx.TANK_STATUS)
    line = point.to_line_protocol()
    assert line.startswith("tank,id=grey ")
    assert 'status="open_circuit"' in line


def test_tank_fluid_type_is_not_logged():
    assert topic_to_point(*fx.TANK_FLUID_TYPE) is None


def test_tank_capacity_l_is_not_logged():
    assert topic_to_point(*fx.TANK_CAPACITY_L) is None


def test_relay_state_true_maps_to_relay_measurement():
    point = topic_to_point(*fx.RELAY_STATE_ON)
    line = point.to_line_protocol()
    assert line.startswith("relay,id=lights ")
    assert "state=true" in line


def test_relay_state_false():
    point = topic_to_point(*fx.RELAY_STATE_OFF)
    line = point.to_line_protocol()
    assert line.startswith("relay,id=fan ")
    assert "state=false" in line


def test_battery_fields_map_to_battery_measurement():
    fixtures = [
        (fx.BATTERY_SOC_PCT, "soc_pct=87.2"),
        (fx.BATTERY_VOLTAGE_V, "voltage_v=13.1"),
        (fx.BATTERY_CURRENT_A, "current_a=-4.6"),
        (fx.BATTERY_POWER_W, "power_w=-60.3"),
        (fx.BATTERY_TEMPERATURE_C, "temperature_c=21.5"),
    ]
    for (topic, payload), expected_field in fixtures:
        point = topic_to_point(topic, payload)
        line = point.to_line_protocol()
        assert line.startswith("battery,id=house ")
        assert expected_field in line


def test_battery_charge_state_is_a_string_field():
    point = topic_to_point(*fx.BATTERY_CHARGE_STATE)
    line = point.to_line_protocol()
    assert line.startswith("battery,id=house ")
    assert 'charge_state="absorption"' in line


def test_unknown_domain_is_not_logged():
    assert topic_to_point(*fx.UNKNOWN_DOMAIN) is None


def test_malformed_topic_is_not_logged():
    assert topic_to_point(*fx.MALFORMED_TOPIC) is None
