from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime
import os

os.makedirs('templates', exist_ok=True)

# 退去立会いチェックリスト 点検箇所・項目の定義
# 各セクションごとに、点検する項目を並べる
SECTIONS = [
    ("玄関", ["玄関ドア・鍵", "たたき・床", "下駄箱"]),
    ("居室（洋室・和室）", ["壁クロス", "天井", "床（フローリング/畳/CF）", "建具・ふすま・障子", "窓・網戸・サッシ", "照明・スイッチ", "コンセント"]),
    ("キッチン", ["シンク・水栓", "コンロ・グリル", "換気扇・レンジフード", "収納・吊戸棚", "壁・床"]),
    ("浴室・洗面", ["浴槽・シャワー水栓", "換気扇・排水", "洗面台・鏡・水栓"]),
    ("トイレ", ["便器・タンク", "ウォシュレット", "換気・床"]),
    ("設備", ["エアコン", "給湯器", "インターホン", "火災警報器"]),
    ("ベランダ・その他", ["ベランダ・物干し", "クリーニング状況", "鍵返却本数", "リモコン・付属品返却"]),
]

# 負担区分の選択肢（番号入力で選ぶ）
BURDEN_CHOICES = {"1": "貸主負担", "2": "借主負担", "3": "経年劣化", "": "－"}
# 状態の選択肢
STATUS_CHOICES = {"1": "良好", "2": "汚れ", "3": "破損・要補修", "": "良好"}


def ask_item(section, item):
    print(f"\n  [{section}] {item}")
    s = input("    状態 (1:良好 2:汚れ 3:破損・要補修) [1]: ").strip()
    status = STATUS_CHOICES.get(s, s or "良好")
    b = input("    負担区分 (1:貸主 2:借主 3:経年劣化) [－]: ").strip()
    burden = BURDEN_CHOICES.get(b, b or "－")
    memo = input("    メモ（経年劣化の内容・補修箇所など）: ").strip()
    return {"item": item, "status": status, "burden": burden, "memo": memo}


checklist_html = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <title>退去立会いチェックリスト</title>
    <style>
        body { font-family: "Hiragino Kaku Gothic Pro", "MS Gothic", sans-serif; margin: 30px; font-size: 10pt; }
        .header { text-align: center; font-size: 20pt; margin-bottom: 10px; }
        .company { text-align: center; font-size: 11pt; color: #444; margin-bottom: 20px; }
        .info { width: 100%; border-collapse: collapse; margin-bottom: 16px; }
        .info th, .info td { border: 1px solid #999; padding: 5px 8px; text-align: left; font-size: 9.5pt; }
        .info th { background: #f0f0f0; width: 90px; }
        .section-title { background: #333; color: #fff; padding: 4px 8px; margin-top: 14px; font-size: 11pt; }
        .check { width: 100%; border-collapse: collapse; }
        .check th, .check td { border: 1px solid #999; padding: 4px 6px; text-align: left; }
        .check th { background: #f0f0f0; }
        .col-item { width: 28%; }
        .col-status { width: 16%; }
        .col-burden { width: 16%; }
        .col-memo { width: 40%; }
        .ng { color: #c00; font-weight: bold; }
        .settle { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .settle th, .settle td { border: 1px solid #999; padding: 6px 8px; }
        .settle th { background: #f0f0f0; width: 160px; }
        .amount { text-align: right; font-weight: bold; }
        .sign { margin-top: 30px; width: 100%; }
        .sign td { padding: 14px 8px; border-bottom: 1px solid #333; width: 50%; }
    </style>
</head>
<body>
    <div class="header">退去立会いチェックリスト</div>
    <div class="company">{{ company_name }}</div>

    <table class="info">
        <tr><th>物件名</th><td>{{ property_name }}</td><th>部屋番号</th><td>{{ room_no }}</td></tr>
        <tr><th>入居者名</th><td>{{ tenant }} 様</td><th>立会日</th><td>{{ inspect_date }}</td></tr>
        <tr><th>入居日</th><td>{{ move_in }}</td><th>退去日</th><td>{{ move_out }}</td></tr>
        <tr><th>立会者</th><td colspan="3">{{ inspector }}</td></tr>
    </table>

    {% for section, items in sections %}
    <div class="section-title">{{ section }}</div>
    <table class="check">
        <tr>
            <th class="col-item">項目</th>
            <th class="col-status">状態</th>
            <th class="col-burden">負担区分</th>
            <th class="col-memo">経年劣化・メモ</th>
        </tr>
        {% for row in items %}
        <tr>
            <td>{{ row.item }}</td>
            <td>{% if row.status == '良好' %}{{ row.status }}{% else %}<span class="ng">{{ row.status }}</span>{% endif %}</td>
            <td>{{ row.burden }}</td>
            <td>{{ row.memo }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endfor %}

    <div class="section-title">敷金精算</div>
    <table class="settle">
        <tr><th>敷金預り額</th><td class="amount">¥{{ deposit }}</td></tr>
        <tr><th>借主負担額（原状回復）</th><td class="amount">¥{{ tenant_charge }}</td></tr>
        <tr><th>返還額</th><td class="amount">¥{{ refund }}</td></tr>
        <tr><th>備考</th><td>{{ remarks }}</td></tr>
    </table>

    <table class="sign">
        <tr>
            <td>立会者署名：</td>
            <td>入居者署名：</td>
        </tr>
    </table>
</body>
</html>
"""

with open('templates/move_out_inspection.html', 'w', encoding='utf-8') as f:
    f.write(checklist_html.strip())

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('move_out_inspection.html')

print("=" * 50)
print("いこい統合不動産 退去立会いチェックリスト作成")
print("=" * 50)

property_name = input("物件名: ") or "いこいハイツ"
room_no = input("部屋番号: ") or "101"
tenant = input("入居者名: ") or "山田太郎"
move_in = input("入居日 (例:2020年4月1日): ") or "－"
move_out = input("退去日 (例:2026年5月31日): ") or "－"
inspector = input("立会者: ") or "いこい太郎"

print("\n--- 各箇所の点検（Enterで既定値） ---")
sections = []
for section, items in SECTIONS:
    rows = [ask_item(section, item) for item in items]
    sections.append((section, rows))

print("\n--- 敷金精算 ---")

def yen(prompt, default):
    v = input(prompt).strip() or default
    try:
        return f"{int(v):,}"
    except ValueError:
        return v

deposit = yen("敷金預り額: ", "0")
tenant_charge = yen("借主負担額（原状回復）: ", "0")
try:
    refund = f"{int(deposit.replace(',', '')) - int(tenant_charge.replace(',', '')):,}"
except ValueError:
    refund = "0"
remarks = input("備考: ").strip()

data = {
    "company_name": "いこい統合不動産",
    "property_name": property_name,
    "room_no": room_no,
    "tenant": tenant,
    "move_in": move_in,
    "move_out": move_out,
    "inspect_date": datetime.now().strftime("%Y年%m月%d日"),
    "inspector": inspector,
    "sections": sections,
    "deposit": deposit,
    "tenant_charge": tenant_charge,
    "refund": refund,
    "remarks": remarks,
}

html_out = template.render(data)
safe_name = f"{property_name}_{room_no}".replace("/", "_").replace(" ", "")
pdf_path = f"退去立会い_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
HTML(string=html_out).write_pdf(pdf_path)

print(f"\n退去立会いチェックリストPDF生成完了: {pdf_path}")
os.system(f"open '{pdf_path}'")
