# 📘 Documentação Oficial do Sistema — É Salú (Recrutamento RH)

Bem-vindo à documentação técnica e funcional da **É Salú**, uma plataforma moderna de recrutamento e seleção orientada por Inteligência Artificial (Google Gemini), concebida para conectar candidatos qualificados às melhores empresas de Angola.

---

## 1. Visão Geral e Objetivos do Produto

A **É Salú** digitaliza e automatiza o ciclo completo de atração, triagem e contratação de talentos. O sistema resolve os principais gargalos dos processos seletivos tradicionais:
- **Para Candidatos:** Interface intuitiva e 100% responsiva (smartphones, tablets e computadores), com candidaturas rápidas via upload de PDF e acompanhamento do status em tempo real.
- **Para Empresas (Recrutadores):** Painel ATS (Applicant Tracking System) com categorização de candidatos por fases (Triagem, Entrevista, Contratado, Reprovado), análise de aderência por IA e download direto dos currículos.
- **Para Administradores:** Painel executivo com métricas de volume, distribuição por modalidade/setores, monitoramento de performance da IA e governança de contas e vagas.

---

## 2. Arquitetura da Solução

O ecossistema foi construído sobre uma arquitetura desacoplada e modular, garantindo escalabilidade, segurança e fácil manutenção:

```mermaid
graph TD
    Client["Navegador / Dispositivo (Mobile, Tablet, Desktop)"]
    
    subgraph Frontend ["Frontend (Vercel)"]
        NextApp["Next.js 16 (App Router & Turbopack)"]
        Tailwind["Design System Responsivo (Tailwind CSS)"]
        SSEListener["Notificações em Tempo Real (EventSource / SSE)"]
    end

    subgraph Backend ["Backend API (Render)"]
        FastAPI["FastAPI (Python 3.12+)"]
        CleanArch["Clean Architecture (Domain, UseCases, Ports)"]
        GeminiScreener["Serviço de Triagem IA (Google Gemini 1.5)"]
        EmailService["Serviço de E-mail (Resend API / SMTP)"]
        Broadcaster["NotificationBroadcaster (Thread-Safe SSE)"]
    end

    subgraph Storage ["Persistência & Nuvem"]
        Postgres["PostgreSQL Gerenciado (Produção) / SQLite (Local)"]
        Alembic["Migrações de Schema (Alembic)"]
        Uploads["Armazenamento de Currículos (PDFs Sanitizados)"]
    end

    Client -->|HTTPS| NextApp
    NextApp -->|REST API & JSON| FastAPI
    SSEListener -->|SSE Stream /stream| Broadcaster
    FastAPI --> CleanArch
    CleanArch --> Postgres
    CleanArch --> GeminiScreener
    CleanArch --> EmailService
```

### Tecnologias Utilizadas

| Camada | Tecnologia | Finalidade |
|---|---|---|
| **Frontend** | Next.js 16 (React 18, TypeScript) | Renderização híbrida rápida e SEO |
| **Estilização** | Tailwind CSS + Lucide Icons | Design moderno, responsivo e adaptável a telas de 320px a 4K |
| **Backend** | FastAPI + Python 3.12+ | API REST assíncrona de alta performance |
| **Arquitetura Backend** | Clean Architecture / Portas & Adaptadores | Separação estrita de regras de negócio e infraestrutura |
| **Base de Dados** | PostgreSQL (Render) / SQLite | Armazenamento relacional com suporte a pools de conexão |
| **ORM & Migrações** | SQLAlchemy 2.0 + Alembic | Modelagem relacional e versionamento de banco |
| **Inteligência Artificial**| Google Gemini Studio API | Extração de texto de PDFs e pontuação semântica (*Match Score*) |
| **Tempo Real** | Server-Sent Events (SSE) | Notificações push leves e sem dependência de websockets pesados |
| **Segurança** | JWT (HMAC-SHA256) + Passlib (bcrypt) | Autenticação stateless com controle de expiração |
| **E-mails** | Resend API + SMTP fallback | Recuperação de senhas e alertas transacionais de contratação |

---

