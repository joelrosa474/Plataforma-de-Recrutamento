import os
import json
import time
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from src.application.ports.ai_screener_port import AIScreenerPort


class HabilidadesSchema(BaseModel):
    habilidades: list[str] = Field(description="Lista de habilidades técnicas e comportamentais extraídas do currículo.")


class MatchScoreSchema(BaseModel):
    score: float = Field(description="Pontuação de 0.0 a 100.0 indicando o fit do candidato com a vaga.")
    justificativa: str = Field(description="Breve explicação do porquê desta nota.")


class GeminiScreenerAdapter(AIScreenerPort):
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("AVISO: GEMINI_API_KEY não encontrada nas variáveis de ambiente.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

        # gemini-flash-latest é o modelo oficial mais estável e rápido para NLP e triagem
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")

    def avaliar_candidatura(self, curriculo_texto: str, vaga_descricao: str, vaga_requisitos: list[str]) -> tuple[float, str]:
        if not self.client:
            return 50.0, "Análise automática desativada (chave de IA não configurada)."

        prompt = f"""
        Atue como um recrutador técnico experiente e analítico.
        Avalie a aderência do candidato à vaga de emprego especificada.

        DADOS DA VAGA:
        Descrição: {vaga_descricao}
        Requisitos: {', '.join(vaga_requisitos)}

        CURRÍCULO DO CANDIDATO:
        {curriculo_texto}

        Avalie o quão bem o currículo do candidato atende aos requisitos e à descrição da vaga.
        Retorne:
        - "score": nota de 0.0 a 100.0.
        - "justificativa": análise concisa e profissional destacando os pontos fortes e eventuais lacunas técnicas encontradas.
        """

        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=MatchScoreSchema,
                        temperature=0.2,
                    ),
                )
                result = json.loads(response.text)
                score = float(result.get("score", 50.0))
                justificativa = str(result.get("justificativa") or "Avaliação concluída pela IA.")
                return score, justificativa
            except Exception as e:
                if attempt < 2 and ("503" in str(e) or "UNAVAILABLE" in str(e) or "429" in str(e)):
                    time.sleep(1.5 * (attempt + 1))
                    continue
                print(f"Erro ao avaliar candidatura com Gemini: {e}")
                return 50.0, "Não foi possível gerar a justificativa detalhada devido a uma instabilidade temporária na API."

        return 50.0, "Análise concluída com pontuação padrão."

    def calcular_match_score(self, curriculo_texto: str, vaga_descricao: str, vaga_requisitos: list[str]) -> float:
        score, _ = self.avaliar_candidatura(curriculo_texto, vaga_descricao, vaga_requisitos)
        return score

    def extrair_habilidades(self, curriculo_texto: str) -> list[str]:
        if not self.client:
            return []

        prompt = f"""
        Analise o seguinte currículo e extraia todas as habilidades (skills) técnicas e comportamentais.
        Retorne uma lista limpa e padronizada.

        CURRÍCULO:
        {curriculo_texto}
        """

        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=HabilidadesSchema,
                        temperature=0.1,
                    ),
                )
                result = json.loads(response.text)
                return result.get("habilidades", [])
            except Exception as e:
                if attempt < 2 and ("503" in str(e) or "UNAVAILABLE" in str(e) or "429" in str(e)):
                    time.sleep(1.5 * (attempt + 1))
                    continue
                print(f"Erro ao extrair habilidades com Gemini: {e}")
                return []

        return []
