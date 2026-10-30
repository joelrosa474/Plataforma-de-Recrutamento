# 🚀 Guia de Implantação (Deploy em Produção)

Este guia explica passo a passo como colocar a **Plataforma de Recrutamento RH** no ar gratuitamente ou com custo mínimo usando a arquitetura recomendada:
- **Frontend**: [Vercel](https://vercel.com) (Next.js) ✅ **https://plataforma-de-recrutamento-rouge.vercel.app**
- **Backend**: [Render](https://render.com) (FastAPI + PostgreSQL) ✅ **https://rh-backend-api-ulcu.onrender.com**
- **Base de Dados**: PostgreSQL Gerenciado no Render ✅ Conectado
- **Status do Backend**: `{"status":"ok","database":"connected"}`

> **Porquê Render e não Vercel para o backend?**
> O backend usa **Server-Sent Events (SSE)** para notificações em tempo real e **background workers**. A Vercel executa funções serverless com tempo limite de 30s, incompatível com ligações de longa duração. O Render mantém o servidor ativo continuamente.

---

## Passo 1: Subir o Backend & Base de Dados (Render)

### Deploy com `render.yaml` (1 clique)

1. Crie uma conta no [Render.com](https://render.com).
2. No painel, clique em **New +** e selecione **Blueprint**.
3. Conecte o repositório GitHub: **`joelrosa474/Plataforma-de-Recrutamento`**
4. O Render detectará automaticamente o arquivo `render.yaml` e provisionará:
   - Um banco de dados **PostgreSQL** gerenciado (gratuito por 90 dias).
   - Um serviço web **FastAPI** rodando via Docker.
5. Preencha as variáveis de ambiente no painel:

   | Variável | Valor |
   |---|---|
   | `GEMINI_API_KEY` | Sua chave do [Google AI Studio](https://aistudio.google.com/) |
   | `JWT_SECRET_KEY` | String aleatória longa e segura (`openssl rand -hex 32`) |
   | `ADMIN_EMAILS` | `rosa03@gmail.com` |
   | `CORS_ORIGINS` | `https://plataforma-de-recrutamento-rouge.vercel.app` |
   | `API_ORIGIN` | `https://rh-backend-api-ulcu.onrender.com` |
   | `FRONTEND_URL` | `https://plataforma-de-recrutamento-rouge.vercel.app` |
   | `RESEND_API_KEY` | *(Opcional)* Chave do [Resend](https://resend.com) para e-mails |

6. Clique em **Apply**. O Render aplicará as migrações do Alembic (`alembic upgrade head`) e iniciará a API.
7. **Copie a URL gerada** (exemplo: `https://rh-backend-api.onrender.com`) — precisará dela a seguir.

---

## Passo 2: Ligar o Frontend ao Backend (Vercel)

O frontend **já está publicado** em: https://plataforma-de-recrutamento-rouge.vercel.app

Para ligar ao backend:

1. Aceda ao painel: [vercel.com/dashboard](https://vercel.com/dashboard)
2. Selecione o projeto `plataforma-de-recrutamento`.
3. Vá em **Settings** → **Environment Variables**.
4. Adicione:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: URL do Render (ex: `https://rh-backend-api.onrender.com`)
5. Clique em **Save** e depois em **Redeploy** para aplicar.

---

## Passo 3: CORS já configurado ✅

O `CORS_ORIGINS` já inclui `https://plataforma-de-recrutamento-rouge.vercel.app`. Defina também `API_ORIGIN` com a URL HTTPS pública do backend, conforme a tabela acima. Estas variáveis permitem pedidos autenticados por cookie apenas a partir das origens confiáveis.

---

## Passo 4: Configurar Domínio Próprio no Cloudflare (Opcional)

Se possuir um domínio próprio (ex: `empresa.com`):

1. Adicione o domínio no painel gratuito do [Cloudflare](https://dash.cloudflare.com).
2. Crie os apontamentos DNS no Cloudflare:
   - **Frontend**: CNAME `rh` → `cname.vercel-dns.com` (Nuvem Laranja ativa)
   - **Backend**: CNAME `api` → `rh-backend-api.onrender.com` (Nuvem Laranja ativa)
3. Configure o SSL no Cloudflare como **Full (strict)**.
4. Atualize `NEXT_PUBLIC_API_URL`, `CORS_ORIGINS` e `API_ORIGIN` para usarem os novos subdomínios.

---

## ✅ Checklist Final de Validação

- [ ] Aceder a `https://SEU-BACKEND.onrender.com/health` e confirmar `{"status": "ok", "database": "connected"}`.
- [ ] Aceder a `https://plataforma-de-recrutamento-rouge.vercel.app` e fazer login com `rosa03@gmail.com`.
- [ ] Criar uma vaga pela área da empresa e realizar uma candidatura de teste com upload de PDF.
- [ ] Confirmar o recebimento da notificação em tempo real (SSE) e o score da IA do Gemini.
- [ ] Verificar se e-mails transacionais estão a ser enviados (se `RESEND_API_KEY` configurado).