## 3. Perfis de Utilizador e Controlo de Acesso (RBAC)

O sistema implementa 3 níveis de permissão com isolamento em rotas protegidas no frontend (`RouteGuard`) e no backend (`get_current_user`):

### 3.1. Candidato
- Pesquisa de vagas abertas com filtros por palavra-chave, localização (província/cidade), modalidade (Presencial, Híbrido, Remoto) e setor.
- Candidatura com anexo de currículo exclusivamente em formato PDF.
- Acompanhamento do histórico de candidaturas com etiqueta da fase atual e score de compatibilidade calculado pela IA.
- Perfil profissional com competências, links de LinkedIn e GitHub.

### 3.2. Empresa (Recrutador)
- Publicação, edição, pausa e encerramento de vagas de emprego.
- Gestão de candidatos por vaga no formato ATS (Applicant Tracking System).
- Acesso ao parecer técnico detalhado gerado pela IA (Google Gemini).
- Descarregamento seguro do currículo original em PDF.
- Transição de fases do candidato: `Triagem` ➔ `Entrevista` ➔ `Contratado` ou `Reprovado` (com disparo automático de e-mail e notificação SSE para o candidato).

### 3.3. Administrador
- Painel analítico de governança com indicadores chave (KPIs):
  - Total de candidatos e empresas cadastradas.
  - Taxa de adoção da triagem com IA e média geral de compatibilidade.
  - Gráfico de funil de candidatos e distribuição de vagas por modalidade.
- Moderação de utilizadores: promover para Administrador, alterar perfil ou eliminar contas.
- Moderação de vagas: auditar, pausar ou remover vagas em desacordo com as diretrizes da plataforma.

---

## 4. Fluxo Inteligente de Triagem com IA (Google Gemini)

```mermaid
sequenceDiagram
    autonumber
    actor C as Candidato
    participant W as Webapp (Frontend)
    participant API as FastAPI Backend
    participant Gemini as Google Gemini IA
    participant DB as PostgreSQL
    actor E as Empresa

    C->>W: Seleciona vaga e anexa Currículo (PDF)
    W->>API: POST /api/candidaturas (multipart/form-data)
    API->>DB: Salva candidatura (fase: Triagem, match_score: null)
    API-->>W: 201 Created (Candidatura registada)
    
    Note over API,Gemini: Processamento Assíncrono da IA
    API->>API: Extrai texto do PDF com pypdf
    API->>Gemini: Analisa compatibilidade (Requisitos da Vaga vs CV)
    Gemini-->>API: JSON: {match_score: 85, feedback_ia: "Forte experiência em..."}
    API->>DB: Atualiza candidatura com Score e Parecer
    API->>E: Dispara Notificação SSE ("Nova candidatura com 85% de aderência")
```

---

## 5. Modelo de Dados (Entidade-Relacionamento)

```mermaid
erDiagram
    USUARIO ||--o{ VAGA : publica
    USUARIO ||--o{ CANDIDATURA : submete
    USUARIO ||--o{ NOTIFICACAO : recebe
    VAGA ||--o{ CANDIDATURA : recebe

    USUARIO {
        int id PK
        string nome
        string email UK
        string senha_hash
        string tipo_perfil "Candidato | Empresa | Administrador"
        string localizacao
        text experiencia
        json competencias
        string linkedin_url
        string github_url
        datetime data_criacao
    }

    VAGA {
        int id PK
        int empresa_id FK
        string titulo
        text descricao
        string status "Aberta | Pausada | Fechada"
        json requisitos
        string localizacao
        string modalidade "Presencial | Híbrido | Remoto"
        string area
        datetime data_criacao
    }

    CANDIDATURA {
        int id PK
        int vaga_id FK
        int candidato_id FK
        string fase_atual "Triagem | Entrevista | Contratado | Reprovado"
        float match_score
        text feedback_ia
        string curriculo_path
        string curriculo_nome
        datetime data_aplicacao
    }

    NOTIFICACAO {
        int id PK
        int usuario_id FK
        string titulo
        text mensagem
        boolean lida
        datetime data_criacao
    }
```

---

## 6. Referência dos Principais Endpoints da API

