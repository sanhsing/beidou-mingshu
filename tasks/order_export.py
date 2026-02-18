"""訂單匯出功能 | @理樞"""
import sqlite3, csv, json
from io import StringIO
def export_orders(db='beidou_unified.db', format='csv'):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT order_no, product_name, amount, status, created_at FROM orders ORDER BY created_at DESC LIMIT 100")
    rows = cursor.fetchall()
    cols = ['order_no', 'product_name', 'amount', 'status', 'created_at']
    conn.close()
    if format == 'csv':
        out = StringIO()
        w = csv.writer(out)
        w.writerow(cols)
        w.writerows(rows)
        return out.getvalue()
    return json.dumps([dict(zip(cols, r)) for r in rows], ensure_ascii=False)
