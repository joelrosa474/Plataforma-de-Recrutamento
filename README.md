# Plataforma de recrutamento RH

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

## Verificações

```powershell
cd webapp
& 'C:\Program Files\nodejs\npm.cmd' run build

cd ..\backend
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -v
```