Documentação interativa disponível localmente em `http://localhost:8000/docs` ou em produção via Swagger.

### Autenticação & Recuperação (`/api/auth`)
- `POST /api/auth/register`: Criar conta com confirmação de senha obrigatória.
- `POST /api/auth/login`: Autenticação e emissão do token JWT.
- `POST /api/auth/forgot-password`: Solicitar link de recuperação de senha por e-mail.
- `POST /api/auth/reset-password`: Redefinir senha usando token criptográfico seguro.
- `GET /api/auth/me`: Obter dados do utilizador autenticado.

### Vagas (`/api/vagas`)
- `GET /api/vagas`: Listar vagas abertas com suporte a paginação e filtros (`termo`, `localizacao`, `modalidade`, `area`).
- `GET /api/vagas/{id}`: Obter detalhes de uma vaga específica.
- `POST /api/vagas`: Publicar nova vaga (restrito a `Empresa`).
- `PUT /api/vagas/{id}`: Atualizar vaga existente.
- `DELETE /api/vagas/{id}`: Remover vaga e dados associados.

### Candidaturas & ATS (`/api/candidaturas`)
- `POST /api/candidaturas`: Submeter candidatura com upload de PDF.
- `GET /api/candidaturas/minhas`: Histórico de candidaturas do candidato logado.
- `GET /api/candidaturas/vaga/{vaga_id}`: Lista de candidatos da vaga (restrito ao recrutador proprietário).
- `PATCH /api/candidaturas/{id}/fase`: Atualizar fase do candidato e disparar notificação.
- `GET /api/candidaturas/{id}/curriculo`: Download seguro do PDF do currículo.

### Notificações em Tempo Real (`/api/notificacoes`)
- `GET /api/notificacoes/stream`: Conexão contínua Server-Sent Events (SSE) autenticada via token de autorização.
- `GET /api/notificacoes`: Listagem de notificações armazenadas.
- `PATCH /api/notificacoes/{id}/ler`: Marcar notificação individual como lida.
- `POST /api/notificacoes/marcar-todas-lidas`: Marcar todas as notificações do usuário como lidas.

### Administração & Métricas (`/api/admin`)
- `GET /api/admin/summary`: Resumo analítico com indicadores de IA, taxas de conversão e totais.
- `GET /api/admin/users`: Listagem completa de utilizadores da plataforma.
- `PATCH /api/admin/users/{id}/role`: Alterar tipo de perfil de utilizador.
- `DELETE /api/admin/users/{id}`: Eliminar utilizador.
- `GET /api/admin/jobs`: Listagem e auditoria de todas as vagas publicadas.
- `PATCH /api/admin/jobs/{id}/status`: Moderação do status de uma vaga.

---

## 7. Práticas de Segurança e Conformidade

1. **Proteção de Credenciais:** As senhas são protegidas com algoritmos de hash modernos via `bcrypt`. Entradas longas são truncadas com segurança de codificação UTF-8 para respeitar o limite padrão de 72 bytes do bcrypt sem falhas.
2. **Prevenção de Ataques (CORS & Injection):**
   - Política restritiva de CORS configurada com os domínios oficiais da Vercel e portas de desenvolvimento.
   - Consultas à base de dados executadas através do ORM SQLAlchemy com *parameter binding*, eliminando riscos de SQL Injection.
3. **Uploads Seguros:** Apenas ficheiros com cabeçalhos MIME válidos de PDF são aceites na triagem.
4. **Isolamento de Segredos:** Arquivos `.env` protegidos no `.gitignore` para prevenir vazamentos acidentais no repositório de código público.

---

## 8. Execução e Testes Automatizados

### Rodar a Suite de Testes do Backend
O backend conta com 35 testes automatizados cobrindo autenticação, use cases, regras de negócio, serviços de e-mail e streaming SSE:

```powershell
cd backend
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

### Rodar o Build de Produção do Frontend
Validação estrita de TypeScript e empacotamento Turbopack:

```powershell
cd webapp
npm run build
```

---

*Documentação mantida pela equipa de engenharia do projeto **É Salú**.*
