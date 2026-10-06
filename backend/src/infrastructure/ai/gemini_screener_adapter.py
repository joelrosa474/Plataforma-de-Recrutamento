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

    def calcular_match_score(self, curriculo_texto: str, vaga_descricao: str, vaga_requisitos: list[str]) -> float:
        if not self.client:
            return 50.0

        prompt = f"""
        Atue como um recrutador técnico experiente.
        Você deve avaliar a aderência de um candidato a uma vaga de emprego.

        DADOS DA VAGA:
        Descrição: {vaga_descricao}
        Requisitos: {', '.join(vaga_requisitos)}

        CURRÍCULO DO CANDIDATO:
        {curriculo_texto}

        Avalie o quão bem o currículo do candidato atende aos requisitos e à descrição da vaga.
        Forneça um "score" de 0.0 a 100.0, onde 100 significa o candidato ideal.
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
                return float(result.get("score", 50.0))
            except Exception as e:
                if attempt < 2 and ("503" in str(e) or "UNAVAILABLE" in str(e) or "429" in str(e)):
                    time.sleep(1.5 * (attempt + 1))
                    continue
                print(f"Erro ao calcular match_score com Gemini: {e}")
                return 50.0

        return 50.0

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
