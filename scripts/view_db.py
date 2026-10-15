import os
import sys
import sqlite3

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def view_db(limit=20):
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "runtime", "waterqa.db")
    if not os.path.exists(db_path):
        print(f"[!] Chua tim thay file database tai: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    print("=" * 105)
    print(f"[*] DATABASE FILE: {db_path} ({round(os.path.getsize(db_path) / 1024, 1)} KB)")
    print("=" * 105)

    # 1. Danh sách bảng
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r["name"] for r in c.fetchall()]
    print(f"[*] Cac bang hien co: {', '.join(tables)}")

    # 2. Xem bảng devices
    if "devices" in tables:
        print("\n" + "-" * 40 + " BANG [devices] " + "-" * 40)
        c.execute("SELECT device_id, transport, last_seen, is_online, sample_count FROM devices;")
        dev_rows = c.fetchall()
        if not dev_rows:
            print("  (Chua co du lieu thiet bi)")
        else:
            print(f"  {'Device ID':<25} {'Transport':<12} {'Online':<8} {'Samples':<10} {'Last Seen':<25}")
            for d in dev_rows:
                print(f"  {d['device_id']:<25} {d['transport']:<12} {bool(d['is_online']):<8} {d['sample_count']:<10} {d['last_seen']:<25}")

    # 3. Xem bảng results
    if "results" in tables:
        c.execute("SELECT COUNT(*) FROM results;")
        total = c.fetchone()[0]
        print("\n" + "-" * 40 + f" BANG [results] (Tong: {total} dong - Hien {min(limit, total)} dong moi nhat) " + "-" * 40)
        
        c.execute(f"SELECT event_id, seq, station, pH, DO, turbidity, EC, temperature, wqi, prediction, anomaly_score, ts FROM results ORDER BY seq DESC LIMIT {limit};")
        rows = c.fetchall()
        if not rows:
            print("  (Chua co du lieu ket qua)")
        else:
            headers = ["Event ID", "Seq", "Station", "pH", "DO", "Turb", "EC", "Temp", "WQI", "Label", "Score", "Date"]
            print(f"  {headers[0]:<10} {headers[1]:<5} {headers[2]:<20} {headers[3]:<6} {headers[4]:<6} {headers[5]:<6} {headers[6]:<7} {headers[7]:<6} {headers[8]:<6} {headers[9]:<10} {headers[10]:<7} {headers[11]:<12}")
            print("  " + "-" * 103)
            for r in rows:
                print(f"  {r['event_id']:<10} {r['seq']:<5} {r['station'][:18]:<20} {r['pH']:<6.2f} {r['DO']:<6.2f} {r['turbidity']:<6.2f} {r['EC']:<7.1f} {r['temperature']:<6.1f} {r['wqi']:<6.1f} {r['prediction']:<10} {r['anomaly_score']:<7.3f} {r['ts']:<12}")
    
    print("\n" + "=" * 105)

if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    view_db(limit)
