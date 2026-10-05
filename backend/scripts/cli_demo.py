import sys
import os

# Garante que a pasta backend está no PYTHONPATH para permitir as importações do 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.infrastructure.repositories.vaga_repository_memory import VagaRepositoryMemory
from src.infrastructure.repositories.candidatura_repository_memory import CandidaturaRepositoryMemory
from src.application.ports.ai_screener_port import AIScreenerPort


class ScreenerAgentMock(AIScreenerPort):
    def calcular_match_score(self, curriculo_texto: str, vaga_descricao: str, vaga_requisitos: list[str]) -> float:
        return 90.0

    def extrair_habilidades(self, curriculo_texto: str) -> list[str]:
        return [r for r in vaga_requisitos if r.lower() in curriculo_texto.lower()]


from src.application.use_cases.gerenciar_vagas import GerenciarVagasUseCase
from src.application.use_cases.realizar_candidatura import RealizarCandidaturaUseCase

def main():
    # Instanciando dependências (A mágica da Arquitetura Hexagonal: rodamos o sistema sem precisar de internet ou banco!)
    vaga_repo = VagaRepositoryMemory()
    cand_repo = CandidaturaRepositoryMemory()
    ai_screener = ScreenerAgentMock()
    
    vagas_use_case = GerenciarVagasUseCase(vaga_repo)
    cand_use_case = RealizarCandidaturaUseCase(cand_repo, vaga_repo, ai_screener)

    print("\n" + "="*50)
    print(" 🚀 PLATAFORMA DE RECRUTAMENTO (CLI de Testes)")
    print("="*50)
    
    while True:
        print("\nEscolha uma opção:")
        print("  1. Criar Nova Vaga (Visão RH)")
        print("  2. Listar Vagas Abertas")
        print("  3. Enviar Currículo para uma Vaga (Visão Candidato)")
        print("  4. Ver Funil de Candidatos de uma Vaga (Visão RH)")
        print("  0. Sair")
        
        opcao = input("\n> ")
        
        if opcao == "1":
            print("\n--- Nova Vaga ---")
            titulo = input("Título da vaga: ")
            descricao = input("Descrição rápida: ")
            reqs = input("Requisitos (separados por vírgula): ")
            requisitos = [r.strip() for r in reqs.split(",") if r.strip()]
            vaga = vagas_use_case.criar_vaga(empresa_id=1, titulo=titulo, descricao=descricao, requisitos=requisitos)
            print(f"✅ Vaga '{vaga.titulo}' criada com sucesso! (ID da Vaga: {vaga.id})")
            
        elif opcao == "2":
            print("\n--- Vagas Abertas ---")
            vagas = vagas_use_case.listar_vagas_abertas()
            if not vagas:
                print("Nenhuma vaga aberta no momento.")
            else:
                for v in vagas:
                    print(f" [ID: {v.id}] {v.titulo} -> Requisitos: {', '.join(v.requisitos)}")
                    
        elif opcao == "3":
            print("\n--- Envio de Currículo ---")
            try:
                vaga_id = int(input("Digite o ID da Vaga que deseja se aplicar: "))
                candidato_id = 101 # ID fictício para o teste
                
                print("Escreva um resumo das suas habilidades (seu currículo simulado):")
                print("(Exemplo: 'Sou desenvolvedor, sei programar em python e react, e tenho boa liderança')")
                curriculo = input("Currículo: ")
                
                print("\nEnviando currículo... Processando pela IA...")
                candidatura = cand_use_case.aplicar_para_vaga(vaga_id, candidato_id, curriculo)
                
                print(f"\n✅ Candidatura realizada com sucesso!")
                print(f"🤖 Resultado da IA Screener (Match Score): {candidatura.match_score}%")
                print(f"📊 Status atual do candidato no funil: {candidatura.fase_atual}")
                
            except ValueError as e:
                print(f"❌ Erro ao enviar: {e}")
            except Exception as e:
                print("❌ ID inválido.")
                
        elif opcao == "4":
            print("\n--- Funil de Candidatos ---")
            try:
                vaga_id = int(input("Digite o ID da Vaga para ver os candidatos: "))
                candidatos = cand_use_case.listar_candidatos_da_vaga(vaga_id)
                if not candidatos:
                    print("Nenhum candidato aplicou para esta vaga ainda.")
                else:
                    for c in candidatos:
                        print(f" - Candidato #{c.candidato_id} | Status: {c.fase_atual} | Match IA: {c.match_score}%")
            except Exception as e:
                print("❌ ID inválido.")
                
        elif opcao == "0":
            print("Saindo do terminal...")
            sys.exit(0)
        else:
            print("❌ Opção inválida, tente novamente.")

if __name__ == "__main__":
    main()
