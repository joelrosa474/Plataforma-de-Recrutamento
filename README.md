# 🇦🇴 É Salú — Plataforma de Recrutamento RH Inteligente

Plataforma moderna de atração e gestão de talentos para Angola, equipada com triagem automática de currículos por Inteligência Artificial (**Google Gemini**), notificações em tempo real (**SSE**) e painel **ATS** para empresas e administradores.

- 🌐 **Frontend em Produção (Vercel):** [https://plataforma-de-recrutamento-rouge.vercel.app](https://plataforma-de-recrutamento-rouge.vercel.app)
- ⚙️ **Backend API em Produção (Render):** [https://rh-backend-api-ulcu.onrender.com](https://rh-backend-api-ulcu.onrender.com)
- 📘 **Documentação Oficial Completa:** Consulte [DOCUMENTACAO.md](DOCUMENTACAO.md) para a arquitetura, modelo de dados e referência da API.
- 📊 **Livro de Diagramas Técnicos:** Consulte [DIAGRAMAS.md](DIAGRAMAS.md) com todos os 9 diagramas Mermaid de fluxo, banco de dados e arquitetura.
- 🚀 **Guia de Implantação e Deploy:** Consulte [DEPLOY.md](DEPLOY.md).

---

## Pré-requisitos

- Node.js 22+ e npm
- Python 3.14+

## Configuração local

1. No backend, copie o template de ambiente para `.env` e preencha os valores:

```env
GEMINI_API_KEY=
JWT_SECRET_KEY=change-me-to-a-long-random-secret
ADMIN_EMAILS=admin@empresa.com
DATABASE_URL=sqlite:///./recrutamento.db
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
APP_ENV=development
```

`JWT_SECRET_KEY` é obrigatória. O e-mail em `ADMIN_EMAILS` ganha o perfil de administrador ao criar conta ou iniciar sessão.

2. No frontend, copie o template para `.env.local` ou `.env`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Instale e execute o backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn src.main:app --reload --port 8000
```

4. Em outro terminal, execute o frontend:

```powershell
cd webapp
& 'C:\Program Files\nodejs\npm.cmd' install
& 'C:\Program Files\nodejs\npm.cmd' run dev
```

O frontend abre em `http://localhost:3000` e a API em `http://localhost:8000`.

## Checklist de produção

- definir `JWT_SECRET_KEY` forte e única por ambiente
- usar `DATABASE_URL` correta para PostgreSQL/SQLite em produção
- restringir `CORS_ORIGINS` ao domínio do frontend real
- definir `APP_ENV=production`
- não versionar `.env` real nem segredos em repositório
- manter `ADMIN_EMAILS` limitado a contas confiáveis

```powershell
cd webapp
& 'C:\Program Files\nodejs\npm.cmd' run build

cd ..\backend
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -v
```

## Migrações de Base de Dados (Alembic)

Para aplicar ou gerar alterações no schema da base de dados (SQLite ou PostgreSQL):

```powershell
cd backend
# Aplicar migrações pendentes até a versão mais recente
.\.venv\Scripts\alembic.exe upgrade head

# Criar nova migração automaticamente após alterar models.py
.\.venv\Scripts\alembic.exe revision --autogenerate -m "nome_da_alteracao"
```

## Execução com Docker (Opcional)

Para rodar todo o ecossistema (Backend + Frontend) em contêineres:

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Documentação interativa Swagger: `http://localhost:8000/docs`

## Integração Contínua (CI/CD)

O repositório possui automação via **GitHub Actions** em `.github/workflows/ci.yml`.
A cada `push` ou `pull request`, a esteira valida:
1. Instalação e execução de **todos os testes unitários/integração** do backend no Python 3.12.
2. Checagem de tipagem TypeScript e compilação do build de produção do Next.js.

## Guia de Deploy em Produção

Para instruções detalhadas de publicação com **Vercel** (frontend), **Render / Railway** (backend com PostgreSQL) e **Cloudflare**, consulte o guia completo em [DEPLOY.md](file:///c:/Users/LENOVO/Desktop/Plataforma%20de%20recrutamento%20RH/DEPLOY.md).
