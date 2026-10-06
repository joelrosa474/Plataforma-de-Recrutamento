import logging
from src.domain.entities.candidatura import Candidatura
from src.application.ports.candidatura_repository import CandidaturaRepository
from src.application.ports.vaga_repository import VagaRepository
from src.application.ports.ai_screener_port import AIScreenerPort

logger = logging.getLogger("rh_api")


class RealizarCandidaturaUseCase:
    def __init__(self,
                 candidatura_repo: CandidaturaRepository,
                 vaga_repo: VagaRepository,
                 ai_screener: AIScreenerPort):
        self.candidatura_repo = candidatura_repo
        self.vaga_repo = vaga_repo
        self.ai_screener = ai_screener

    def aplicar_para_vaga(self, vaga_id: int, candidato_id: int, curriculo_texto: str = "", curriculo_path: str = "", curriculo_nome: str = "", processar_ia: bool = True) -> Candidatura:
        if not curriculo_texto or not curriculo_texto.strip():
            raise ValueError("É obrigatório anexar um currículo válido para candidatar-se.")

        vaga = self.vaga_repo.buscar_por_id(vaga_id)
        if not vaga or vaga.status != "Aberta":
            raise ValueError("Vaga não encontrada ou não está aberta para novas candidaturas.")
        if any(c.vaga_id == vaga_id for c in self.candidatura_repo.buscar_por_candidato(candidato_id)):
            raise ValueError("Já existe uma candidatura sua para esta vaga.")

        nova_candidatura = Candidatura(
            vaga_id=vaga_id,
            candidato_id=candidato_id,
            curriculo_path=curriculo_path or None,
            curriculo_nome=curriculo_nome or None
        )

        salva = self.candidatura_repo.salvar(nova_candidatura)

        if processar_ia and self.ai_screener:
            try:
                if hasattr(self.ai_screener, "avaliar_candidatura"):
                    score, feedback = self.ai_screener.avaliar_candidatura(
                        curriculo_texto=curriculo_texto,
                        vaga_descricao=vaga.descricao,
                        vaga_requisitos=vaga.requisitos
                    )
                    salva.registrar_score(score, feedback)
                else:
                    score = self.ai_screener.calcular_match_score(
                        curriculo_texto=curriculo_texto,
                        vaga_descricao=vaga.descricao,
                        vaga_requisitos=vaga.requisitos
                    )
                    salva.registrar_score(score)

                if score >= 85.0:
                    salva.avancar_fase("Entrevista")
                salva = self.candidatura_repo.salvar(salva)
            except Exception as e:
                logger.warning(f"Erro síncrono ao calcular match_score com IA: {e}")

        return salva

    def processar_triagem_ia(self, candidatura_id: int, curriculo_texto: str) -> Candidatura | None:
        """Processa a análise da IA em segundo plano (background worker) sem bloquear a API."""
        candidatura = self.candidatura_repo.buscar_por_id(candidatura_id)
        if not candidatura:
            return None
        vaga = self.vaga_repo.buscar_por_id(candidatura.vaga_id)
        if not vaga:
            return None

        try:
            if hasattr(self.ai_screener, "avaliar_candidatura"):
                score, feedback = self.ai_screener.avaliar_candidatura(
                    curriculo_texto=curriculo_texto,
                    vaga_descricao=vaga.descricao,
                    vaga_requisitos=vaga.requisitos
                )
                candidatura.registrar_score(score, feedback)
            else:
                score = self.ai_screener.calcular_match_score(
                    curriculo_texto=curriculo_texto,
                    vaga_descricao=vaga.descricao,
                    vaga_requisitos=vaga.requisitos
                )
                candidatura.registrar_score(score)

            if score >= 85.0:
                candidatura.avancar_fase("Entrevista")
            salva = self.candidatura_repo.salvar(candidatura)
            logger.info(f"Triagem de IA concluída para candidatura {candidatura_id}. Score: {score}")
            return salva
        except Exception as e:
            logger.error(f"Erro em background task de IA para candidatura {candidatura_id}: {e}")
            return candidatura

    def listar_candidatos_da_vaga(self, vaga_id: int) -> list[Candidatura]:
        return self.candidatura_repo.buscar_por_vaga(vaga_id)

    def listar_candidaturas_do_candidato(self, candidato_id: int) -> list[Candidatura]:
        return self.candidatura_repo.buscar_por_candidato(candidato_id)

    def atualizar_fase(self, candidatura_id: int, nova_fase: str) -> Candidatura | None:
        candidatura = self.candidatura_repo.buscar_por_id(candidatura_id)
        if not candidatura:
            return None
        candidatura.avancar_fase(nova_fase)
        return self.candidatura_repo.salvar(candidatura)
