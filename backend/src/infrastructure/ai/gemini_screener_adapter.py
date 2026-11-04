import os
import re
import json
import logging
import time
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from src.application.ports.ai_screener_port import AIScreenerPort

logger = logging.getLogger("rh_api")


# ── Schemas de resposta estruturada ──────────────────────────────────────────

class HabilidadesSchema(BaseModel):
    habilidades: list[str] = Field(description="Lista de habilidades tecnicas e comportamentais extraidas do curriculo.")


class MatchScoreSchema(BaseModel):
    score: float = Field(description="Pontuacao de 0.0 a 100.0 indicando o fit do candidato com a vaga.")
    justificativa: str = Field(description="Breve explicacao do porque desta nota.")
    competencias_alinhadas: list[str] = Field(description="Ate cinco competencias ou evidencias do curriculo que atendem a vaga.")
    requisitos_em_falta: list[str] = Field(description="Ate cinco requisitos que nao foram encontrados claramente no curriculo.")
    evidencias_experiencia: list[str] = Field(description="Ate tres experiencias, projetos ou formacoes do curriculo relevantes para a vaga.")
    recomendacao: str = Field(description="Recomendacao concisa e neutra para o recrutador sobre o proximo passo.")


class PerguntaEntrevistaSchema(BaseModel):
    pergunta: str = Field(description="Pergunta objetiva e profissional para a entrevista.")
    criterio_avaliacao: str = Field(description="O que o entrevistador deve procurar na resposta.")


class RoteiroEntrevistaSchema(BaseModel):
    perguntas: list[PerguntaEntrevistaSchema] = Field(description="Cinco perguntas personalizadas, justas e relevantes.")


class ValidacaoDocumentoSchema(BaseModel):
    e_curriculo: bool = Field(description="True se o documento for claramente um curriculo vitae ou CV. False caso contrario.")
    motivo: str = Field(description="Explicacao curta do por que e ou nao e um curriculo.")


# ── Palavras-chave de CV em PT e EN (verificação offline sem IA) ─────────────
_PALAVRAS_CV = [
    # Português
    "experiencia", "experiência", "formacao", "formação", "habilitacoes", "habilitações",
    "competencias", "competências", "habilidades", "curriculo", "currículo",
    "objetivo profissional", "objetivo", "perfil profissional", "perfil",
    "educacao", "educação", "licenciatura", "mestrado", "doutoramento", "bacharel",
    "estagio", "estágio", "trabalho", "emprego", "cargo", "funcao", "função",
    "referencia", "referência", "idiomas", "lingua", "língua", "certificado", "certificacao",
    "realizacoes", "realizações", "conquistas", "projetos", "projecto",
    # Inglês (CVs em inglês também são aceites)
    "experience", "education", "skills", "objective", "summary", "profile",
    "employment", "work history", "qualifications", "achievements", "references",
    "degree", "bachelor", "master", "internship", "volunteer", "languages",
]

# Palavras que fortemente indicam que NÃO é CV
_PALAVRAS_NAO_CV = [
    "fatura", "factura", "invoice", "nif do fornecedor", "iban", "valor total",
    "contrato de", "contrato entre", "agreement between", "whereas", "terms and conditions",
    "termos e condicoes", "termos e condições", "clausula", "cláusula", "artigo n.",
    "valor a pagar", "montante", "desconto", "iva", "total a pagar",
    "relatorio", "relatório", "abstract", "keywords", "introduction", "conclusion",
    "bibliography", "references cited", "doi:", "journal of",
]


