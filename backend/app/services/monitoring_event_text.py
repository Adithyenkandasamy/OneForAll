"""Pure helpers shared by mock-data ingestion and future MQTT event processing."""

from __future__ import annotations

from typing import Any

REQUIRED_EVENT_FIELDS = {
    "event_id", "machine_id", "machine_name", "machine_type", "event_type",
    "severity", "timestamp", "description", "sensor_values", "detected_issue", "recommendation",
}


def validate_monitoring_event(event: dict[str, Any]) -> None:
    missing = REQUIRED_EVENT_FIELDS.difference(event)
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")
    if not isinstance(event["sensor_values"], dict):
        raise ValueError("sensor_values must be an object")
    for field in REQUIRED_EVENT_FIELDS - {"sensor_values"}:
        if not str(event[field]).strip():
            raise ValueError(f"{field} must not be empty")


def monitoring_event_to_text(event: dict[str, Any]) -> str:
    """Create semantic content without embedding raw telemetry JSON."""
    validate_monitoring_event(event)
    return "\n".join((
        f"Machine: {event['machine_id']} ({event['machine_name']}, {event['machine_type']})",
        f"Event: {event['event_type']}", f"Severity: {event['severity']}",
        f"Description: {event['description']}", f"Detected issue: {event['detected_issue']}",
        f"Recommendation: {event['recommendation']}",
    ))
