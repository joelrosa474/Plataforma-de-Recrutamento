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
    competencias_alinhadas: list[str] = Field(description="Até cinco competências ou evidências do currículo que atendem à vaga.")
    requisitos_em_falta: list[str] = Field(description="Até cinco requisitos que não foram encontrados claramente no currículo. Não inferir informações.")
    evidencias_experiencia: list[str] = Field(description="Até três experiências, projetos ou formações do currículo relevantes para a vaga.")
    recomendacao: str = Field(description="Recomendação concisa e neutra para o recrutador sobre o próximo passo.")


class PerguntaEntrevistaSchema(BaseModel):
    pergunta: str = Field(description="Pergunta objetiva e profissional para a entrevista.")
    criterio_avaliacao: str = Field(description="O que o entrevistador deve procurar na resposta.")


class RoteiroEntrevistaSchema(BaseModel):
    perguntas: list[PerguntaEntrevistaSchema] = Field(description="Cinco perguntas personalizadas, justas e relevantes.")


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

    def avaliar_candidatura(self, curriculo_texto: str, vaga_descricao: str, vaga_requisitos: list[str]) -> tuple[float, str, dict]:
        if not self.client:
            return 50.0, "Análise automática desativada (chave de IA não configurada).", self._analise_padrao()

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
        - "competencias_alinhadas": lista com até 5 competências comprovadas no currículo e relevantes para a vaga.
        - "requisitos_em_falta": lista com até 5 requisitos da vaga sem evidência clara no currículo. Não use atributos pessoais, idade, género, origem ou outros critérios sensíveis.
        - "evidencias_experiencia": lista com até 3 evidências objetivas do currículo (experiência, projeto ou formação) relevantes para a vaga.
        - "recomendacao": próximo passo objetivo para o recrutador. A decisão final deve permanecer humana.
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
                analise = {
                    "competencias_alinhadas": self._lista_limitada(result.get("competencias_alinhadas"), 5),
                    "requisitos_em_falta": self._lista_limitada(result.get("requisitos_em_falta"), 5),
                    "evidencias_experiencia": self._lista_limitada(result.get("evidencias_experiencia"), 3),
                    "recomendacao": str(result.get("recomendacao") or "Reveja o currículo e decida o próximo passo de forma humana."),
                }
                return max(0.0, min(100.0, score)), justificativa, analise
            except Exception as e:
                if attempt < 2 and ("503" in str(e) or "UNAVAILABLE" in str(e) or "429" in str(e)):
                    time.sleep(1.5 * (attempt + 1))
                    continue
                print(f"Erro ao avaliar candidatura com Gemini: {e}")
                return 50.0, "Não foi possível gerar a justificativa detalhada devido a uma instabilidade temporária na API.", self._analise_padrao()

        return 50.0, "Análise concluída com pontuação padrão.", self._analise_padrao()

    def calcular_match_score(self, curriculo_texto: str, vaga_descricao: str, vaga_requisitos: list[str]) -> float:
        score, _, _ = self.avaliar_candidatura(curriculo_texto, vaga_descricao, vaga_requisitos)
        return score

    def gerar_roteiro_entrevista(self, vaga_descricao: str, vaga_requisitos: list[str], perfil_candidato: str, analise_match: dict | None = None) -> list[dict]:
        """Gera perguntas de apoio; nunca usa atributos pessoais ou decide a contratação."""
        if not self.client:
            return self._roteiro_padrao(vaga_requisitos)
        prompt = f"""
        Atue como apoio a um recrutador. Crie exatamente cinco perguntas para uma entrevista justa.
        Não pergunte sobre idade, género, religião, origem, saúde, estado civil, gravidez ou outros dados sensíveis.
        VAGA: {vaga_descricao}\nREQUISITOS: {', '.join(vaga_requisitos)}\nPERFIL DO CANDIDATO: {perfil_candidato}\nANÁLISE ANTERIOR: {json.dumps(analise_match or {}, ensure_ascii=False)}
        Combine perguntas sobre experiência comprovável, competências da vaga, resolução de problemas, colaboração e motivação.
        Para cada pergunta, indique um critério objetivo de avaliação. A decisão final é humana.
        """
        try:
            response = self.client.models.generate_content(model=self.model_name, contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=RoteiroEntrevistaSchema, temperature=0.25))
            dados = json.loads(response.text)
            perguntas = dados.get("perguntas", [])
            resultado = [{"pergunta": str(item.get("pergunta", "")).strip(), "criterio_avaliacao": str(item.get("criterio_avaliacao", "")).strip(), "nota": None, "observacao": ""} for item in perguntas]
            return [item for item in resultado if item["pergunta"] and item["criterio_avaliacao"]][:5] or self._roteiro_padrao(vaga_requisitos)
        except Exception as e:
            print(f"Erro ao gerar roteiro de entrevista com Gemini: {e}")
            return self._roteiro_padrao(vaga_requisitos)

    @staticmethod
    def _roteiro_padrao(requisitos: list[str]) -> list[dict]:
        requisito = requisitos[0] if requisitos else "os principais requisitos desta vaga"
        return [
            {"pergunta": f"Conte sobre uma experiência prática relevante para {requisito}.", "criterio_avaliacao": "Procure contexto, ação concreta e resultado verificável.", "nota": None, "observacao": ""},
            {"pergunta": "Descreva um problema profissional complexo que resolveu e como tomou decisões.", "criterio_avaliacao": "Avalie raciocínio, autonomia e clareza na solução.", "nota": None, "observacao": ""},
            {"pergunta": "Como colabora com colegas e comunica riscos ou bloqueios?", "criterio_avaliacao": "Avalie comunicação, responsabilidade e trabalho em equipa.", "nota": None, "observacao": ""},
            {"pergunta": "Que aprendizagem recente aplicou no seu trabalho ou projeto?", "criterio_avaliacao": "Procure curiosidade e capacidade de evolução profissional.", "nota": None, "observacao": ""},
            {"pergunta": "O que o atrai nesta função e como pretende gerar impacto?", "criterio_avaliacao": "Avalie motivação relacionada com a função e entendimento da vaga.", "nota": None, "observacao": ""},
        ]

    @staticmethod
    def _lista_limitada(valor, limite: int) -> list[str]:
        if not isinstance(valor, list):
            return []
        return [str(item).strip() for item in valor if str(item).strip()][:limite]

    @staticmethod
    def _analise_padrao() -> dict:
        return {
            "competencias_alinhadas": [],
            "requisitos_em_falta": [],
            "evidencias_experiencia": [],
            "recomendacao": "Aguarde uma nova análise ou reveja o currículo manualmente.",
        }

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
