# 📊 Livro de Diagramas Técnicos do Sistema — É Salú (Recrutamento RH)

Este documento reúne todos os diagramas visuais da arquitetura, fluxos de dados, processos de negócio, banco de dados e pipelines do sistema **É Salú**.

Todos os diagramas foram modelados utilizando a sintaxe **Mermaid**, sendo renderizados nativamente pelo GitHub, GitLab e na maioria dos editores Markdown.

---

## Índice dos Diagramas

1. [Diagrama 1: Arquitetura Geral da Solução (Visão de Infraestrutura & Nuvem)](#1-arquitetura-geral-da-solução)
2. [Diagrama 2: Modelo Entidade-Relacionamento (DER / Banco de Dados)](#2-modelo-entidade-relacionamento-der)
3. [Diagrama 3: Fluxo de Autenticação, Registro e RBAC (JWT)](#3-fluxo-de-autenticação-e-autorização-jwt)
4. [Diagrama 4: Fluxo de Triagem Inteligente com IA (Google Gemini 1.5)](#4-fluxo-de-triagem-inteligente-com-ia-gemini)
5. [Diagrama 5: Ciclo de Vida da Candidatura no ATS (Máquina de Estados)](#5-ciclo-de-vida-da-candidatura-ats)
6. [Diagrama 6: Ciclo de Vida e Moderação de Vagas](#6-ciclo-de-vida-e-moderação-de-vagas)
7. [Diagrama 7: Arquitetura de Notificações em Tempo Real (SSE - Server-Sent Events)](#7-arquitetura-de-notificações-em-tempo-real-sse)
8. [Diagrama 8: Pipeline de Integração Contínua e Deploy (CI/CD)](#8-pipeline-de-integração-contínua-e-deploy-cicd)
9. [Diagrama 9: Mapa de Navegação e Responsividade da Interface (Frontend)](#9-mapa-de-navegação-e-rotas-frontend)
10. [Diagrama 10: Diagrama de Classes UML (Clean Architecture)](#10-diagrama-de-classes-uml)
11. [Diagrama 11: Diagrama de Casos de Uso (Atores & Funcionalidades)](#11-diagrama-de-casos-de-uso)
12. [Diagrama 12: Diagramas de Atividades (Processos de Negócio)](#12-diagramas-de-atividades)

---

## 1. Arquitetura Geral da Solução

Representa os componentes do ecossistema e a divisão de responsabilidades entre cliente, frontend estático/dinâmico, API assíncrona, microsserviço de IA e persistência gerenciada.

```mermaid
flowchart TB
    subgraph Clients ["Dispositivos de Acesso"]
        M[Smartphone iOS / Android]
        T[Tablet iPad / Android]
        D[Desktop / Laptop]
    end

    subgraph Edge ["Camada de Borda & DNS"]
        CF["Cloudflare (DNS Anycast & SSL Full Strict)"]
    end

    subgraph FrontendPlatform ["Frontend Hosting (Vercel)"]
        NextApp["Next.js 16 Webapp\n(React 18 + Tailwind CSS)"]
        StaticPages["Páginas Prerenderizadas (SSG)"]
        DynamicRoutes["Rotas Dinâmicas (SSR)"]
        RouteGuard["Controle de Acesso (RouteGuard)"]
    end

    subgraph BackendPlatform ["Backend Hosting (Render.com)"]
        FastAPI["FastAPI App (Python 3.12+)"]
        AuthModule["Módulo de Autenticação & JWT"]
        JobModule["Módulo de Vagas & Moderação"]
        AppModule["Módulo ATS & Candidaturas"]
        NotificationModule["Broadcaster SSE (Thread-Safe Queue)"]
    end

    subgraph ExternalServices ["Serviços Externos & IA"]
        Gemini["Google Gemini 1.5 Studio API\n(Triagem Semântica de CVs)"]
        Resend["Resend API / SMTP\n(E-mails Transacionais)"]
    end

    subgraph DatabaseLayer ["Camada de Dados & Persistência"]
        PG[(PostgreSQL 16 Gerenciado)]
        Alembic["Migrações de Schema (Alembic)"]
        LocalFiles["Armazenamento de PDFs"]
    end

    Clients -->|HTTPS / Porta 443| CF
    CF --> NextApp
    NextApp --> RouteGuard
    RouteGuard --> StaticPages
    RouteGuard --> DynamicRoutes

    NextApp -->|Chamadas REST JSON / API| FastAPI
    NextApp -->|EventSource SSE /api/notificacoes/stream| NotificationModule

    FastAPI --> AuthModule
    FastAPI --> JobModule
    FastAPI --> AppModule

    AppModule -->|Upload de PDF| LocalFiles
    AppModule -->|Extração de Texto + Prompt| Gemini
    AppModule -->|Alerta de Fase| Resend
    AppModule -->|Broadcast em Memória| NotificationModule

    AuthModule --> PG
    JobModule --> PG
    AppModule --> PG
    Alembic -->|Gerencia Schema| PG
```

---

## 2. Modelo Entidade-Relacionamento (DER)

Estrutura das tabelas, chaves primárias, tipos de dados, chaves estrangeiras e integridade referencial mantidas no PostgreSQL e mapeadas pelo SQLAlchemy 2.0.

```mermaid
erDiagram
    USUARIOS ||--o{ VAGAS : "publica (empresa_id)"
    USUARIOS ||--o{ CANDIDATURAS : "submete (candidato_id)"
    USUARIOS ||--o{ NOTIFICACOES : "recebe (usuario_id)"
    VAGAS ||--o{ CANDIDATURAS : "recebe (vaga_id)"

    USUARIOS {
        int id PK "Identificador único incremental"
        string nome "Nome completo ou razão social"
        string email UK "E-mail único (indexado)"
        string senha_hash "Hash seguro bcrypt"
        string tipo_perfil "Candidato | Empresa | Administrador"
        string localizacao "Província / Cidade (ex: Luanda)"
        text experiencia "Resumo profissional ou sobre a empresa"
        json competencias "Lista de habilidades em JSON"
        string linkedin_url "Link do perfil LinkedIn"
        string github_url "Link GitHub ou website institucional"
        datetime data_criacao "Data de cadastro no sistema"
    }

    VAGAS {
        int id PK "Identificador único da vaga"
        int empresa_id FK "Referência ao Usuário recrutador"
        string titulo "Título da vaga (ex: Engenheiro Frontend)"
        text descricao "Descrição das responsabilidades"
        string status "Aberta | Pausada | Fechada"
        json requisitos "Lista de competências exigidas em JSON"
        string localizacao "Cidade/Província da vaga"
        string modalidade "Presencial | Híbrido | Remoto"
        string area "Tecnologia | Finanças | RH | Vendas | etc"
        datetime data_criacao "Timestamp de publicação"
    }

    CANDIDATURAS {
        int id PK "Identificador único da candidatura"
        int vaga_id FK "Referência à vaga aplicada"
        int candidato_id FK "Referência ao candidato"
        string fase_atual "Triagem | Entrevista | Contratado | Reprovado"
        float match_score "Pontuação 0-100 calculada pela IA"
        text feedback_ia "Parecer técnico gerado pelo Gemini"
        string curriculo_path "Caminho do arquivo PDF no servidor"
        string curriculo_nome "Nome original do arquivo enviado"
        datetime data_aplicacao "Timestamp de envio da candidatura"
    }

    NOTIFICACOES {
        int id PK "Identificador único da notificação"
        int usuario_id FK "Usuário destinatário"
        string titulo "Título curto do alerta"
        text mensagem "Descrição do evento ocorrido"
        boolean lida "Status de leitura (default: false)"
        datetime data_criacao "Timestamp do envio"
    }
```

---

## 3. Fluxo de Autenticação e Autorização (JWT)

Detalha os processos de registo com dupla confirmação de senha, login com emissão de token criptográfico e validação RBAC nos endpoints protegidos.

```mermaid
sequenceDiagram
    autonumber
    actor U as Utilizador (Browser)
    participant AuthUI as Página /auth (Next.js)
    participant API as FastAPI (/api/auth)
    participant Hash as Bcrypt Hasher
    participant JWT as JWT Service
    participant DB as Base de Dados (PostgreSQL)

    %% Cadastro
    rect rgb(240, 248, 255)
    Note over U,DB: Fluxo 1: Registo de Nova Conta
    U->>AuthUI: Preenche Nome, E-mail, Senha e Confirmação
    AuthUI->>AuthUI: Valida se Senha === Confirmar Senha
    alt Senhas não coincidem
        AuthUI-->>U: Erro: "As palavras-passe não coincidem"
    else Senhas coincidem
        AuthUI->>API: POST /api/auth/register {nome, email, senha, perfil}
        API->>Hash: Trunca para 72 bytes & gera salt/hash
        Hash-->>API: senha_hash
        API->>DB: INSERT INTO usuarios (..., senha_hash)
        DB-->>API: Utilizador Criado
        API-->>AuthUI: 201 Created
    end
    end

    %% Login
    rect rgb(245, 255, 245)
    Note over U,DB: Fluxo 2: Início de Sessão & Emissão de Token
    U->>AuthUI: Informa E-mail e Palavra-passe
    AuthUI->>API: POST /api/auth/login {email, senha}
    API->>DB: SELECT * FROM usuarios WHERE email = ?
    DB-->>API: Registro do Usuário
    API->>Hash: Verifica senha em texto puro com hash
    alt Senha inválida
        API-->>AuthUI: 401 Unauthorized ("Credenciais inválidas")
    else Senha correta
        API->>JWT: Cria token com subject=email, id, perfil e expiração
        JWT-->>API: access_token (HMAC-SHA256)
        API-->>AuthUI: 200 OK {access_token, usuario}
        AuthUI->>AuthUI: Armazena token no localStorage ("rh-session")
        AuthUI-->>U: Redireciona para o Dashboard correspondente
    end
    end
```

---

## 4. Fluxo de Triagem Inteligente com IA (Gemini)

Demonstra a esteira de processamento que analisa currículos em PDF de forma assíncrona, gerando o parecer técnico e a nota de compatibilidade sem bloquear a requisição do usuário.

```mermaid
sequenceDiagram
    autonumber
    actor C as Candidato
    participant W as Frontend (Vercel)
    participant API as FastAPI Backend (Render)
    participant Storage as Armazenamento Local
    participant Parser as Leitor PDF (pypdf)
    participant Gemini as Google Gemini 1.5 API
    participant DB as PostgreSQL
    participant Broadcaster as SSE Broadcaster
    actor E as Empresa (Recrutador)

    C->>W: Seleciona vaga e faz upload do currículo (.pdf)
    W->>API: POST /api/candidaturas (multipart/form-data)
    API->>Storage: Salva PDF em /uploads/{hash}.pdf
    API->>DB: Registra candidatura (fase="Triagem", match_score=null)
    DB-->>API: Candidatura #123 persistida
    API-->>W: 201 Created ("Candidatura enviada com sucesso!")
    W-->>C: Modal de sucesso com confirmação

    Note over API,Gemini: Processamento em Background da Inteligência Artificial
    API->>Parser: Extrai conteúdo de texto das páginas do PDF
    Parser-->>API: Texto limpo do currículo
    API->>Gemini: Prompt estruturado: Requisitos da Vaga + Texto do Currículo
    Note over Gemini: Analisa competências, experiência,<br/>tempo de atuação e lacunas
    Gemini-->>API: Resposta JSON: { "match_score": 87.5, "feedback_ia": "Forte perfil em..." }
    API->>DB: UPDATE candidaturas SET match_score=87.5, feedback_ia=... WHERE id=123
    API->>DB: INSERT INTO notificacoes (usuario_id, titulo, mensagem)
    API->>Broadcaster: Notifica canal da Empresa: "Novo candidato com 88% de aderência"
    Broadcaster-->>E: Evento SSE recebido em tempo real (Toast + Badge animado)
```

---

## 5. Ciclo de Vida da Candidatura (ATS)

Mostra a máquina de estados que governa a evolução do candidato dentro do funil de recrutamento da empresa, detalhando os gatilhos disparados em cada transição de fase.

```mermaid
stateDiagram-v2
    [*] --> Submetida: Candidato envia currículo
    
    Submetida --> Triagem: Processamento automático inicial
    
    state Triagem {
        [*] --> AnaliseIA: IA extrai dados do PDF
        AnaliseIA --> ScoreCalculado: Match Score gerado (0 a 100%)
    }

    Triagem --> Entrevista: Recrutador convoca para entrevista
    note right of Entrevista
        Dispara:
        1. E-mail automático para o candidato
        2. Notificação em tempo real (SSE)
    end note

    Triagem --> Reprovado: Perfil não aderente aos requisitos
    note left of Reprovado
        Dispara e-mail de agradecimento e feedback
    end note

    Entrevista --> Contratado: Candidato aprovado no processo
    note right of Contratado
        Dispara e-mail de boas-vindas / oferta oficial
        e encerra o ciclo positivamente
    end note

    Entrevista --> Reprovado: Candidato não selecionado após entrevista

    Contratado --> [*]
    Reprovado --> [*]
```

---

## 6. Ciclo de Vida e Moderação de Vagas

Diagrama de estados que representa as fases de uma oportunidade de trabalho e as permissões de moderação da empresa e do administrador da plataforma.

```mermaid
stateDiagram-v2
    [*] --> RascunhoForm: Empresa preenche formulário
    RascunhoForm --> Aberta: Publicar vaga (POST /api/vagas)

    state Aberta {
        [*] --> VisivelNoFeed: Disponível na busca pública
        VisivelNoFeed --> RecebendoCandidaturas: Candidatos podem aplicar
    }

    Aberta --> Pausada: Empresa ou Admin clica em "Pausar"
    note right of Pausada
        Vaga não aceita novas inscrições,
        mas candidatos atuais seguem no processo.
    end note

    Pausada --> Aberta: Empresa clica em "Reabrir"

    Aberta --> Fechada: Empresa encerra o processo seletivo
    Pausada --> Fechada: Empresa encerra o processo seletivo

    state Fechada {
        [*] --> ProcessoEncerrado: Histórico arquivado
    }

    Aberta --> Excluida: Empresa ou Admin clica em "Eliminar"
    Pausada --> Excluida: Empresa ou Admin clica em "Eliminar"
    Fechada --> Excluida: Empresa ou Admin clica em "Eliminar"

    Excluida --> [*]
```

---

## 7. Arquitetura de Notificações em Tempo Real (SSE)

Demonstra a conexão persistente e leve mantida entre os navegadores conectados e o servidor FastAPI via Server-Sent Events, garantindo consumo mínimo de banda e atualização instantânea.

```mermaid
sequenceDiagram
    autonumber
    actor User as Navegador do Utilizador (React)
    participant UI as NotificationsPanel.tsx
    participant SSE as FastAPI /api/notificacoes/stream
    participant Broadcaster as NotificationBroadcaster (In-Memory Queue)
    participant Service as Qualquer Serviço da Aplicação

    User->>UI: Abre a aplicação logado
    UI->>SSE: Inicia new EventSource("/stream?token=JWT")
    SSE->>SSE: Valida token JWT e extrai user_id
    SSE->>Broadcaster: Inscreve cliente: register_client(user_id, queue)
    SSE-->>UI: Conexão HTTP 200 mantida com Transfer-Encoding: chunked

    loop Monitoramento Contínuo
        UI->>UI: Mantém ícone com contagem atual de não lidas
    end

    Note over Service,Broadcaster: Evento Ocorre (Ex: Mudança de Fase de Candidatura)
    Service->>Broadcaster: broadcast_to_user(user_id, {id, titulo, mensagem})
    Broadcaster->>SSE: Enfileira mensagem na fila do cliente
    SSE-->>UI: data: {"id": 45, "titulo": "Avanço de Fase", "mensagem": "..."}\n\n
    UI->>UI: 1. Dispara Toast animado flutuante no canto da tela
    UI->>UI: 2. Incrementa badge numérico no sino de notificações
    UI->>UI: 3. Insere a notificação no topo da lista sem recarregar a página
```

---

## 8. Pipeline de Integração Contínua e Deploy (CI/CD)

Demonstra o fluxo automatizado de integração, teste e publicação contínua desde o commit do desenvolvedor até o ambiente de produção.

```mermaid
flowchart LR
    Dev["Desenvolvedor\n(Git Push /main)"] --> Repo["GitHub Repository\njoelrosa474/Plataforma-de-Recrutamento"]

    subgraph GitHubActions ["GitHub Actions (.github/workflows/ci.yml)"]
        direction TB
        TestBackend["Job 1: Testes Backend\n- Python 3.12 Setup\n- Instalação de dependências\n- Execução de 35 testes unitários\n- Validação de regras e Alembic"]
        BuildFrontend["Job 2: Build Frontend\n- Node.js 22 Setup\n- Validação TypeScript\n- Compilação Turbopack / Next.js"]
    end

    subgraph CD_Vercel ["Deploy Contínuo Frontend (Vercel)"]
        VercelHook["Vercel Webhook"]
        VercelBuild["Next.js Production Build"]
        VercelEdge["Publicação Global Edge Network\nhttps://plataforma-de-recrutamento-rouge.vercel.app"]
    end

    subgraph CD_Render ["Deploy Contínuo Backend (Render)"]
        RenderHook["Render Blueprint Webhook"]
        DockerBuild["Docker Multi-Stage Build"]
        DBMigration["Alembic upgrade head (Migrações)"]
        RenderLive["FastAPI API Online\nhttps://rh-backend-api-ulcu.onrender.com"]
    end

    Repo --> GitHubActions
    Repo --> VercelHook
    Repo --> RenderHook

    VercelHook --> VercelBuild --> VercelEdge
    RenderHook --> DockerBuild --> DBMigration --> RenderLive
```

---

## 9. Mapa de Navegação e Rotas (Frontend)

Estrutura de páginas e proteção por rotas implementada no Next.js (App Router), dividida pelos perfis de usuário:

```mermaid
graph TD
    Home["/ (Landing Page Pública)"]
    Auth["/auth (Login, Cadastro & Recuperação)"]

    subgraph CandidateArea ["Área do Candidato (/candidate/*)"]
        C_Dash["/candidate/dashboard\n(Pesquisa de Vagas & Candidatura)"]
        C_Apps["/candidate/applications\n(Minhas Candidaturas & Status)"]
        C_Prof["/candidate/profile\n(Meu Perfil Profissional)"]
    end

    subgraph CompanyArea ["Área da Empresa (/company/*)"]
        E_Dash["/company/dashboard\n(Painel com Métricas de Vagas)"]
        E_Jobs["/company/jobs\n(Criar, Editar e Pausar Vagas)"]
        E_ATS["/company/candidates\n(Funil ATS de Candidatos & Parecer IA)"]
        E_Prof["/company/profile\n(Perfil Institucional da Empresa)"]
        E_Sett["/company/settings\n(Segurança, E-mail e Zona de Perigo)"]
    end

    subgraph AdminArea ["Área do Administrador (/admin/*)"]
        A_Dash["/admin/dashboard\n(KPIs Globais & Monitor de IA)"]
        A_Users["/admin/users\n(Gestão e Moderação de Contas)"]
        A_Jobs["/admin/moderation\n(Moderação e Auditoria de Vagas)"]
    end

    Home -->|Explorar Vagas| C_Dash
    Home -->|Entrar / Criar Conta| Auth

    Auth -->|Perfil: Candidato| C_Dash
    Auth -->|Perfil: Empresa| E_Dash
    Auth -->|Perfil: Administrador| A_Dash

    C_Dash <--> C_Apps
    C_Dash <--> C_Prof

    E_Dash <--> E_Jobs
    E_Dash <--> E_ATS
    E_Dash <--> E_Prof
    E_Dash <--> E_Sett

    A_Dash <--> A_Users
    A_Dash <--> A_Jobs
```

---

## 10. Diagrama de Classes UML

Modela a estrutura orientada a objetos do backend estruturada segundo os princípios da **Clean Architecture** (Arquitetura Limpa), dividida em:
- **Entidades de Domínio (`Domain`):** Modelos puros e desacoplados de frameworks externos.
- **Portas / Interfaces Contratuais (`Ports`):** Contratos de repositórios, serviços de IA e e-mail.
- **Casos de Uso (`Use Cases`):** Orquestração dos fluxos de negócio.
- **Adaptadores Concretos (`Adapters`):** Implementações em SQLAlchemy, Google Gemini, Resend e FastAPI.

```mermaid
classDiagram
    direction TB

    %% Pacote de Domínio
    class Usuario {
        +int id
        +string nome
        +string email
        +string senha_hash
        +string tipo_perfil
        +string localizacao
        +string experiencia
        +List~string~ competencias
        +string linkedin_url
        +string github_url
        +datetime data_criacao
        +verificar_senha(senha_pura: str) bool
        +is_administrador() bool
        +is_empresa() bool
        +is_candidato() bool
    }

    class Vaga {
        +int id
        +int empresa_id
        +string titulo
        +string descricao
        +string status
        +List~string~ requisitos
        +string localizacao
        +string modalidade
        +string area
        +datetime data_criacao
        +pausar() void
        +fechar() void
        +reabrir() void
        +is_aberta() bool
    }

    class Candidatura {
        +int id
        +int vaga_id
        +int candidato_id
        +string fase_atual
        +float match_score
        +string feedback_ia
        +string curriculo_path
        +string curriculo_nome
        +datetime data_aplicacao
        +avancar_fase(nova_fase: str) void
        +definir_resultado_ia(score: float, parecer: str) void
    }

    class Notificacao {
        +int id
        +int usuario_id
        +string titulo
        +string mensagem
        +bool lida
        +datetime data_criacao
        +marcar_como_lida() void
    }

    %% Interfaces / Portas
    class UsuarioRepositoryPort {
        <<interface>>
        +obter_por_id(id: int) Usuario
        +obter_por_email(email: str) Usuario
        +salvar(usuario: Usuario) Usuario
        +listar_todos() List~Usuario~
        +eliminar(id: int) void
    }

    class VagaRepositoryPort {
        <<interface>>
        +obter_por_id(id: int) Vaga
        +listar(filtros: dict) List~Vaga~
        +listar_por_empresa(empresa_id: int) List~Vaga~
        +salvar(vaga: Vaga) Vaga
        +eliminar(id: int) void
    }

    class CandidaturaRepositoryPort {
        <<interface>>
        +obter_por_id(id: int) Candidatura
        +listar_por_vaga(vaga_id: int) List~Candidatura~
        +listar_por_candidato(candidato_id: int) List~Candidatura~
        +salvar(candidatura: Candidatura) Candidatura
    }

    class AIScreenerPort {
        <<interface>>
        +analisar_curriculo(requisitos: List~str~, conteudo_cv: str) dict
    }

    class EmailServicePort {
        <<interface>>
        +enviar_recuperacao_senha(destinatario: str, token: str) void
        +enviar_atualizacao_fase(destinatario: str, vaga_titulo: str, nova_fase: str) void
    }

    %% Casos de Uso
    class AutenticacaoUseCase {
        -UsuarioRepositoryPort usuario_repo
        -EmailServicePort email_service
        +registrar(dados: dict) Usuario
        +login(email: str, senha: str) dict
        +solicitar_recuperacao(email: str) dict
        +redefinir_senha(token: str, nova_senha: str) dict
    }

    class GerenciarVagasUseCase {
        -VagaRepositoryPort vaga_repo
        +criar_vaga(empresa_id: int, dados: dict) Vaga
        +atualizar_vaga(vaga_id: int, dados: dict) Vaga
        +alterar_status(vaga_id: int, status: str) Vaga
        +excluir_vaga(vaga_id: int) void
    }

    class RealizarCandidaturaUseCase {
        -CandidaturaRepositoryPort candidatura_repo
        -VagaRepositoryPort vaga_repo
        -AIScreenerPort ai_screener
        -EmailServicePort email_service
        +submeter_candidatura(candidato_id: int, vaga_id: int, pdf_bytes: bytes) Candidatura
        +avancar_candidato(candidatura_id: int, nova_fase: str) Candidatura
    }

    %% Relacionamentos de Domínio
    Usuario "1" --> "*" Vaga : publica
    Usuario "1" --> "*" Candidatura : submete
    Usuario "1" --> "*" Notificacao : recebe
    Vaga "1" --> "*" Candidatura : recebe

    %% Relacionamentos de Casos de Uso com Portas
    AutenticacaoUseCase ..> UsuarioRepositoryPort : usa
    AutenticacaoUseCase ..> EmailServicePort : usa
    GerenciarVagasUseCase ..> VagaRepositoryPort : usa
    RealizarCandidaturaUseCase ..> CandidaturaRepositoryPort : usa
    RealizarCandidaturaUseCase ..> VagaRepositoryPort : usa
    RealizarCandidaturaUseCase ..> AIScreenerPort : usa
    RealizarCandidaturaUseCase ..> EmailServicePort : usa
```

---

## 11. Diagrama de Casos de Uso

Apresenta as funcionalidades agrupadas por perfil de acesso (Atores), ilustrando as dependências e o papel do assistente de inteligência artificial na triagem.

```mermaid
flowchart LR
    %% Atores
    Candidato((Candidato))
    Empresa((Empresa / Recrutador))
    Admin((Administrador))
    GeminiIA((Google Gemini 1.5))

    subgraph Sistema ["Plataforma de Recrutamento É Salú"]
        %% Casos de Uso - Autenticação
        UC_Reg["Criar Conta com Confirmação"]
        UC_Login["Iniciar Sessão (JWT)"]
        UC_Forgot["Recuperar Senha por E-mail"]
        
        %% Casos de Uso - Candidato
        UC_Search["Pesquisar & Filtrar Vagas"]
        UC_Apply["Candidatar-se (Upload PDF)"]
        UC_Track["Acompanhar Status & Match IA"]
        UC_CandProfile["Gerir Perfil Profissional"]
        
        %% Casos de Uso - Empresa
        UC_PostJob["Publicar / Editar Vaga"]
        UC_ManageJobs["Pausar / Fechar Vagas"]
        UC_ViewATS["Aceder ao Funil ATS de Candidatos"]
        UC_ViewFeedback["Consultar Parecer Técnico da IA"]
        UC_DownloadCV["Descarregar Currículo PDF"]
        UC_ChangePhase["Mover Fase (Triagem / Entrevista / Contratado)"]
        UC_CompProfile["Gerir Perfil Institucional"]
        
        %% Casos de Uso - IA
        UC_ExtractPDF["Extrair Texto do Currículo"]
        UC_ScoreMatch["Calcular Match Score (0-100%)"]
        UC_GenFeedback["Gerar Parecer Técnico"]
        
        %% Casos de Uso - Administrador
        UC_DashKPI["Visualizar Métricas Globais & IA"]
        UC_ModUsers["Moderar Contas & Alterar Perfis"]
        UC_ModJobs["Moderar & Auditar Vagas"]
        
        %% Notificações
        UC_SSE["Receber Notificações em Tempo Real (SSE)"]
    end

    %% Relações Candidato
    Candidato --> UC_Reg
    Candidato --> UC_Login
    Candidato --> UC_Forgot
    Candidato --> UC_Search
    Candidato --> UC_Apply
    Candidato --> UC_Track
    Candidato --> UC_CandProfile
    Candidato --> UC_SSE

    %% Relações Empresa
    Empresa --> UC_Login
    Empresa --> UC_PostJob
    Empresa --> UC_ManageJobs
    Empresa --> UC_ViewATS
    Empresa --> UC_ViewFeedback
    Empresa --> UC_DownloadCV
    Empresa --> UC_ChangePhase
    Empresa --> UC_CompProfile
    Empresa --> UC_SSE

    %% Relações Admin
    Admin --> UC_Login
    Admin --> UC_DashKPI
    Admin --> UC_ModUsers
    Admin --> UC_ModJobs

    %% Inclusões / Relações da IA
    UC_Apply -.->|<<include>>| UC_ExtractPDF
    UC_ExtractPDF -.->|<<include>>| UC_ScoreMatch
    UC_ScoreMatch -.->|<<include>>| UC_GenFeedback
    GeminiIA --- UC_ScoreMatch
    GeminiIA --- UC_GenFeedback

    %% Relações de dependência
    UC_ChangePhase -.->|<<include>>| UC_SSE
```

---

## 12. Diagramas de Atividades

Modelam o fluxo lógico e as decisões operacionais dos principais processos de negócio do sistema.

### 12.1. Atividade: Processo de Candidatura e Triagem Automática

Representa o workflow com faixas de responsabilidade (*swimlanes*) desde a submissão do currículo até a disponibilização do score no ATS.

```mermaid
flowchart TD
    Start([Início]) --> SearchJob[Candidato busca vaga no portal]
    SearchJob --> SelectJob[Seleciona a oportunidade de interesse]
    SelectJob --> CheckAuth{Está logado como Candidato?}

    CheckAuth -- Não --> ShowLogin[Exibe tela de login / registro]
    ShowLogin --> CheckAuth

    CheckAuth -- Sim --> OpenModal[Abre modal de candidatura]
    OpenModal --> UploadPDF[Anexa arquivo do currículo em PDF]
    UploadPDF --> ValidatePDF{Arquivo é PDF válido?}

    ValidatePDF -- Não --> ShowError[Exibe alerta de formato inválido]
    ShowError --> UploadPDF

    ValidatePDF -- Sim --> SubmitApp[Dispara POST /api/candidaturas]
    SubmitApp --> SaveDB[API salva candidatura com fase 'Triagem']
    SaveDB --> AckClient[Retorna 201 Created para o candidato]
    AckClient --> SuccessToast[Candidato recebe confirmação na tela]

    %% Processamento em Background
    SaveDB --> ExtractText[Extrai texto do PDF com pypdf]
    ExtractText --> CallGemini[Envia requisitos da vaga e texto à API do Gemini]
    CallGemini --> ParseAIResponse{Resposta da IA válida?}

    ParseAIResponse -- Sim --> UpdateScore[Grava match_score e parecer técnico no banco]
    ParseAIResponse -- Não --> FallbackManual[Grava flag para revisão humana]

    UpdateScore --> NotifyCompany[Gera notificação SSE para o recrutador]
    FallbackManual --> NotifyCompany
    NotifyCompany --> End([Fim do Processo de Triagem])
```

---

### 12.2. Atividade: Publicação e Gestão de Vagas pela Empresa

Ilustra o ciclo operacional do recrutador ao cadastrar, gerenciar o status e encerrar oportunidades.

```mermaid
flowchart TD
    Start([Início]) --> EnterDashboard[Recrutador acessa o Painel da Empresa]
    EnterDashboard --> ClickNewJob[Clica em 'Publicar Nova Vaga']
    ClickNewJob --> FillForm[Preenche Título, Área, Modalidade, Localização, Descrição e Requisitos]
    FillForm --> ValidateFields{Campos obrigatórios preenchidos?}

    ValidateFields -- Não --> ShowFormError[Exibe mensagens de validação]
    ShowFormError --> FillForm

    ValidateFields -- Sim --> SaveJob[Envia formulário à API]
    SaveJob --> SetStatusOpen[Vaga salva com status 'Aberta']
    SetStatusOpen --> AvailableToPublic[Vaga imediatamente visível aos candidatos]

    AvailableToPublic --> MonitorApplications[Recrutador monitora candidatos no ATS]
    MonitorApplications --> DecideAction{Deseja alterar status da vaga?}

    DecideAction -- Pausar --> PauseJob[Status alterado para 'Pausada' - Vaga oculta para novos inscritos]
    PauseJob --> DecideAction

    DecideAction -- Reabrir --> ReopenJob[Status retorna para 'Aberta']
    ReopenJob --> DecideAction

    DecideAction -- Encerrar --> CloseJob[Status alterado para 'Fechada']
    DecideAction -- Excluir --> DeleteJob[Vaga e candidaturas removidas do sistema]

    CloseJob --> End([Processo Concluído])
    DeleteJob --> End
```

---

### 12.3. Atividade: Transição de Fase no ATS e Comunicação Multicanal

Demonstra o fluxo acionado quando um recrutador move um candidato no funil ATS (ex: de *Triagem* para *Entrevista* ou *Contratado*).

```mermaid
flowchart TD
    Start([Início]) --> ViewATS[Recrutador abre funil ATS da vaga]
    ViewATS --> ReviewCandidate[Analisa perfil, CV em PDF e parecer da IA]
    ReviewCandidate --> SelectNewPhase[Seleciona nova fase: Entrevista, Contratado ou Reprovado]
    SelectNewPhase --> ConfirmChange[Dispara PATCH /api/candidaturas/{id}/fase]

    ConfirmChange --> UpdateDB[API atualiza fase_atual na base de dados]
    UpdateDB --> CreateNotification[Cria registro na tabela NOTIFICACOES]

    %% Disparos Paralelos
    CreateNotification --> TriggerSSE[Broadcaster SSE envia evento em tempo real]
    CreateNotification --> TriggerEmail[EmailService envia e-mail transacional]

    TriggerSSE --> ClientToast[Candidato visualiza Toast flutuante instantâneo]
    TriggerEmail --> ClientInbox[Candidato recebe e-mail na sua caixa postal]

    ClientToast --> SyncBoard[Interface ATS da empresa atualiza status]
    ClientInbox --> SyncBoard
    SyncBoard --> End([Fim do Ciclo de Transição])
```

---

*Livro de Diagramas mantido e versionado no repositório da **É Salú**.*
