# from lfx.field_typing import Data
from lfx.custom.custom_component.component import Component
from lfx.io import MessageTextInput, Output
from lfx.schema.data import Data

class MetricTrendTool(Component):
    display_name = "Metric Trend / Deviation Tool"
    description = (
        "Compare a metric's values across selected days (e.g. p99_ms) and "
        "calculate the deviation and trend (regression/improvement) between them. "
        "Must be used separately for each metric, e.g. p99_ms, error_rate, etc."
    )
    icon = "trending-up"
    name = "MetricTrendTool"

    inputs = [
        MessageTextInput(
            name="metric_name",
            display_name="Metric name",
            info="Name of the metric being compared, e.g. 'p99_ms'.",
            value="",
            tool_mode=True,
        ),
        MessageTextInput(
            name="values",
            display_name="Metric values",
            info="Comma-separated metric values in day order, e.g. '424.4, 918.9, 610.2'.",
            tool_mode=True,
        ),
        MessageTextInput(
            name="labels",
            display_name="Day labels",
            info="Optional comma-separated labels matching the values, e.g. '2026-07-23, 2026-07-24, 2026-07-25'.",
            value="",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(display_name="Output", name="output", method="analyze_trend"),
    ]

    def analyze_trend(self) -> Data:
        values = [float(v.strip()) for v in self.values.split(",") if v.strip()]

        labels = [l.strip() for l in self.labels.split(",") if l.strip()] if self.labels else []
        if len(labels) != len(values):
            labels = [f"Day {i + 1}" for i in range(len(values))]

        if len(values) < 2:
            return Data(data={"error": "Provide at least two values to compare."})

        # Higher value = regression, lower value = improvement (latency/error-rate style metrics)
        steps = []
        for i in range(1, len(values)):
            prev, curr = values[i - 1], values[i]
            delta = curr - prev
            percent_change = (delta / prev * 100) if prev else 0.0
            steps.append({
                "from": labels[i - 1],
                "to": labels[i],
                "delta": round(delta, 2),
                "percent_change": round(percent_change, 2),
                "direction": "regression" if delta > 0 else "improvement" if delta < 0 else "no change",
            })

        overall_delta = values[-1] - values[0]
        overall_percent = (overall_delta / values[0] * 100) if values[0] else 0.0

        return Data(data={
            "name": self.metric_name or "",
            "labels": labels,
            "values": values,
            "steps": steps,
            "overall_trend": {
                "from": labels[0],
                "to": labels[-1],
                "delta": round(overall_delta, 2),
                "percent_change": round(overall_percent, 2),
                "direction": "regression" if overall_delta > 0 else "improvement" if overall_delta < 0 else "no change",
            },
            "average_value": round(sum(values) / len(values), 2),
            "max_value": max(values),
            "min_value": min(values),
        })
