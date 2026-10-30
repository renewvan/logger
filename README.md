# logger

`renewvan/#` → InfluxDB point writer for the renewvan hub. Subscribes every
topic on the renewvan bus and writes one InfluxDB point per MQTT message
received — no fixed-interval sampling, no downsampling, no batching/rollup
logic. Per `hub/.scratch/renewvan-hub-v0-build/issues/05-influxdb-logger.md`.

## Mapping

One InfluxDB measurement per entity type (`tank`, `relay`, `battery`,
`solar`, `charger`, `router`, `temperature`), tagged by `id` (the topic's
`<id>` path segment):

| Measurement | Fields logged |
|---|---|
| `tank` | `level_pct`, `status` |
| `relay` | `state` |
| `battery` | `soc_pct`, `voltage_v`, `current_a`, `power_w`, `temperature_c`, `charge_state` |
| `temperature` | `temperature_c`, `status` |

`tank.fluid_type`/`capacity_l` and `temperature.unit` (a display
preference, C/F) are **not** logged as time-series points —
they're static identity config, not history.
Any other topic (unrecognized domain, unrecognized property, malformed
topic shape) is silently dropped.

The MQTT-message → InfluxDB-point mapping lives in `logger/mapping.py` as
a pure function (no network, no broker, no InfluxDB client) — this is
what `tests/test_mapping.py` exercises against fixture topics/payloads,
no live broker or InfluxDB instance required.

## Configuration

All config is environment variables (matches `hub`'s
`docker-compose-truenas.yml` `logger:` service block):

| Variable | Default | Notes |
|---|---|---|
| `MQTT_HOST` | `mosquitto` | Renewvan bus broker |
| `MQTT_PORT` | `1883` | |
| `MQTT_USERNAME` | _(none)_ | |
| `MQTT_PASSWORD` | _(none)_ | |
| `INFLUXDB_URL` | _(required)_ | e.g. `http://influxdb:8086` |
| `INFLUXDB_TOKEN` | _(required)_ | |
| `INFLUXDB_ORG` | _(required)_ | `renewvan` in the reference deployment |
| `INFLUXDB_BUCKET` | _(required)_ | `van` in the reference deployment |

Writes into the already-provisioned InfluxDB 2 instance (org `renewvan`,
bucket `van`) — this repo never creates a bucket or retention policy.

## Running

```bash
pip install -r requirements.txt
INFLUXDB_URL=http://localhost:8086 \
INFLUXDB_TOKEN=... \
INFLUXDB_ORG=renewvan \
INFLUXDB_BUCKET=van \
python -m logger.main
```

## Testing

```bash
pip install -r requirements.txt -r requirements-test.txt
pytest tests/ -v
```

Mapping tests run with fixture topics/payloads only — no MQTT broker or
InfluxDB instance required.

## Releasing

Start a release from **Actions → Release → Run workflow**, or
`gh workflow run release.yml -f bump=minor` (`patch`, `major`, or `-f version=0.2.0`
to set it explicitly). One run works out the next version from the latest `v*` tag,
tags `main`, creates the GitHub release and builds and publishes
`ghcr.io/<owner>/logger:<tag>` (and `:latest`), which `hub`'s deployment compose
file pins by tag (never builds from source — see
`hub/docs/adr/0001-compose-services-via-pinned-images-not-git-submodules.md`).

A beta from a feature branch: dispatch the workflow on that branch with **prerelease**
ticked. It runs the tests, publishes only its own tag (never `:latest`) and writes nothing
to `main`. The process is shared by every renewvan repo and lives in `hub` (`hub/docs/adr/0015-one-release-process-via-reusable-workflows.md`);
this repo's `release.yml` only says what it ships.
