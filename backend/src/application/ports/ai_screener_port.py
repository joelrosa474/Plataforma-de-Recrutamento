from abc import ABC, abstractmethod

class AIScreenerPort(ABC):
    @abstractmethod
    def calcular_match_score(self, curriculo_texto: str, vaga_descricao: str, vaga_requisitos: list[str]) -> float:
        """
        Recebe o texto de um currículo e os dados da vaga,
        e retorna uma pontuação de 0.0 a 100.0 indicando o fit.
        """
        pass

    @abstractmethod
    def avaliar_candidatura(self, curriculo_texto: str, vaga_descricao: str, vaga_requisitos: list[str]) -> tuple[float, str]:
        """
        Avalia o currículo em profundidade e retorna (score, parecer_justificativa).
        """
        pass
    
    @abstractmethod
    def extrair_habilidades(self, curriculo_texto: str) -> list[str]:
        """
        Analisa um currículo bruto e retorna uma lista padronizada de habilidades.
        """
        pass
