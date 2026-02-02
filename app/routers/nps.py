from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from datetime import date

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfMerger

from app.services.upload import upload_pdf
from app.services.supabase_client import supabase

router = APIRouter(prefix="/nps", tags=["NPS"])


# ===============================
# MODELS
# ===============================
class NPSRequest(BaseModel):
    processo_id: str
    nps: int
    avaliacoes: dict
    feedback: dict


# ===============================
# ROTA
# ===============================
@router.post("/finalizar")
def finalizar_nps(data: NPSRequest):

    processo_id = data.processo_id.strip()
    if not processo_id:
        raise HTTPException(status_code=400, detail="processo_id ausente")

    # ===============================
    # CAMINHOS
    # ===============================
    base_dir = os.path.join("pdfs", processo_id)

    termo_pdf = os.path.join(base_dir, "termo", "termo.pdf")
    ressalvas_pdf = os.path.join(base_dir, "ressalvas", "ressalvas.pdf")
    final_dir = os.path.join(base_dir, "final")

    if not os.path.exists(termo_pdf):
        raise HTTPException(404, "Termo não encontrado")

    if not os.path.exists(ressalvas_pdf):
        raise HTTPException(404, "Ressalvas não encontradas")

    os.makedirs(final_dir, exist_ok=True)

    # ===============================
    # GERAR PDF NPS
    # ===============================
    nps_pdf = os.path.join(final_dir, "nps.pdf")
    c = canvas.Canvas(nps_pdf, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Pesquisa de Satisfação (NPS)")
    y -= 40

    c.setFont("Helvetica", 12)
    c.drawString(40, y, f"NPS informado: {data.nps}")
    y -= 30

    # Avaliações
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Avaliações")
    y -= 20

    c.setFont("Helvetica", 10)
    for k, v in data.avaliacoes.items():
        c.drawString(40, y, f"{k}: {v}")
        y -= 15
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)

    # Feedback
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Feedback")
    y -= 20

    c.setFont("Helvetica", 10)
    for titulo, texto in data.feedback.items():
        c.drawString(40, y, f"{titulo}:")
        y -= 14

        for linha in texto.split("\n"):
            c.drawString(50, y, linha[:110])
            y -= 14
            if y < 80:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)

        y -= 10

    c.showPage()
    c.save()

    # ===============================
    # MERGE FINAL (3 PDFs)
    # ===============================
    final_pdf = os.path.join(final_dir, "entrega_final.pdf")

    merger = PdfMerger()
    merger.append(termo_pdf)
    merger.append(ressalvas_pdf)
    merger.append(nps_pdf)
    merger.write(final_pdf)
    merger.close()

    if not os.path.exists(final_pdf):
        raise HTTPException(500, "Falha ao gerar PDF final")

    # ===============================
    # UPLOAD
    # ===============================
    remote_path = f"{processo_id}/entrega_final.pdf"
    final_url = upload_pdf(final_pdf, remote_path)

    if not final_url:
        raise HTTPException(500, "Falha no upload do PDF final")

    # ===============================
    # UPDATE BANCO (100% COMPATÍVEL)
    # ===============================
    supabase.table("processos").update({
        "status": "finalizado",
        "pdf_final": final_url,
        "finalizado_em": date.today().isoformat()
    }).eq("processo_id", processo_id).execute()

    return {
        "status": "ok",
        "pdf_final": final_url
    }
