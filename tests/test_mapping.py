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


def test_cleared_retained_topic_is_not_logged():
    # A device clears a retained topic with an empty payload when a reading stops being valid
    # (e.g. Venus sends null for charge_state). That means "no value", not a data point.
    assert topic_to_point("renewvan/battery/290/charge_state", "") is None
    assert topic_to_point("renewvan/battery/290/soc_pct", "") is None


def test_battery_optional_time_fields_are_logged():
    point = topic_to_point("renewvan/battery/290/time_since_full_charge_s", "169036")
    assert point.to_line_protocol().startswith("battery,id=290 ")
    assert "time_since_full_charge_s=169036" in point.to_line_protocol()
    point = topic_to_point("renewvan/battery/290/time_to_go_s", "98400.0")
    assert "time_to_go_s=98400" in point.to_line_protocol()


def test_solar_fields_map_to_solar_measurement():
    fixtures = [
        ("power_w", "14.0", "power_w=14"),
        ("battery_voltage_v", "13.44", "battery_voltage_v=13.44"),
        ("battery_current_a", "1.4", "battery_current_a=1.4"),
        ("pv_voltage_v", "47.5", "pv_voltage_v=47.5"),
        ("pv_current_a", "0.3", "pv_current_a=0.3"),
        ("yield_today_wh", "120.0", "yield_today_wh=120"),
    ]
    for prop, payload, expected_field in fixtures:
        line = topic_to_point(f"renewvan/solar/291/{prop}", payload).to_line_protocol()
        assert line.startswith("solar,id=291 ")
        assert expected_field in line
    line = topic_to_point("renewvan/solar/291/charge_state", '"bulk"').to_line_protocol()
    assert 'charge_state="bulk"' in line


def test_charger_fields_map_to_charger_measurement():
    fixtures = [
        ("voltage_v", "13.39", "voltage_v=13.39"),
        ("current_a", "18.2", "current_a=18.2"),
        ("power_w", "243", "power_w=243"),
        ("input_voltage_v", "12.54", "input_voltage_v=12.54"),
    ]
    for prop, payload, expected_field in fixtures:
        line = topic_to_point(f"renewvan/charger/288/{prop}", payload).to_line_protocol()
        assert line.startswith("charger,id=288 ")
        assert expected_field in line
    for prop, payload in [("source", '"alternator"'), ("charge_state", '"absorption"')]:
        line = topic_to_point(f"renewvan/charger/288/{prop}", payload).to_line_protocol()
        assert f'{prop}="' in line


def test_router_signal_fields_map_to_router_measurement():
    fixtures = [
        (fx.ROUTER_SIGNAL_RSRP_DBM, "signal_rsrp_dbm=-85"),
        (fx.ROUTER_SIGNAL_RSRQ_DB, "signal_rsrq_db=-10"),
        (fx.ROUTER_SIGNAL_SINR_DB, "signal_sinr_db=6"),
        (fx.ROUTER_SIGNAL_RSSI_DBM, "signal_rssi_dbm=-54"),
        (fx.ROUTER_UPTIME_S, "uptime_s=826671"),
        (fx.ROUTER_DATA_TX_B, "data_used_month_tx_b=140194858"),
        (fx.ROUTER_DATA_RX_B, "data_used_month_rx_b=385092522"),
    ]
    for (topic, payload), expected_field in fixtures:
        point = topic_to_point(topic, payload)
        line = point.to_line_protocol()
        assert line.startswith("router,id=main ")
        assert expected_field in line


def test_router_operator_and_network_type_are_string_fields():
    for (topic, payload), expected in [
        (fx.ROUTER_OPERATOR, 'operator="26203"'),
        (fx.ROUTER_NETWORK_TYPE, 'network_type="lte"'),
    ]:
        point = topic_to_point(topic, payload)
        line = point.to_line_protocol()
        assert line.startswith("router,id=main ")
        assert expected in line


def test_router_raw_payload_is_not_logged():
    assert topic_to_point(*fx.ROUTER_RAW) is None


def test_unknown_domain_is_not_logged():
    assert topic_to_point(*fx.UNKNOWN_DOMAIN) is None


def test_malformed_topic_is_not_logged():
    assert topic_to_point(*fx.MALFORMED_TOPIC) is None


# --- demo namespace -----------------------------------------------------------------------------
# The hub's simulated van is published under `renewvan/demo/...`, i.e. INSIDE the `renewvan/#`
# subscription this logger holds (hub docs/demo-mode.md). Nothing simulated may ever be written to
# InfluxDB: it would sit in the real van's history next to real readings.


def _logged_properties():
    from logger.mapping import _FIELDS

    return [(domain, prop) for domain, props in _FIELDS.items() for prop in props]


def test_every_logged_property_is_dropped_under_the_demo_namespace():
    """Derived from the logger's own field table, so a newly logged property is covered too."""
    cases = _logged_properties()
    assert cases, "the logger logs at least one property"
    for domain, prop in cases:
        for payload in ("1", "true", '"ok"', "12.5"):
            assert topic_to_point(f"renewvan/demo/{domain}/house/{prop}", payload) is None, (
                domain,
                prop,
            )


def test_the_demo_switch_and_health_topics_are_not_logged():
    for topic in (
        "renewvan/demo/enabled",
        "renewvan/demo/enabled/set",
        "renewvan/demo/health",
        "renewvan/demo/router/health",
    ):
        assert topic_to_point(topic, "true") is None, topic


def test_demo_is_not_a_logged_domain():
    """A real entity whose domain slot said `demo` would otherwise be a four-segment match."""
    from logger.mapping import _FIELDS

    assert "demo" not in _FIELDS
    assert topic_to_point("renewvan/demo/level_pct", "50") is None
