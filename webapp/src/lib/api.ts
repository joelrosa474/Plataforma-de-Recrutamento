export type ApiJob = {
  id: number;
  empresa_id: number;
  titulo: string;
  descricao: string;
  status: "Aberta" | "Fechada" | "Pausada";
  requisitos: string[];
  localizacao?: string | null;
  modalidade?: string | null;
  area?: string | null;
  data_criacao: string;
};

export type ApiApplication = {
  id: number;
  vaga_id: number;
  candidato_id: number;
  fase_atual: "Triagem" | "Entrevista" | "Contratado" | "Reprovado";
  match_score: number | null;
  curriculo_nome?: string | null;
  tem_curriculo?: boolean;
  data_aplicacao: string;
  candidato?: {
    id: number;
    nome: string;
    email: string;
    localizacao?: string | null;
    competencias?: string[];
    experiencia?: string | null;
    linkedin_url?: string | null;
    github_url?: string | null;
  } | null;
};

export type JobPage = { items: ApiJob[]; total: number; pagina: number; tamanho: number };
export type AdminSummary = { usuarios: number; empresas: number; candidatos: number; vagas: number; candidaturas: number };
export type Notification = { id: number; titulo: string; mensagem: string; lida: boolean; data_criacao: string };

export type SessionUser = { id: number; nome: string; email: string; tipo_perfil: string; localizacao?: string | null; experiencia?: string | null; competencias?: string[]; linkedin_url?: string | null; github_url?: string | null };

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const options: RequestInit = {
    credentials: "include", // Envia cookies HttpOnly automaticamente
    ...init,
  };
  const response = await fetch(`${API_URL}${path}`, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail ?? "Não foi possível concluir a operação.");
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  register: (data: { nome: string; email: string; senha: string; tipo_perfil: string }) =>
    request<SessionUser>("/api/auth/registrar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) }),
  login: async (email: string, senha: string) => {
    const body = new URLSearchParams({ username: email, password: senha });
    return request<{ access_token: string; token_type: string; usuario: SessionUser }>("/api/auth/login", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body });
  },
  logout: () => request<{ message: string }>("/api/auth/logout", { method: "POST" }),
  requestPasswordReset: (email: string) =>
    request<{ message: string; debug_token?: string; debug_reset_link?: string }>("/api/auth/recuperar-senha", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    }),
  resetPassword: (token: string, nova_senha: string) =>
    request<{ message: string }>("/api/auth/redefinir-senha", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, nova_senha }),
    }),
  listJobs: () => request<ApiJob[]>("/api/vagas/"),
  searchJobs: (filters: { termo?: string; localizacao?: string; modalidade?: string; area?: string; pagina?: number } = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => { if (value) params.set(key, String(value)); });
    return request<JobPage>(`/api/vagas/busca?${params.toString()}`);
  },
  getJob: (id: number) => request<ApiJob>(`/api/vagas/${id}`),
  myJobs: (token?: string) => request<ApiJob[]>("/api/vagas/minhas", { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
  createJob: (data: Pick<ApiJob, "titulo" | "descricao" | "requisitos" | "localizacao" | "modalidade" | "area">, token?: string) =>
    request<ApiJob>("/api/vagas/", { method: "POST", headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: JSON.stringify(data) }),
  updateJob: (id: number, data: Pick<ApiJob, "titulo" | "descricao" | "requisitos" | "localizacao" | "modalidade" | "area">, token?: string) => request<ApiJob>(`/api/vagas/${id}`, { method: "PUT", headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: JSON.stringify(data) }),
  pauseJob: (id: number, token?: string) => request<ApiJob>(`/api/vagas/${id}/pausar`, { method: "PUT", headers: token ? { Authorization: `Bearer ${token}` } : {} }),
  closeJob: (id: number, token?: string) =>
    request<ApiJob>(`/api/vagas/${id}/fechar`, { method: "PUT", headers: token ? { Authorization: `Bearer ${token}` } : {} }),
  deleteJob: (id: number, token?: string) => request<void>(`/api/vagas/${id}`, { method: "DELETE", headers: token ? { Authorization: `Bearer ${token}` } : {} }),
  apply: (jobId: number, resume: File, token?: string) => {
    const body = new FormData();
    body.append("vaga_id", String(jobId));
    body.append("curriculo_pdf", resume);
    return request<ApiApplication>("/api/candidaturas/", { method: "POST", headers: token ? { Authorization: `Bearer ${token}` } : {}, body });
  },
  myApplications: (token?: string) => request<ApiApplication[]>("/api/candidaturas/minhas", { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
  applicationsByJob: (jobId: number, token?: string) => request<ApiApplication[]>(`/api/candidaturas/vaga/${jobId}`, { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
  downloadResume: async (applicationId: number, token?: string): Promise<Blob> => {
    const res = await fetch(`${API_URL}/api/candidaturas/${applicationId}/curriculo`, {
      credentials: "include",
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.detail ?? "Não foi possível descarregar o currículo.");
    }
    return res.blob();
  },
  updateApplicationPhase: (id: number, fase_atual: ApiApplication["fase_atual"], token?: string) => request<ApiApplication>(`/api/candidaturas/${id}/fase`, { method: "PUT", headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: JSON.stringify({ fase_atual }) }),
  myProfile: (token?: string) => request<SessionUser>("/api/auth/me", { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
  updateProfile: (data: Pick<SessionUser, "nome" | "localizacao" | "experiencia" | "competencias" | "linkedin_url" | "github_url">, token?: string) => request<SessionUser>("/api/auth/me", { method: "PUT", headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: JSON.stringify(data) }),
  candidateProfile: (id: number, token?: string) => request<SessionUser>(`/api/auth/candidatos/${id}`, { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
  updateEmail: (email: string, senha_atual: string, token?: string) => request<SessionUser>("/api/auth/me/email", { method: "PUT", headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: JSON.stringify({ email, senha_atual }) }),
  updatePassword: (senha_atual: string, nova_senha: string, token?: string) => request<void>("/api/auth/me/senha", { method: "PUT", headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: JSON.stringify({ senha_atual, nova_senha }) }),
  deleteAccount: (senha_atual: string, token?: string) => request<void>("/api/auth/me", { method: "DELETE", headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: JSON.stringify({ senha_atual }) }),
  adminSummary: (token?: string) => request<AdminSummary>("/api/admin/resumo", { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
  adminUsers: (token?: string) => request<SessionUser[]>("/api/admin/usuarios", { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
  adminJobs: (token?: string) => request<ApiJob[]>("/api/admin/vagas", { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
  updateAdminJobStatus: (id: number, status: ApiJob["status"], token?: string) => request<ApiJob>(`/api/admin/vagas/${id}/status`, { method: "PUT", headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: JSON.stringify({ status }) }),
  notifications: (token?: string) => request<Notification[]>("/api/notificacoes/", { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
  readNotification: (id: number, token?: string) => request<Notification>(`/api/notificacoes/${id}/lida`, { method: "PUT", headers: token ? { Authorization: `Bearer ${token}` } : {} }),
  readAllNotifications: (token?: string) => request<void>("/api/notificacoes/ler-todas", { method: "PUT", headers: token ? { Authorization: `Bearer ${token}` } : {} }),
};

export function getSession(): { token: string; user: SessionUser } | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem("rh-session");
  return raw ? JSON.parse(raw) : null;
}

export function saveSession(token: string, user: SessionUser) {
  window.localStorage.setItem("rh-session", JSON.stringify({ token, user }));
}

export function clearSession() {
  if (typeof window !== "undefined") {
    window.localStorage.removeItem("rh-session");
  }
}
