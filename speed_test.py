#!/usr/bin/env python3
"""Measure download speed with ten sequential HTTP(S) requests."""

from __future__ import annotations

import argparse
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REQUEST_COUNT = 10
CHUNK_SIZE = 64 * 1024


def download_once(url: str, timeout: float, request_number: int) -> tuple[int, float]:
    """Download one complete response body and return its size and duration."""
    request = Request(url, headers={"User-Agent": "internet-speed-test/1.0"})
    started = time.perf_counter()
    byte_count = 0

    with urlopen(request, timeout=timeout) as response:
        while chunk := response.read(CHUNK_SIZE):
            byte_count += len(chunk)

    elapsed = time.perf_counter() - started
    print(f"Запрос {request_number:2}: {byte_count:,} байт за {elapsed:.3f} с")
    return byte_count, elapsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Последовательно скачивает один URL 10 раз и измеряет скорость."
    )
    parser.add_argument("url", help="HTTP(S)-адрес ресурса для скачивания")
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="тайм-аут каждого запроса в секундах (по умолчанию: 30)",
    )
    args = parser.parse_args()

    if not args.url.startswith(("http://", "https://")):
        parser.error("адрес должен начинаться с http:// или https://")
    if args.timeout <= 0:
        parser.error("тайм-аут должен быть больше нуля")
    return args


def main() -> int:
    args = parse_args()
    total_bytes = 0
    total_seconds = 0.0

    print(f"Адрес: {args.url}")
    print(f"Выполняю {REQUEST_COUNT} последовательных запросов…")

    try:
        for request_number in range(1, REQUEST_COUNT + 1):
            byte_count, elapsed = download_once(args.url, args.timeout, request_number)
            total_bytes += byte_count
            total_seconds += elapsed
    except HTTPError as error:
        print(f"HTTP-ошибка при запросе {request_number}: {error}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError, OSError) as error:
        print(f"Ошибка при запросе {request_number}: {error}", file=sys.stderr)
        return 1

    average_seconds = total_seconds / REQUEST_COUNT
    bytes_per_second = total_bytes / total_seconds if total_seconds else 0.0
    megabytes_per_second = bytes_per_second / 1_000_000
    megabits_per_second = bytes_per_second * 8 / 1_000_000

    print("\nИтог:")
    print(f"Среднее время запроса: {average_seconds:.3f} с")
    print(f"Всего скачано: {total_bytes:,} байт ({total_bytes / 1_000_000:.3f} MB)")
    print(f"Средняя скорость скачивания: {megabytes_per_second:.3f} MB/s")
    print(f"То же в битах: {megabits_per_second:.3f} Mbps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
