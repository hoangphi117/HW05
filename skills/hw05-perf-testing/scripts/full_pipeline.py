#!/usr/bin/env python3
"""
full_pipeline.py — HW05 Agent Skill
Chạy toàn bộ pipeline cho một scenario:
  1. generate_csv (nếu chưa có)
  2. generate_jmx
  3. Hướng dẫn chạy JMeter (hoặc tự chạy nếu có --run)
  4. analyze_jtl (nếu có .jtl file)

Usage:
  python full_pipeline.py --student-id 22127001 --scenario load
  python full_pipeline.py --student-id 22127001 --scenario all
"""
import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
BASE_DIR    = SCRIPTS_DIR.parent.parent.parent  # hw05/


def run_step(step_name: str, cmd: list) -> bool:
    print(f"\n{'─'*55}")
    print(f"▶ {step_name}")
    print(f"  $ {' '.join(cmd)}")
    print(f"{'─'*55}")
    result = subprocess.run(cmd, capture_output=False, text=True)
    if result.returncode != 0:
        print(f"⚠  Step '{step_name}' exited with code {result.returncode}")
        return False
    return True


def pipeline(student_id: str, scenario: str, date: str, base_url: str,
             skip_csv: bool, run_jmeter: bool) -> None:
    print(f"\n{'═'*55}")
    print(f"  🚀 HW05 Full Pipeline — {scenario.upper()}")
    print(f"  Student ID : {student_id}")
    print(f"  Date       : {date}")
    print(f"  Base URL   : {base_url}")
    print(f"{'═'*55}")

    scripts = str(SCRIPTS_DIR)

    # Step 1: Generate CSV data
    users_csv    = str(BASE_DIR / "data" / "users.csv")
    products_csv = str(BASE_DIR / "data" / "products.csv")

    if not skip_csv or not os.path.exists(users_csv):
        run_step("Generate CSV test data", [
            sys.executable, str(SCRIPTS_DIR / "generate_csv.py"),
            "--users", "150",
            "--products", "150",
            "--out-dir", str(BASE_DIR / "data"),
        ])
    else:
        print(f"\n⏭  Skipping CSV generation (--skip-csv, files exist)")

    # Step 2: Generate JMX
    jmx_ok = run_step(f"Generate JMX — {scenario.upper()}", [
        sys.executable, str(SCRIPTS_DIR / "generate_jmx.py"),
        "--scenario",    scenario,
        "--student-id",  student_id,
        "--date",        date,
        "--base-url",    base_url,
        "--out-dir",     str(BASE_DIR / "test-plans"),
        "--users-csv",   users_csv,
        "--products-csv", products_csv,
    ])

    if not jmx_ok:
        print("❌ JMX generation failed. Stopping pipeline.")
        return

    plan_name = f"{student_id}_{scenario.capitalize()}_{date}"
    jmx_path  = BASE_DIR / "test-plans" / f"{plan_name}.jmx"
    jtl_path  = BASE_DIR / "results" / scenario / f"{plan_name}.jtl"
    html_dir  = BASE_DIR / "results" / scenario / "html-report"

    # Step 3: Run JMeter
    if run_jmeter:
        jmeter_cmd = os.environ.get("JMETER_HOME", "")
        if jmeter_cmd:
            jmeter_bin = str(Path(jmeter_cmd) / "bin" / "jmeter.bat")
        else:
            jmeter_bin = "jmeter"

        os.makedirs(str(html_dir), exist_ok=True)
        run_step(f"Run JMeter — {scenario.upper()}", [
            jmeter_bin, "-n",
            "-t", str(jmx_path),
            "-l", str(jtl_path),
            "-e", "-o", str(html_dir),
        ])
    else:
        print(f"\n📋 Manual step — Run JMeter:")
        print(f"   jmeter -n \\")
        print(f"     -t \"{jmx_path}\" \\")
        print(f"     -l \"{jtl_path}\" \\")
        print(f"     -e -o \"{html_dir}\"")
        print(f"\n   Hoặc dùng PowerShell script:")
        print(f"   .\\scripts\\run_scenario.ps1 -Scenario {scenario} -StudentID {student_id} -Date {date}")

    # Step 4: Analyze JTL (nếu có)
    if jtl_path.exists():
        run_step("Analyze JTL", [
            sys.executable, str(SCRIPTS_DIR / "analyze_jtl.py"),
            "--file", str(jtl_path),
        ])
    else:
        print(f"\n⏭  JTL not found yet (chưa chạy JMeter): {jtl_path}")

    print(f"\n{'═'*55}")
    print(f"  ✅ Pipeline complete for {scenario.upper()}")
    print(f"  📄 JMX    : {jmx_path}")
    print(f"  📊 Report : {html_dir}/index.html")
    print(f"{'═'*55}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="HW05 full pipeline: CSV → JMX → (JMeter) → Analysis"
    )
    parser.add_argument("--student-id",  required=True)
    parser.add_argument("--scenario",    default="load",
                        choices=["load", "stress", "spike", "soak", "all"])
    parser.add_argument("--date",        default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--base-url",    default="http://localhost:3000")
    parser.add_argument("--skip-csv",    action="store_true",
                        help="Skip CSV generation nếu files đã tồn tại")
    parser.add_argument("--run",         action="store_true",
                        help="Tự động chạy JMeter (cần JMETER_HOME hoặc jmeter trong PATH)")
    args = parser.parse_args()

    scenarios = ["load", "stress", "spike"] if args.scenario == "all" else [args.scenario]
    skip_csv  = args.skip_csv

    for i, sc in enumerate(scenarios):
        pipeline(
            student_id  = args.student_id,
            scenario    = sc,
            date        = args.date,
            base_url    = args.base_url,
            skip_csv    = skip_csv or (i > 0),  # chỉ generate CSV 1 lần
            run_jmeter  = args.run,
        )

