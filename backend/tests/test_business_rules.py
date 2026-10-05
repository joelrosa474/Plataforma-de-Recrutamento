import unittest

from src.application.use_cases.autenticacao import AutenticacaoUseCase
from src.application.use_cases.realizar_candidatura import RealizarCandidaturaUseCase
from src.domain.entities.candidatura import Candidatura
from src.domain.entities.vaga import Vaga
from src.infrastructure.repositories.candidatura_repository_memory import CandidaturaRepositoryMemory
from src.infrastructure.repositories.usuario_repository_memory import UsuarioRepositoryMemory
from src.infrastructure.repositories.vaga_repository_memory import VagaRepositoryMemory


class FakeAIScreener:
    def calcular_match_score(self, curriculo_texto: str, vaga_descricao: str, vaga_requisitos: list[str]) -> float:
        return 90.0

    def extrair_habilidades(self, curriculo_texto: str) -> list[str]:
        return ["python"]


class TestBusinessRules(unittest.TestCase):
    def test_registrar_rejeita_email_invalido(self):
        repo = UsuarioRepositoryMemory()
        use_case = AutenticacaoUseCase(repo)

        with self.assertRaisesRegex(ValueError, "E-mail inválido"):
            use_case.registrar("Ana Silva", "email-invalido", "senha123", "Candidato")

    def test_aplicar_para_vaga_rejeita_curriculo_vazio(self):
        vaga_repo = VagaRepositoryMemory()
        candidatura_repo = CandidaturaRepositoryMemory()
        vaga_repo.salvar(Vaga(id=1, empresa_id=10, titulo="Analista", descricao="Trabalhar com dados", requisitos=["Python"], status="Aberta"))
        use_case = RealizarCandidaturaUseCase(candidatura_repo, vaga_repo, FakeAIScreener())

        with self.assertRaisesRegex(ValueError, "currículo"):
            use_case.aplicar_para_vaga(vaga_id=1, candidato_id=99, curriculo_texto="   ")

    def test_atualizar_fase_rejeita_transicao_invalida(self):
        candidatura_repo = CandidaturaRepositoryMemory()
        vaga_repo = VagaRepositoryMemory()
        candidatura = Candidatura(id=1, vaga_id=7, candidato_id=5, fase_atual="Triagem")
        candidatura_repo.salvar(candidatura)
        use_case = RealizarCandidaturaUseCase(candidatura_repo, vaga_repo, FakeAIScreener())

        with self.assertRaisesRegex(ValueError, "Transição de fase inválida"):
            use_case.atualizar_fase(1, "Contratado")

    def test_aplicar_para_vaga_salva_metadados_curriculo(self):
        vaga_repo = VagaRepositoryMemory()
        candidatura_repo = CandidaturaRepositoryMemory()
        vaga_repo.salvar(Vaga(id=1, empresa_id=10, titulo="Dev Python", descricao="Desenvolvimento backend", requisitos=["Python"], status="Aberta"))
        use_case = RealizarCandidaturaUseCase(candidatura_repo, vaga_repo, FakeAIScreener())

        cand = use_case.aplicar_para_vaga(
            vaga_id=1,
            candidato_id=15,
            curriculo_texto="Experiência com Python",
            curriculo_path="/tmp/cv15.pdf",
            curriculo_nome="meu_curriculo.pdf"
        )
        self.assertEqual(cand.curriculo_path, "/tmp/cv15.pdf")
        self.assertEqual(cand.curriculo_nome, "meu_curriculo.pdf")
        self.assertEqual(cand.match_score, 90.0)
        self.assertEqual(cand.fase_atual, "Entrevista")

    def test_aplicar_para_vaga_sem_ia_imediata_e_depois_processa_background(self):
        vaga_repo = VagaRepositoryMemory()
        candidatura_repo = CandidaturaRepositoryMemory()
        vaga_salva = vaga_repo.salvar(Vaga(empresa_id=10, titulo="Dev React", descricao="Desenvolvimento frontend", requisitos=["React"], status="Aberta"))
        use_case = RealizarCandidaturaUseCase(candidatura_repo, vaga_repo, FakeAIScreener())

        cand = use_case.aplicar_para_vaga(
            vaga_id=vaga_salva.id,
            candidato_id=20,
            curriculo_texto="Experiência com React e TypeScript",
            curriculo_path="/tmp/cv20.pdf",
            curriculo_nome="cv.pdf",
            processar_ia=False  # Simula submissão assíncrona
        )
        self.assertIsNone(cand.match_score)
        self.assertEqual(cand.fase_atual, "Triagem")

        # Agora simula o worker de background processando a IA
        atualizada = use_case.processar_triagem_ia(cand.id, "Experiência com React e TypeScript")
        self.assertIsNotNone(atualizada)
        self.assertEqual(atualizada.match_score, 90.0)
        self.assertEqual(atualizada.fase_atual, "Entrevista")


if __name__ == "__main__":
    unittest.main()
