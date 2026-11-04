"""
re_triagem_candidaturas.py
--------------------------
Script de manutenção: re-executa a triagem de IA (Gemini 1.5 Flash) para todas
as candidaturas que ficaram com o score padrão de 50% devido ao bug do modelo
'gemini-flash-latest' (nome inválido).

Uso:
    cd backend
    python re_triagem_candidaturas.py

    # Apenas ver o que seria processado (sem alterar nada):
    python re_triagem_candidaturas.py --dry-run

    # Re-triar candidatura específica:
    python re_triagem_candidaturas.py --id 5
"""

import sys
import os
import argparse
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente do backend
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Adiciona o backend ao PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

from src.infrastructure.database.config import SessionLocal
from src.infrastructure.database.models import CandidaturaModel, VagaModel, UsuarioModel
from src.application.services.pdf_service import PDFService
from src.application.services.storage_service import StorageService
from src.infrastructure.ai.gemini_screener_adapter import GeminiScreenerAdapter

storage = StorageService()
ai = GeminiScreenerAdapter()


def extrair_texto_curriculo(candidatura: CandidaturaModel) -> str:
    """Tenta extrair o texto do PDF em disco. Retorna string vazia se não encontrar."""
    if not candidatura.curriculo_path:
        return ""
    if not storage.arquivo_existe(candidatura.curriculo_path):
        print(f"  [AVISO] Ficheiro não encontrado: {candidatura.curriculo_path}")
        return ""
    try:
        with open(candidatura.curriculo_path, "rb") as f:
            file_bytes = f.read()
        texto = PDFService.extract_text_from_pdf(file_bytes)
        return texto or ""
    except Exception as e:
        print(f"  [ERRO] Falha ao ler PDF: {e}")
        return ""


def re_triar_candidatura(db, candidatura: CandidaturaModel, vaga: VagaModel, dry_run: bool) -> dict:
    """Re-executa a triagem de IA para uma candidatura e actualiza a BD."""
    texto = extrair_texto_curriculo(candidatura)
    if not texto.strip():
        return {"status": "IGNORADA", "motivo": "PDF sem texto extraível ou não encontrado"}

    score, feedback, analise = ai.avaliar_candidatura(
        curriculo_texto=texto,
        vaga_descricao=vaga.descricao or "",
        vaga_requisitos=vaga.get_requisitos_list(),
    )

    # Determinar nova fase
    fase_anterior = candidatura.fase_atual
    if fase_anterior in ("Contratado", "Reprovado"):
        return {"status": "IGNORADA", "motivo": f"Fase final '{fase_anterior}' — não alterada"}

    nova_fase = fase_anterior
    if score >= 85.0 and fase_anterior == "Triagem":
        nova_fase = "Entrevista"

    if dry_run:
        return {
            "status": "DRY-RUN",
            "score_anterior": candidatura.match_score,
            "score_novo": round(score, 1),
            "fase_anterior": fase_anterior,
            "nova_fase": nova_fase,
            "feedback_preview": feedback[:100] + "…" if len(feedback) > 100 else feedback,
        }

    # Aplicar na BD
    candidatura.match_score = score
    candidatura.feedback_ia = feedback
    candidatura.analise_match_ia = json.dumps(analise, ensure_ascii=False) if analise else None
    candidatura.fase_atual = nova_fase
    db.commit()

    return {
        "status": "ATUALIZADA",
        "score_anterior": candidatura.match_score,
        "score_novo": round(score, 1),
        "fase_anterior": fase_anterior,
        "nova_fase": nova_fase,
    }


def main():
    parser = argparse.ArgumentParser(description="Re-triagem de candidaturas com score padrão 50%")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem alterar a base de dados")
    parser.add_argument("--id", type=int, default=None, help="Re-triar apenas a candidatura com este ID")
    parser.add_argument("--all", action="store_true", help="Re-triar TODAS as candidaturas, mesmo as que nao tem score 50")
    args = parser.parse_args()

    if not ai.client:
        print("[ERRO FATAL] GEMINI_API_KEY não configurada. Defina-a no backend/.env.")
        sys.exit(1)

    db = SessionLocal()
    try:
        # Seleccionar candidaturas a processar
        query = db.query(CandidaturaModel)

        if args.id:
            query = query.filter(CandidaturaModel.id == args.id)
        elif not args.all:
            # Por defeito: apenas as que têm o score padrão de 50% E feedback de erro
            query = query.filter(
                CandidaturaModel.match_score == 50.0,
                CandidaturaModel.fase_atual.notin_(["Contratado", "Reprovado"])
            )

        candidaturas = query.order_by(CandidaturaModel.id).all()

        if not candidaturas:
            print("Nenhuma candidatura encontrada com os critérios especificados.")
            return

        modo = "DRY-RUN (simulação)" if args.dry_run else "REAL (vai alterar a BD)"
        print(f"\n{'='*60}")
        print(f"RE-TRIAGEM DE CANDIDATURAS — Modo: {modo}")
        print(f"Modelo Gemini: {ai.model_name}")
        print(f"Candidaturas a processar: {len(candidaturas)}")
        print(f"{'='*60}\n")

        for cand in candidaturas:
            vaga = db.query(VagaModel).filter(VagaModel.id == cand.vaga_id).first()
            candidato = db.query(UsuarioModel).filter(UsuarioModel.id == cand.candidato_id).first()

            print(f"[ID {cand.id:>4}] Candidato: {candidato.nome if candidato else 'N/A':<30} | Vaga: {vaga.titulo if vaga else 'N/A'}")

            if not vaga:
                print(f"  [IGNORADA] Vaga não encontrada.\n")
                continue

            resultado = re_triar_candidatura(db, cand, vaga, dry_run=args.dry_run)
            status = resultado.get("status")

            if status == "IGNORADA":
                print(f"  [IGNORADA] {resultado.get('motivo')}")
            elif status == "DRY-RUN":
                print(f"  [SIMULAÇÃO] Score: {resultado['score_anterior']}% → {resultado['score_novo']}%")
                print(f"  [SIMULAÇÃO] Fase:  {resultado['fase_anterior']} → {resultado['nova_fase']}")
                print(f"  [SIMULAÇÃO] Parecer: {resultado['feedback_preview']}")
            else:
                print(f"  [OK] Score actualizado: {resultado['score_novo']}%")
                print(f"  [OK] Fase: {resultado['fase_anterior']} → {resultado['nova_fase']}")
            print()

        print(f"{'='*60}")
        if args.dry_run:
            print("Simulação concluída. Nenhuma alteração foi feita na base de dados.")
            print("Para aplicar, corra sem o flag --dry-run.")
        else:
            print("Re-triagem concluída. Todas as candidaturas foram actualizadas.")
        print(f"{'='*60}\n")

    finally:
        db.close()


if __name__ == "__main__":
    main()
