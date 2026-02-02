import base64
import uuid

from app.services.supabase_client import supabase


def upload_pdf(pdf_base64: str, folder: str) -> str:
    """
    Recebe PDF em base64 (data:application/pdf;base64,...)
    Faz upload no Supabase Storage (bucket: processos)
    Retorna URL pública
    """

    try:
        # ---------------------------------
        # 1. Remove header base64
        # ---------------------------------
        if "," in pdf_base64:
            pdf_base64 = pdf_base64.split(",", 1)[1]

        pdf_bytes = base64.b64decode(pdf_base64)

        # ---------------------------------
        # 2. Path
        # ---------------------------------
        filename = f"{uuid.uuid4()}.pdf"
        path = f"{folder}/{filename}"

        # ---------------------------------
        # 3. Upload (SE FALHAR, LANÇA EXCEPTION)
        # ---------------------------------
        supabase.storage.from_("processos").upload(
            path,
            pdf_bytes,
            file_options={
                "content-type": "application/pdf",
                "upsert": False
            }
        )

        # ---------------------------------
        # 4. URL pública
        # ---------------------------------
        public_url = supabase.storage.from_("processos").get_public_url(path)

        return public_url

    except Exception as e:
        raise Exception(f"Falha no upload do PDF: {str(e)}")