class GeminiScreenerAdapter(AIScreenerPort):
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY nao encontrada. IA desativada.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

        # Modelo oficial estavel. Pode ser sobrescrito via variavel GEMINI_MODEL.
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        logger.info(f"[Gemini] Adaptador inicializado. Modelo: {self.model_name}")

    # ── Verificação primária por texto (sem IA, sempre disponível) ───────────

    @staticmethod
    def _verificar_por_texto(texto: str) -> tuple[bool | None, str]:
        """
        Verificação rápida offline por palavras-chave.
        Retorna:
          (True,  motivo) → claramente um CV
          (False, motivo) → claramente NÃO é um CV
          (None,  "")     → inconclusivo — deve chamar a IA
        """
        if not texto or len(texto.strip()) < 30:
            return False, "Documento vazio ou sem texto suficiente para ser um curriculo."

        texto_lower = texto.lower()

        # Eliminar imediatamente documentos com forte sinal negativo
        negativos = [p for p in _PALAVRAS_NAO_CV if p in texto_lower]
        if len(negativos) >= 3:
            return False, (
                f"O documento parece ser um documento financeiro/juridico/academico "
                f"(encontradas as palavras: {', '.join(negativos[:3])})."
            )

        # Contar palavras-chave de CV
        positivos = [p for p in _PALAVRAS_CV if p in texto_lower]
        if len(positivos) >= 4:
            return True, f"Documento reconhecido como CV por palavras-chave ({len(positivos)} correspondencias)."

        # Inconclusivo — precisa de IA
        return None, ""

    # ── Verificação completa (texto + IA como segundo nível) ─────────────────

    def verificar_se_e_curriculo(self, texto_documento: str) -> tuple[bool, str]:
        """
        Verifica se o PDF submetido é um currículo vitae.
        Estratégia em dois níveis:
          1. Verificação offline por palavras-chave (sem IA, instantânea)
          2. Se inconclusivo, chama o Gemini para classificação definitiva
        Retorna (True, motivo) se CV, (False, motivo) se NÃO é CV.
        Em caso de falha total da IA, usa o resultado offline como desempate conservador.
        """
        # Nível 1 — verificação por palavras-chave (sem chamada de rede)
        resultado_texto, motivo_texto = self._verificar_por_texto(texto_documento)

        if resultado_texto is False:
            # Documento claramente inválido mesmo sem IA
            logger.warning(f"[Gemini] Documento rejeitado por heuristica offline: {motivo_texto}")
            return False, motivo_texto

        if resultado_texto is True and not self.client:
            # IA desativada mas texto parece ser CV — aceitar
            return True, motivo_texto

        # Nível 2 — verificação por IA (Gemini)
        if not self.client:
            # Sem IA e heurística inconclusiva → aceitar por benefício da dúvida
            return True, "Verificacao automatica desativada (IA nao configurada). Triagem normal aplicada."

        texto_truncado = texto_documento[:3000]
        prompt = f"""Analise o texto extraido de um PDF submetido por um candidato a emprego.
Determine com rigor se o documento e um CURRICULO VITAE (CV).

Um curriculo vitae contem tipicamente: nome e contacto do candidato, experiencia profissional,
formacao academica, competencias ou habilidades, e opcionalmente objectivos profissionais.

NAO e curriculo: cartas de apresentacao sem historial profissional, contratos, faturas,
documentos juridicos, apresentacoes, relatorios, artigos cientificos, documentos em branco.

TEXTO DO DOCUMENTO:
{texto_truncado}

Responda apenas com o JSON solicitado."""

        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ValidacaoDocumentoSchema,
                        temperature=0.1,
                    ),
                )
                result = json.loads(response.text)
                e_curriculo = bool(result.get("e_curriculo", True))
                motivo = str(result.get("motivo", ""))
                logger.info(f"[Gemini] Verificacao de documento: e_curriculo={e_curriculo}, motivo={motivo[:80]}")
                return e_curriculo, motivo
            except Exception as exc:
                err_str = str(exc)
                if attempt < 2 and any(c in err_str for c in ("503", "UNAVAILABLE", "429", "500")):
                    wait = 2.0 * (attempt + 1)
                    logger.warning(f"[Gemini] Verificacao — tentativa {attempt+1}/3 falhou ({err_str[:60]}). Aguardando {wait}s...")
                    time.sleep(wait)
                    continue
                logger.error(f"[Gemini] Falha definitiva na verificacao do documento (modelo: {self.model_name}): {exc}")
                # Fallback: usar o resultado da heuristica de texto
                if resultado_texto is True:
                    return True, f"IA indisponivel. Heuristica aceita o documento como possivel CV ({motivo_texto})."
                # Inconclusivo + IA falhou → aceitar por beneficio da duvida
                return True, "Nao foi possivel verificar o documento. Triagem normal aplicada."

        return True, "Verificacao concluida com resultado padrao."

    # ── Avaliação de candidatura ──────────────────────────────────────────────

    def avaliar_candidatura(self, curriculo_texto: str, vaga_descricao: str, vaga_requisitos: list[str]) -> tuple[float, str, dict]:
        if not self.client:
            return 50.0, "Analise automatica desativada (chave de IA nao configurada).", self._analise_padrao()

        prompt = f"""Atue como um recrutador tecnico experiente e analitico.
Avalie a aderencia do candidato a vaga de emprego especificada.

DADOS DA VAGA:
Descricao: {vaga_descricao}
Requisitos: {', '.join(vaga_requisitos)}

CURRICULO DO CANDIDATO:
{curriculo_texto}

Avalie o quao bem o curriculo atende aos requisitos e a descricao da vaga. Retorne:
- "score": nota de 0.0 a 100.0.
- "justificativa": analise concisa e profissional destacando pontos fortes e lacunas tecnicas.
- "competencias_alinhadas": lista com ate 5 competencias comprovadas no curriculo e relevantes para a vaga.
- "requisitos_em_falta": lista com ate 5 requisitos da vaga sem evidencia clara no curriculo.
- "evidencias_experiencia": lista com ate 3 evidencias objetivas (experiencia, projeto ou formacao) relevantes.
- "recomendacao": proximo passo objetivo para o recrutador. A decisao final e humana."""

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
                justificativa = str(result.get("justificativa") or "Avaliacao concluida pela IA.")
                analise = {
                    "competencias_alinhadas": self._lista_limitada(result.get("competencias_alinhadas"), 5),
                    "requisitos_em_falta": self._lista_limitada(result.get("requisitos_em_falta"), 5),
                    "evidencias_experiencia": self._lista_limitada(result.get("evidencias_experiencia"), 3),
                    "recomendacao": str(result.get("recomendacao") or "Reveja o curriculo e decida o proximo passo de forma humana."),
                }
                logger.info(f"[Gemini] Triagem concluida: score={score:.1f}")
                return max(0.0, min(100.0, score)), justificativa, analise
            except Exception as exc:
                err_str = str(exc)
                if attempt < 2 and any(c in err_str for c in ("503", "UNAVAILABLE", "429", "500")):
                    wait = 2.0 * (attempt + 1)
                    logger.warning(f"[Gemini] Triagem — tentativa {attempt+1}/3 falhou. Aguardando {wait}s...")
                    time.sleep(wait)
                    continue
                logger.error(f"[Gemini] Falha definitiva na avaliacao (modelo: {self.model_name}): {exc}")
                return 50.0, "Nao foi possivel gerar a justificativa detalhada devido a uma instabilidade temporaria na API.", self._analise_padrao()

        return 50.0, "Analise concluida com pontuacao padrao.", self._analise_padrao()

    def calcular_match_score(self, curriculo_texto: str, vaga_descricao: str, vaga_requisitos: list[str]) -> float:
        score, _, _ = self.avaliar_candidatura(curriculo_texto, vaga_descricao, vaga_requisitos)
        return score

    # ── Roteiro de entrevista ─────────────────────────────────────────────────

    def gerar_roteiro_entrevista(self, vaga_descricao: str, vaga_requisitos: list[str], perfil_candidato: str, analise_match: dict | None = None) -> list[dict]:
        """Gera perguntas de apoio; nunca usa atributos pessoais ou decide a contratacao."""
        if not self.client:
            return self._roteiro_padrao(vaga_requisitos)
        prompt = (
            f"Atue como apoio a um recrutador. Crie exatamente cinco perguntas para uma entrevista justa.\n"
            f"Nao pergunte sobre idade, genero, religiao, origem, saude, estado civil, gravidez ou outros dados sensiveis.\n"
            f"VAGA: {vaga_descricao}\nREQUISITOS: {', '.join(vaga_requisitos)}\n"
            f"PERFIL DO CANDIDATO: {perfil_candidato}\nANALISE ANTERIOR: {json.dumps(analise_match or {}, ensure_ascii=False)}\n"
            "Combine perguntas sobre experiencia comprovavel, competencias da vaga, resolucao de problemas, colaboracao e motivacao.\n"
            "Para cada pergunta, indique um criterio objetivo de avaliacao. A decisao final e humana."
        )
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=RoteiroEntrevistaSchema,
                    temperature=0.25,
                ),
            )
            dados = json.loads(response.text)
            perguntas = dados.get("perguntas", [])
            resultado = [
                {
                    "pergunta": str(item.get("pergunta", "")).strip(),
                    "criterio_avaliacao": str(item.get("criterio_avaliacao", "")).strip(),
                    "nota": None,
                    "observacao": "",
                }
                for item in perguntas
            ]
            return [i for i in resultado if i["pergunta"] and i["criterio_avaliacao"]][:5] or self._roteiro_padrao(vaga_requisitos)
        except Exception as exc:
            logger.error(f"[Gemini] Erro ao gerar roteiro de entrevista: {exc}")
            return self._roteiro_padrao(vaga_requisitos)

    # ── Extração de habilidades ───────────────────────────────────────────────

    def extrair_habilidades(self, curriculo_texto: str) -> list[str]:
        if not self.client:
            return []
        prompt = (
            f"Analise o seguinte curriculo e extraia todas as habilidades (skills) tecnicas e comportamentais.\n"
            f"Retorne uma lista limpa e padronizada.\n\nCURRICULO:\n{curriculo_texto}"
        )
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
            except Exception as exc:
                if attempt < 2 and any(c in str(exc) for c in ("503", "UNAVAILABLE", "429")):
                    time.sleep(1.5 * (attempt + 1))
                    continue
                logger.error(f"[Gemini] Erro ao extrair habilidades: {exc}")
                return []
        return []

    # ── Helpers estáticos ─────────────────────────────────────────────────────

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
            "recomendacao": "Aguarde uma nova analise ou reveja o curriculo manualmente.",
        }

    @staticmethod
    def _roteiro_padrao(requisitos: list[str]) -> list[dict]:
        req = requisitos[0] if requisitos else "os principais requisitos desta vaga"
        return [
            {"pergunta": f"Conte sobre uma experiencia pratica relevante para {req}.", "criterio_avaliacao": "Procure contexto, acao concreta e resultado verificavel.", "nota": None, "observacao": ""},
            {"pergunta": "Descreva um problema profissional complexo que resolveu e como tomou decisoes.", "criterio_avaliacao": "Avalie raciocinio, autonomia e clareza na solucao.", "nota": None, "observacao": ""},
            {"pergunta": "Como colabora com colegas e comunica riscos ou bloqueios?", "criterio_avaliacao": "Avalie comunicacao, responsabilidade e trabalho em equipa.", "nota": None, "observacao": ""},
            {"pergunta": "Que aprendizagem recente aplicou no seu trabalho ou projeto?", "criterio_avaliacao": "Procure curiosidade e capacidade de evolucao profissional.", "nota": None, "observacao": ""},
            {"pergunta": "O que o atrai nesta funcao e como pretende gerar impacto?", "criterio_avaliacao": "Avalie motivacao relacionada com a funcao e entendimento da vaga.", "nota": None, "observacao": ""},
        ]
