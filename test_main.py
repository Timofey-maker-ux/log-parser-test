import json
from datetime import date
from collections import defaultdict
import pytest

from main import process_logs, average_report, parse_args


@pytest.mark.parametrize(
    "logs, date_filter, expected",
    [
        (
            [
                {
                    "@timestamp": "2025-06-22T13:00:00+00:00",
                    "url": "/a",
                    "response_time": 0.1,
                },
                {
                    "@timestamp": "2025-06-22T14:00:00+00:00",
                    "url": "/a",
                    "response_time": 0.2,
                },
                {
                    "@timestamp": "2025-06-23T10:00:00+00:00",
                    "url": "/b",
                    "response_time": 0.3,
                },
            ],
            None,
            {
                "/a": {"count": 2, "total_time": 0.3},
                "/b": {"count": 1, "total_time": 0.3},
            },
        ),
        (
            [
                {
                    "@timestamp": "2025-06-22T13:00:00+00:00",
                    "url": "/a",
                    "response_time": 0.1,
                },
                {
                    "@timestamp": "2025-06-22T14:00:00+00:00",
                    "url": "/a",
                    "response_time": 0.2,
                },
                {
                    "@timestamp": "2025-06-23T10:00:00+00:00",
                    "url": "/b",
                    "response_time": 0.3,
                },
            ],
            date(2025, 6, 22),
            {
                "/a": {"count": 2, "total_time": 0.3},
            },
        ),
    ],
)
def test_process_logs(tmp_path, logs, date_filter, expected):
    file_path = tmp_path / "test.log"
    with open(file_path, "w", encoding="utf-8") as f:
        for entry in logs:
            f.write(json.dumps(entry) + "\n")

    result = process_logs([str(file_path)], date_filter=date_filter)
    result_dict = {
        k: {"count": v["count"], "total_time": round(v["total_time"], 1)}
        for k, v in result.items()
    }
    assert result_dict == expected


def test_average_report_output(capsys):
    stats = defaultdict(lambda: {"count": 0, "total_time": 0.0})
    stats["/endpoint1"]["count"] = 3
    stats["/endpoint1"]["total_time"] = 0.9
    stats["/endpoint2"]["count"] = 2
    stats["/endpoint2"]["total_time"] = 0.4

    average_report(stats)

    captured = capsys.readouterr()
    output = captured.out

    assert "/endpoint1" in output
    assert "/endpoint2" in output
    assert "0.3" in output
    assert "0.2" in output


def test_parse_args():
    test_args = [
        "--file",
        "log1.log",
        "log2.log",
        "--report",
        "average",
        "--date",
        "2025-06-22",
    ]
    args = parse_args(test_args)

    assert args.file == ["log1.log", "log2.log"]
    assert args.report == "average"
    assert args.date == "2025-06-22"
