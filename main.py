import argparse
import json
from collections import defaultdict
from datetime import datetime, date
from typing import List, Optional, DefaultDict, Dict

from tabulate import tabulate


def parse_args(args=None) -> argparse:
    """
    Разбирает аргументы командной строки.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", nargs="+", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--date")
    return parser.parse_args(args)


def parse_date(timestamp_str: str) -> date:
    """
    Парсит метку времени из строки ISO в объект date.
    """
    dt = datetime.fromisoformat(timestamp_str)
    return dt.date()


def process_logs(
    file_paths: List[str], date_filter: Optional[date] = None
) -> DefaultDict[str, Dict]:
    """
    Обрабатывает один или несколько лог-файлов, возвращает статистику
    """
    stats = defaultdict(lambda: {"count": 0, "total_time": 0})
    for path in file_paths:
        with open(path, "r", encoding="UTF-8") as f:
            for line in f:
                log_entry = json.loads(line)
                timestamp_str = log_entry.get("@timestamp")
                if not timestamp_str:
                    continue
                if date_filter:
                    log_date = parse_date(timestamp_str)
                    if log_date != date_filter:
                        continue
                endpoint = log_entry.get("url")
                response_time = log_entry.get("response_time")
                if endpoint is None or response_time is None:
                    continue
                stats[endpoint]["count"] += 1
                stats[endpoint]["total_time"] += response_time
    return stats


def average_report(stats: DefaultDict[str, Dict]) -> None:
    """
    Формирует и выводит отчёт
    """
    table = []
    for endpoint, data in stats.items():
        avg_time = data["total_time"] / data["count"] if data["count"] else 0
        table.append([endpoint, data["count"], round(avg_time, 3)])
    headers = ["Endpoint", "Request Count", "Average Response Time"]
    print(tabulate(table, headers, tablefmt="grid"))


REPORTS = {
    "average": average_report,
}


def main() -> None:
    """
    Разбирает аргументы, обрабатывает логи, вызывает нужный отчёт.
    """
    args = parse_args()
    date_filter = None
    if args.date:
        try:
            date_filter = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"Неверный формат даты: {args.date}, ожидался YYYY-MM-DD")
            return

    stats = process_logs(file_paths=args.file, date_filter=date_filter)
    report_func = REPORTS.get(args.report)
    if report_func:
        report_func(stats)
    else:
        print(f"Отчёт {args.report} не найден.")


if __name__ == "__main__":
    main()
