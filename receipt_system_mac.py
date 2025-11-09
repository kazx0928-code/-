from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime
import os

os.makedirs('templates', exist_ok=True)
receipt_html = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <title>領収書</title>
    <style>
        body { font-family: "Hiragino Kaku Gothic Pro", "MS Gothic", sans-serif; margin: 40px; font-size: 12pt; }
        .header { text-align: center; font-size: 24pt; margin-bottom: 30px; }
        .table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .table th, .table td { border: 1px solid black; padding: 10px; text-align: left; }
        .amount { text-align: right; font-size: 18pt; font-weight: bold; }
        .footer { margin-top: 50px; text-align: right; }
    </style>
</head>
<body>
    <div class="header">{{ company_name }} 領収書</div>
    <table class="table">
        <tr><th>番号</th><td>{{ receipt_no }}</td><th>日付</th><td>{{ date }}</td></tr>
        <tr><th colspan="2">お客様</th><td colspan="2">{{ customer }} 様</td></tr>
        <tr><th colspan="2">金額</th><td colspan="2" class="amount">¥{{ amount }}</td></tr>
        <tr><th colspan="2">但し書き</th><td colspan="2">{{ description }}</td></tr>
        <tr><th colspan="2">発行者</th><td colspan="2">{{ issuer }}</td></tr>
    </table>
    <div class="footer">いこい統合不動産</div>
</body>
</html>
"""
with open('templates/receipt.html', 'w', encoding='utf-8') as f:
    f.write(receipt_html.strip())

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('receipt.html')

print("いこい統合不動産 領収書発行システム Mac版")
data = {
    'company_name': 'いこい統合不動産',
    'receipt_no': f"REC-{datetime.now().strftime('%Y%m%d')}-001",
    'date': datetime.now().strftime('%Y年%m月%d日'),
    'customer': input("お客様名: ") or "株式会社例",
    'amount': input("金額: ") or "1234567",
    'description': input("但し書き: ") or "家賃預り金",
    'issuer': input("発行者: ") or "いこい太郎"
}

html_out = template.render(data)
pdf_path = f"receipt_{data['receipt_no']}.pdf"
HTML(string=html_out).write_pdf(pdf_path)

print(f"領収書PDF生成完了: {pdf_path}")
os.system(f"open {pdf_path}")
