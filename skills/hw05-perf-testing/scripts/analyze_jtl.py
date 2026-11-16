#!/usr/bin/env python3
"""
analyze_jtl.py — HW05 Agent Skill
Phân tích file .jtl của JMeter, tính các metrics chuẩn và xuất Markdown report.

Dùng để:
  1. Lấy số liệu thực tế sau khi chạy test
  2. So sánh với AI analysis để hunt misinterpretations

JTL format (CSV): timeStamp,elapsed,label,responseCode,responseMessage,
                  threadName,dataType,success,failureMessage,bytes,
                  sentBytes,grpThreads,allThreads,URL,Latency,
                  IdleTime,Connect

Usage:
  python analyze_jtl.py --file ../../results/load/XXXXXXXX_Load_20261116.jtl
  python analyze_jtl.py --file ../../results/load/XXXXXXXX_Load_20261116.jtl --per-label
"""
import csv
import argparse
import os
import statistics
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def percentile(sorted_data: list, pct: float) -> float:
    """Tính percentile theo phương pháp nearest-rank (giống JMeter)."""
    if not sorted_data:
        return 0.0
    idx = max(0, int(len(sorted_data) * pct / 100) - 1)
    return sorted_data[idx]


def parse_jtl(jtl_path: str) -> dict:
    """
    Parse file .jtl và trả về dict gồm:
      - 'all'    : metrics tổng hợp cho toàn bộ file
      - 'labels' : dict[label_name] -> metrics per sampler
    """
    rows_by_label = defaultdict(list)
    all_rows      = []

    with open(jtl_path, newline="", encoding="utf-8") as f:
        # Thử detect delimiter
        sample = f.read(1024)
        f.seek(0)
        delimiter = "," if "," in sample else "\t"
        
        reader = csv.DictReader(f, delimiter=delimiter)
        
        for row in reader:
            try:
                elapsed   = int(row.get("elapsed", 0) or 0)
                ts        = int(row.get("timeStamp", 0) or 0)
                success   = str(row.get("success", "true")).strip().lower() == "true"
                label     = str(row.get("label", "unknown")).strip()
                resp_code = str(row.get("responseCode", "")).strip()
                latency   = int(row.get("Latency", 0) or 0)
                connect   = int(row.get("Connect", 0) or 0)
                
                entry = {
                    "elapsed":   elapsed,
                    "ts":        ts,
                    "success":   success,
                    "label":     label,
                    "resp_code": resp_code,
                    "latency":   latency,
                    "connect":   connect,
                }
                all_rows.append(entry)
                rows_by_label[label].append(entry)
            except (ValueError, KeyError):
                continue   # skip malformed rows

    def compute_metrics(rows: list, name: str = "ALL") -> dict:
        if not rows:
            return {}
        
        latencies  = sorted([r["elapsed"] for r in rows])
        timestamps = [r["ts"] for r in rows]
        errors     = [r for r in rows if not r["success"]]
        
        start_ts   = min(timestamps)
        end_ts     = max(timestamps)
        duration_s = max((end_ts - start_ts) / 1000.0, 1.0)
        
        return {
            "name":            name,
            "total":           len(rows),
            "errors":          len(errors),
            "error_rate_pct":  round(len(errors) / len(rows) * 100, 2),
            "throughput_rps":  round(len(rows) / duration_s, 2),
            "duration_s":      round(duration_s, 1),
            "min_ms":          latencies[0],
            "max_ms":          latencies[-1],
            "avg_ms":          round(statistics.mean(latencies), 1),
            "median_ms":       int(statistics.median(latencies)),
            "p50_ms":          int(percentile(latencies, 50)),
            "p75_ms":          int(percentile(latencies, 75)),
            "p90_ms":          int(percentile(latencies, 90)),
            "p95_ms":          int(percentile(latencies, 95)),
            "p99_ms":          int(percentile(latencies, 99)),
            "stdev_ms":        round(statistics.stdev(latencies), 1) if len(latencies) > 1 else 0.0,
            # Breakdown lỗi theo HTTP status
            "error_codes":     _count_error_codes(errors),
        }

    def _count_error_codes(error_rows: list) -> dict:
        counts = defaultdict(int)
        for r in error_rows:
            counts[r["resp_code"] or "unknown"] += 1
        return dict(sorted(counts.items()))

    return {
        "all":    compute_metrics(all_rows, "ALL REQUESTS"),
        "labels": {lbl: compute_metrics(rows, lbl) for lbl, rows in rows_by_label.items()},
    }


