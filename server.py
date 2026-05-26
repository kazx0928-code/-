"""退去立会いチェックリスト 保存サーバー

スマホUIから送られた立会いデータを受け取り、
  1. PDFを生成して pdfs/ に保存
  2. DB（MySQL / SQL Server / SQLite）に保存
する。

接続先は環境変数 DATABASE_URL で切替（未設定なら同フォルダの SQLite）:
  PostgreSQL: postgresql+psycopg2://user:pass@host:5432/dbname
  SQLite    : sqlite:///inspections.db  （既定・検証用）

起動:  python server.py   →  http://localhost:5000 をスマホのブラウザで開く
"""
import os
from datetime import datetime

from flask import Flask, request, jsonify, send_file, send_from_directory, abort
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'inspections.db')}")
engine = create_engine(DATABASE_URL, future=True)
Session = sessionmaker(bind=engine, future=True)
Base = declarative_base()


class Inspection(Base):
    __tablename__ = "inspections"
    id = Column(Integer, primary_key=True)
    property_name = Column(String(120))
    room_no = Column(String(40))
    tenant = Column(String(120))
    move_in = Column(String(40))
    move_out = Column(String(40))
    inspect_date = Column(String(40))
    inspector = Column(String(120))
    deposit = Column(Integer, default=0)
    tenant_charge = Column(Integer, default=0)
    refund = Column(Integer, default=0)
    remarks = Column(Text, default="")
    pdf_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    items = relationship("InspectionItem", back_populates="inspection",
                         cascade="all, delete-orphan")


class InspectionItem(Base):
    __tablename__ = "inspection_items"
    id = Column(Integer, primary_key=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"))
    section = Column(String(80))
    item = Column(String(120))
    status = Column(String(40))
    burden = Column(String(40))
    memo = Column(Text, default="")
    inspection = relationship("Inspection", back_populates="items")


Base.metadata.create_all(engine)

_env = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")))

app = Flask(__name__)


def _int(v):
    try:
        return int(str(v).replace(",", "").strip() or 0)
    except ValueError:
        return 0


def build_pdf(payload, refund):
    """payload(JSON) からPDFを生成し、保存パスを返す。"""
    sections = [(s["section"], s.get("items", [])) for s in payload.get("sections", [])]
    ctx = {
        "company_name": "いこい統合不動産",
        "property_name": payload.get("property", ""),
        "room_no": payload.get("room", ""),
        "tenant": payload.get("tenant", ""),
        "move_in": payload.get("move_in", "－"),
        "move_out": payload.get("move_out", "－"),
        "inspect_date": payload.get("inspect_date", datetime.now().strftime("%Y年%m月%d日")),
        "inspector": payload.get("inspector", ""),
        "sections": sections,
        "deposit": f"{_int(payload.get('deposit')):,}",
        "tenant_charge": f"{_int(payload.get('charge')):,}",
        "refund": f"{refund:,}",
        "remarks": payload.get("remarks", ""),
    }
    html_out = _env.get_template("move_out_inspection.html").render(ctx)
    safe = f"{ctx['property_name']}_{ctx['room_no']}".replace("/", "_").replace(" ", "") or "inspection"
    fname = f"退去立会い_{safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join(PDF_DIR, fname)
    HTML(string=html_out).write_pdf(path)
    return fname


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "taikyo_checklist.html")


@app.route("/api/inspections", methods=["POST"])
def create_inspection():
    payload = request.get_json(force=True, silent=True) or {}
    deposit = _int(payload.get("deposit"))
    charge = _int(payload.get("charge"))
    refund = deposit - charge

    pdf_name = build_pdf(payload, refund)

    with Session() as s:
        insp = Inspection(
            property_name=payload.get("property", ""),
            room_no=payload.get("room", ""),
            tenant=payload.get("tenant", ""),
            move_in=payload.get("move_in", ""),
            move_out=payload.get("move_out", ""),
            inspect_date=payload.get("inspect_date", datetime.now().strftime("%Y年%m月%d日")),
            inspector=payload.get("inspector", ""),
            deposit=deposit,
            tenant_charge=charge,
            refund=refund,
            remarks=payload.get("remarks", ""),
            pdf_path=pdf_name,
        )
        for sec in payload.get("sections", []):
            for it in sec.get("items", []):
                insp.items.append(InspectionItem(
                    section=sec.get("section", ""),
                    item=it.get("item", ""),
                    status=it.get("status", ""),
                    burden=it.get("burden", ""),
                    memo=it.get("memo", ""),
                ))
        s.add(insp)
        s.commit()
        new_id = insp.id

    return jsonify({"id": new_id, "refund": refund, "pdf_url": f"/api/inspections/{new_id}/pdf"})


@app.route("/api/inspections", methods=["GET"])
def list_inspections():
    with Session() as s:
        rows = s.query(Inspection).order_by(Inspection.id.desc()).all()
        return jsonify([{
            "id": r.id, "property_name": r.property_name, "room_no": r.room_no,
            "tenant": r.tenant, "inspect_date": r.inspect_date,
            "refund": r.refund, "pdf_url": f"/api/inspections/{r.id}/pdf",
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in rows])


@app.route("/api/inspections/<int:insp_id>/pdf")
def get_pdf(insp_id):
    with Session() as s:
        r = s.get(Inspection, insp_id)
        if not r or not r.pdf_path:
            abort(404)
        path = os.path.join(PDF_DIR, r.pdf_path)
        if not os.path.exists(path):
            abort(404)
        return send_file(path, mimetype="application/pdf",
                         as_attachment=False, download_name=r.pdf_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
