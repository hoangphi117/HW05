#!/usr/bin/env python3
"""
generate_csv.py — HW05 Agent Skill
Sinh file users.csv và products.csv cho Browse-to-Buy workflow.

Endpoints sử dụng data này:
  POST /api/login          → users.csv (email, password)
  GET  /api/products/:id   → products.csv (product_id)
  POST /api/cart           → products.csv (product_id, quantity)
  POST /api/checkout       → products.csv (coupon_code, total_amount)

Usage:
  python generate_csv.py --users 150 --products 150
  python generate_csv.py --users 50  --products 50 --out-dir ../data
"""
import csv
import argparse
import os
import random
import sqlite3
from datetime import datetime


# ── Tài khoản thực từ SUT README ─────────────────────────────────────────────
# Admin: admin@eshop.com / Admin123!
# User test: test@eshop.com / Test1234!
# Mật khẩu pattern yêu cầu: ≥8 ký tự, 1 hoa, 1 thường, 1 số, 1 ký tự đặc biệt

VALID_PASSWORD   = "Test1234!"   # khớp FR-01 password policy
WRONG_PASSWORD   = "wrongpass"   # cố tình sai để trigger lockout (FR-02)
WRONG_RATIO      = 0.10          # 10% dòng sẽ dùng wrong password

# Coupon codes có sẵn trong SUT (từ README):
# SAVE10  — percent 10%, ngưỡng 300.000đ, hạn 2099
# BIGBUY  — fixed 50.000đ, ngưỡng 500.000đ, hạn 2099
# VIP100  — fixed 100.000đ, ngưỡng 300.000đ, hạn 2099
# EXPIRED — đã hết hạn (dùng để test negative case)
COUPONS = ["SAVE10", "BIGBUY", "VIP100", "", "", ""]  # "" = không dùng coupon


def seed_database(users: list, db_path: str) -> None:
    """Đảm bảo các tài khoản test tồn tại trong database SQLite của SUT."""
    if not os.path.exists(db_path):
        print(f"ℹ  DB not found at {db_path}, skipping seed.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        inserted = 0
        for u in users:
            email = u["email"]
            cur.execute("SELECT id FROM users WHERE email = ?", (email,))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                    (f"Perf User {email.split('@')[0]}", email, VALID_PASSWORD, "user")
                )
                inserted += 1
        conn.commit()
        conn.close()
        print(f"✅ Database seeded: {inserted} new virtual users added to {db_path}")
    except Exception as e:
        print(f"⚠  Failed to seed database: {e}")


def generate_users(count: int, out_path: str, db_path: str = None) -> list:
    """
    Sinh danh sách virtual users.
    
    Columns:
      email        — địa chỉ email test (định dạng hợp lệ)
      password     — mật khẩu (90% đúng, 10% sai để trigger lockout)
      expect_fail  — true/false để JMeter biết bỏ qua lỗi login hay assert thành công
    
    Chú ý: Các dòng wrong-password phân bố đều, không dồn vào cuối,
    để tránh một user bị lockout 3 lần liên tiếp quá nhanh.
    """
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    
    user_records = []
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["email", "password", "expect_fail"])
        writer.writeheader()
        
        wrong_count = int(count * WRONG_RATIO)
        # Phân bố đều các dòng wrong_password trong toàn bộ dataset
        step = max(1, count // wrong_count) if wrong_count > 0 else 1
        wrong_indices = set(range(0, count, step)[:wrong_count])
        
        for i in range(count):
            is_wrong = (i in wrong_indices)
            rec = {
                "email":       f"perfuser{i+1:04d}@eshop.test",
                "password":    WRONG_PASSWORD if is_wrong else VALID_PASSWORD,
                "expect_fail": "true" if is_wrong else "false",
            }
            writer.writerow(rec)
            user_records.append(rec)
    
    wrong_in_file = sum(1 for r in user_records if r["expect_fail"] == "true")
    print(f"✅ users.csv        → {out_path}")
    print(f"   {count} users | {wrong_in_file} wrong-password ({wrong_in_file/count*100:.0f}%) for lockout testing")

    if db_path:
        seed_database(user_records, db_path)

    return user_records


def generate_products(count: int, out_path: str, product_id_range: tuple = (1, 20)) -> None:
    """
    Sinh danh sách product references cho cart và checkout.
    
    Columns:
      product_id    — ID sản phẩm trong SUT (mặc định 1-20)
      quantity      — số lượng thêm vào giỏ (1-3)
      coupon_code   — mã giảm giá (hoặc rỗng)
      total_amount  — tổng tiền giả lập cho checkout body
                      (NOTE: theo FR-08, backend tự tính lại — giá trị này chỉ
                       để JMeter có thể gửi request hợp lệ; server sẽ override)
    """
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    
    id_min, id_max = product_id_range
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["product_id", "quantity", "coupon_code", "total_amount"]
        )
        writer.writeheader()
        
        for i in range(count):
            product_id = random.randint(id_min, id_max)
            quantity   = random.randint(1, 3)
            coupon     = random.choice(COUPONS)
            # total_amount ước tính (server sẽ tính lại theo FR-08)
            total_amt  = random.randint(1, 5) * 100_000   # 100k–500k VND
            
            writer.writerow({
                "product_id":   product_id,
                "quantity":     quantity,
                "coupon_code":  coupon,
                "total_amount": total_amt,
            })
    
    print(f"✅ products.csv     → {out_path}")
    print(f"   {count} rows | product_id range [{id_min}-{id_max}] | 3 coupon types")


def print_summary(users_path: str, products_path: str) -> None:
    print()
    print("─" * 55)
    print("📋 CSV Data Summary")
    print("─" * 55)
    print(f"  users.csv    : {users_path}")
    print(f"  products.csv : {products_path}")
    print()
    print("  Workflow mapping (Browse-to-Buy):")
    print("    POST /api/login          ← users.csv (email, password)")
    print("    GET  /api/products/:id   ← products.csv (product_id)")
    print("    POST /api/cart           ← products.csv (product_id, quantity)")
    print("    POST /api/checkout       ← products.csv (coupon_code, total_amount)")
    print()
    print("  ⚠  Lưu ý: 10% dòng users.csv có wrong-password")
    print("     → JMeter sẽ nhận 401, skip và chuyển VU tiếp theo")
    print("     → Trigger lockout tự nhiên trong Stress/Spike scenario")
    print("─" * 55)
    print(f"  Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("─" * 55)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate CSV test data for HW05 Browse-to-Buy workflow"
    )
    parser.add_argument("--users",    type=int, default=150, help="Number of users (default: 150)")
    parser.add_argument("--products", type=int, default=150, help="Number of product rows (default: 150)")
    parser.add_argument("--out-dir",  type=str, default="../data", help="Output directory (default: ../data)")
    parser.add_argument("--db-path",  type=str, default=r"C:\Users\opmeo\OneDrive\Desktop\eshop-sut\backend\database.sqlite",
                        help="Path to SUT SQLite database for seeding users")
    parser.add_argument("--product-id-max", type=int, default=5,
                        help="Max product ID to use (check actual SUT DB, default: 5)")
    args = parser.parse_args()

    out_dir      = args.out_dir
    users_path   = os.path.join(out_dir, "users.csv")
    products_path = os.path.join(out_dir, "products.csv")

    print(f"\n🔧 Generating test data → {os.path.abspath(out_dir)}\n")
    generate_users(args.users, users_path, db_path=args.db_path)
    generate_products(args.products, products_path, product_id_range=(1, args.product_id_max))
    print_summary(users_path, products_path)

