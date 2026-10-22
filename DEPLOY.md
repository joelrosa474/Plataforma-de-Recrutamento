# 🚀 Guia de Implantação (Deploy em Produção)

Este guia explica passo a passo como colocar a **Plataforma de Recrutamento RH** no ar gratuitamente ou com custo mínimo usando a arquitetura recomendada:
- **Frontend**: [Vercel](https://vercel.com) (Next.js)
- **Backend**: [Render](https://render.com) ou [Railway](https://railway.app) (FastAPI + Docker)
- **Base de Dados**: PostgreSQL Gerenciado (Render, Neon ou Supabase)
- **Domínio & DNS**: [Cloudflare](https://cloudflare.com) (Opcional para domínio customizado e SSL)

---

## Passo 1: Subir o Backend & Base de Dados (Render ou Railway)

### Opção A: Render.com (Mais fácil com `render.yaml`)

1. Crie uma conta no [Render.com](https://render.com).
2. No painel, clique em **New +** e selecione **Blueprint**.
3. Conecte o repositório GitHub do seu projeto.
4. O Render detectará automaticamente o arquivo [`render.yaml`](file:///c:/Users/LENOVO/Desktop/Plataforma%20de%20recrutamento%20RH/render.yaml) e provisionará:
   - Um banco de dados **PostgreSQL** gerenciado.
   - Um serviço web **FastAPI** rodando via Docker.
5. Preencha as variáveis de ambiente no painel quando solicitado:
   - `GEMINI_API_KEY`: Sua chave do [Google AI Studio](https://aistudio.google.com/).
   - `ADMIN_EMAILS`: Seu e-mail de administrador (ex: `admin@suaempresa.com`).
   - `RESEND_API_KEY`: (Opcional) Chave de e-mail do [Resend](https://resend.com).
6. Clique em **Apply**. O Render aplicará as migrações do Alembic (`alembic upgrade head`) e iniciará a API.
7. Copie a URL gerada (exemplo: `https://rh-backend-api.onrender.com`).

---

## Passo 2: Subir o Frontend (Vercel)

1. Crie uma conta no [Vercel.com](https://vercel.com).
2. Clique em **Add New...** > **Project** e importe o mesmo repositório do GitHub.
3. Na tela de configuração:
   - **Framework Preset**: Next.js
   - **Root Directory**: Clique em *Edit* e selecione a pasta **`webapp`**.
4. Expanda a seção **Environment Variables** e adicione:
   - `NEXT_PUBLIC_API_URL`: A URL do seu backend obtida no Passo 1 (ex: `https://rh-backend-api.onrender.com`).
5. Clique em **Deploy**.
6. Em cerca de 1 a 2 minutos, o frontend estará publicado com certificado SSL (ex: `https://sua-plataforma.vercel.app`).

---

## Passo 3: Fechar o Ciclo de Segurança (CORS)

Agora que o frontend tem um endereço oficial:

1. Volte ao painel do **Render** (ou Railway).
2. Vá em **Environment** do serviço do backend e atualize:
   - `CORS_ORIGINS`: Adicione o domínio da Vercel (ex: `https://sua-plataforma.vercel.app`).
   - `FRONTEND_URL`: `https://sua-plataforma.vercel.app` (para links de redefinição de senha).
3. Salve as alterações. O backend reiniciará automaticamente com o CORS protegido.

---

## Passo 4: Configurar Domínio Próprio no Cloudflare (Opcional)

Se você possuir um domínio próprio (ex: `empresa.com`):

1. Adicione seu domínio no painel gratuito do [Cloudflare](https://dash.cloudflare.com).
2. Crie os apontamentos DNS no Cloudflare:
   - **Frontend**: CNAME `rh` apontando para `cname.vercel-dns.com` (com Nuvem Laranja ativa).
   - **Backend**: CNAME `api` apontando para `rh-backend-api.onrender.com` (com Nuvem Laranja ativa).
3. Configure o SSL no Cloudflare como **Full (strict)**.
4. Atualize as variáveis `NEXT_PUBLIC_API_URL` e `CORS_ORIGINS` para usarem os novos subdomínios (`https://api.empresa.com` e `https://rh.empresa.com`).

---

## Checklist Final de Validação

- [ ] Acessar `https://seu-backend/health` e conferir se retorna `{"status": "ok", "database": "connected"}`.
- [ ] Criar a conta de Administrador usando o e-mail definido em `ADMIN_EMAILS`.
- [ ] Criar uma vaga pela área da empresa e realizar uma candidatura de teste com upload de PDF.
- [ ] Confirmar o recebimento da notificação em tempo real (SSE) e o score da IA do Gemini.