def render_markdown(result: dict, jtl_path: str, include_labels: bool = True) -> str:
    """Render kết quả thành Markdown table."""
    all_m  = result["all"]
    labels = result["labels"]
    fname  = Path(jtl_path).name
    now    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        f"# JTL Analysis Report",
        f"",
        f"**File:** `{fname}`  ",
        f"**Generated:** {now}  ",
        f"**Total duration:** {all_m.get('duration_s', 0)} s  ",
        f"",
        f"---",
        f"",
        f"## Overall Metrics (All Samplers)",
        f"",
        f"| Metric               | Value                |",
        f"|----------------------|----------------------|",
        f"| Total Requests       | {all_m.get('total', 0):,}            |",
        f"| Error Count          | {all_m.get('errors', 0):,}            |",
        f"| **Error Rate**       | **{all_m.get('error_rate_pct', 0):.2f}%**         |",
        f"| **Throughput**       | **{all_m.get('throughput_rps', 0):.2f} req/s**   |",
        f"| Duration             | {all_m.get('duration_s', 0)} s          |",
        f"| Min Latency          | {all_m.get('min_ms', 0)} ms           |",
        f"| Avg Latency          | {all_m.get('avg_ms', 0)} ms           |",
        f"| Std Dev              | {all_m.get('stdev_ms', 0)} ms          |",
        f"| Max Latency          | {all_m.get('max_ms', 0)} ms           |",
        f"| **p50**              | **{all_m.get('p50_ms', 0)} ms**          |",
        f"| **p75**              | **{all_m.get('p75_ms', 0)} ms**          |",
        f"| **p90**              | **{all_m.get('p90_ms', 0)} ms**          |",
        f"| **p95**              | **{all_m.get('p95_ms', 0)} ms**          |",
        f"| **p99**              | **{all_m.get('p99_ms', 0)} ms**          |",
    ]

    if all_m.get("error_codes"):
        lines += ["", "### Error Code Breakdown", "", "| HTTP Code | Count |", "|-----------|-------|"]
        for code, cnt in all_m["error_codes"].items():
            lines.append(f"| {code}       | {cnt}   |")

    if include_labels and labels:
        lines += [
            "", "---", "",
            "## Per-Sampler Breakdown",
            "",
            "| Sampler | Requests | Errors | Error% | Throughput | p50 | p90 | p95 | p99 |",
            "|---------|----------|--------|--------|------------|-----|-----|-----|-----|",
        ]
        for lbl, m in labels.items():
            lines.append(
                f"| {lbl} | {m.get('total',0):,} | {m.get('errors',0)} | "
                f"{m.get('error_rate_pct',0):.1f}% | "
                f"{m.get('throughput_rps',0):.2f} rps | "
                f"{m.get('p50_ms',0)} ms | {m.get('p90_ms',0)} ms | "
                f"{m.get('p95_ms',0)} ms | {m.get('p99_ms',0)} ms |"
            )

    lines += [
        "", "---", "",
        "> **Ghi chú cho Human Review:**",
        "> - Percentile tính theo nearest-rank (giống JMeter mặc định).",
        "> - `error_rate` tính trên `success=false` trong .jtl, **không phải** chỉ HTTP 4xx/5xx.",
        ">   Timeout cũng được tính là error. Kiểm tra `error_codes` để phân biệt.",
        "> - `throughput` = total_requests / (last_ts - first_ts). Khác với JMeter GUI",
        ">   (JMeter GUI dùng active duration, bỏ qua idle time giữa ramp-up và ramp-down).",
        "",
    ]
    return "\n".join(lines)


def print_console(result: dict) -> None:
    """In tóm tắt ra console."""
    m = result["all"]
    w = 55
    print(f"\n{'='*w}")
    print(f"  📊 JTL Analysis — {m.get('name', '')}")
    print(f"{'='*w}")
    print(f"  Total Requests : {m.get('total', 0):,}")
    print(f"  Errors         : {m.get('errors', 0):,}  ({m.get('error_rate_pct', 0):.2f}%)")
    print(f"  Throughput     : {m.get('throughput_rps', 0):.2f} req/s")
    print(f"  Duration       : {m.get('duration_s', 0)} s")
    print(f"  Latency (ms)   : min={m.get('min_ms',0)}  avg={m.get('avg_ms',0)}  max={m.get('max_ms',0)}")
    print(f"  Percentiles    : p50={m.get('p50_ms',0)}  p75={m.get('p75_ms',0)}  "
          f"p90={m.get('p90_ms',0)}  p95={m.get('p95_ms',0)}  p99={m.get('p99_ms',0)}")
    if m.get("error_codes"):
        print(f"  Error codes    : {m['error_codes']}")
    print(f"{'='*w}\n")

    labels = result.get("labels", {})
    if labels:
        print("  Per-sampler breakdown:")
        hdr = f"  {'Sampler':<35} {'Req':>6} {'Err%':>6} {'p95(ms)':>8} {'RPS':>7}"
        print(hdr)
        print("  " + "-" * (len(hdr)-2))
        for lbl, lm in labels.items():
            short = lbl[:33] + ".." if len(lbl) > 35 else lbl
            print(f"  {short:<35} {lm.get('total',0):>6,} "
                  f"{lm.get('error_rate_pct',0):>6.1f}% "
                  f"{lm.get('p95_ms',0):>8} "
                  f"{lm.get('throughput_rps',0):>7.2f}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze JMeter .jtl file and produce structured Markdown report"
    )
    parser.add_argument("--file",       required=True, help="Path to .jtl file")
    parser.add_argument("--per-label",  action="store_true", default=True,
                        help="Include per-sampler breakdown (default: True)")
    parser.add_argument("--no-label",   action="store_true", default=False,
                        help="Skip per-sampler breakdown")
    args = parser.parse_args()

    jtl_path = args.file
    if not os.path.exists(jtl_path):
        print(f"❌ File not found: {jtl_path}")
        exit(1)

    print(f"\n🔍 Analyzing: {jtl_path}")
    result = parse_jtl(jtl_path)

    if not result["all"]:
        print("❌ No data parsed — check JTL format (need CSV with header row)")
        exit(1)

    print_console(result)

    include_labels = args.per_label and not args.no_label
    md_content = render_markdown(result, jtl_path, include_labels)

    out_path = str(Path(jtl_path).with_suffix(".analysis.md"))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"✅ Analysis saved → {out_path}")

