"use client";

import { useEffect, useState, useMemo } from "react";
import { Search, Shield, Building2, User, Trash2, CheckCircle2, AlertCircle, RefreshCw } from "lucide-react";
import { api, getSession, SessionUser } from "@/lib/api";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<SessionUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [roleFilter, setRoleFilter] = useState<string>("todos");
  const [userToDelete, setUserToDelete] = useState<SessionUser | null>(null);
  const [updatingUserId, setUpdatingUserId] = useState<number | null>(null);

  const session = getSession();

  function loadUsers() {
    if (!session) return;
    setLoading(true);
    api.adminUsers(session.token)
      .then((data) => {
        setUsers(data);
        setError("");
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadUsers();
  }, []);

  async function handleRoleChange(user: SessionUser, newRole: string) {
    if (!session || user.tipo_perfil === newRole) return;
    setUpdatingUserId(user.id);
    setError("");
    try {
      const updated = await api.updateAdminUserRole(user.id, newRole, session.token);
      setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
      setSuccessMsg(`Perfil de ${user.nome} atualizado para "${newRole}".`);
      setTimeout(() => setSuccessMsg(""), 4000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro ao alterar tipo de perfil.");
    } finally {
      setUpdatingUserId(null);
    }
  }

  async function handleDeleteUser() {
    if (!session || !userToDelete) return;
    setError("");
    try {
      await api.deleteAdminUser(userToDelete.id, session.token);
      setUsers((prev) => prev.filter((u) => u.id !== userToDelete.id));
      setSuccessMsg(`Utilizador ${userToDelete.nome} removido com sucesso.`);
      setUserToDelete(null);
      setTimeout(() => setSuccessMsg(""), 4000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro ao excluir utilizador.");
    }
  }

  // Estatísticas rápidas
  const counts = useMemo(() => {
    return {
      total: users.length,
      candidatos: users.filter((u) => u.tipo_perfil === "Candidato").length,
      empresas: users.filter((u) => u.tipo_perfil === "Empresa").length,
      admins: users.filter((u) => u.tipo_perfil === "Administrador").length,
    };
  }, [users]);

  // Filtragem
  const filteredUsers = useMemo(() => {
    return users.filter((user) => {
      const matchesSearch =
        user.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (user.localizacao && user.localizacao.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchesRole = roleFilter === "todos" || user.tipo_perfil === roleFilter;

      return matchesSearch && matchesRole;
    });
  }, [users, searchTerm, roleFilter]);

  const getRoleBadge = (role: string) => {
    switch (role) {
      case "Administrador":
        return "bg-amber-50 text-amber-700 border-amber-200";
      case "Empresa":
        return "bg-purple-50 text-purple-700 border-purple-200";
      case "Candidato":
      default:
        return "bg-sky-50 text-sky-700 border-sky-200";
    }
  };

  return (
    <div className="space-y-6">
      {/* Cabeçalho */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">Gestão de Utilizadores</h2>
          <p className="mt-1 text-sm text-slate-500">
            Controle de acessos, perfis e contas registadas na plataforma.
          </p>
        </div>
        <button
          onClick={loadUsers}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3.5 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin text-sky-600" : "text-slate-400"}`} />
          Atualizar
        </button>
      </div>

      {/* Cards de Resumo */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div
          onClick={() => setRoleFilter("todos")}
          className={`cursor-pointer rounded-xl border p-4 transition-all ${
            roleFilter === "todos" ? "border-sky-500 bg-sky-50/50 shadow-sm" : "border-slate-200 bg-white hover:border-slate-300"
          }`}
        >
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Todos</p>
          <p className="mt-1 text-2xl font-bold text-slate-900">{counts.total}</p>
        </div>
        <div
          onClick={() => setRoleFilter("Candidato")}
          className={`cursor-pointer rounded-xl border p-4 transition-all ${
            roleFilter === "Candidato" ? "border-sky-500 bg-sky-50/50 shadow-sm" : "border-slate-200 bg-white hover:border-slate-300"
          }`}
        >
          <div className="flex items-center gap-1.5 text-sky-600">
            <User className="h-3.5 w-3.5" />
            <p className="text-xs font-semibold uppercase tracking-wider">Candidatos</p>
          </div>
          <p className="mt-1 text-2xl font-bold text-slate-900">{counts.candidatos}</p>
        </div>
        <div
          onClick={() => setRoleFilter("Empresa")}
          className={`cursor-pointer rounded-xl border p-4 transition-all ${
            roleFilter === "Empresa" ? "border-purple-500 bg-purple-50/50 shadow-sm" : "border-slate-200 bg-white hover:border-slate-300"
          }`}
        >
          <div className="flex items-center gap-1.5 text-purple-600">
            <Building2 className="h-3.5 w-3.5" />
            <p className="text-xs font-semibold uppercase tracking-wider">Empresas</p>
          </div>
          <p className="mt-1 text-2xl font-bold text-slate-900">{counts.empresas}</p>
        </div>
        <div
          onClick={() => setRoleFilter("Administrador")}
          className={`cursor-pointer rounded-xl border p-4 transition-all ${
            roleFilter === "Administrador" ? "border-amber-500 bg-amber-50/50 shadow-sm" : "border-slate-200 bg-white hover:border-slate-300"
          }`}
        >
          <div className="flex items-center gap-1.5 text-amber-600">
            <Shield className="h-3.5 w-3.5" />
            <p className="text-xs font-semibold uppercase tracking-wider">Admins</p>
          </div>
          <p className="mt-1 text-2xl font-bold text-slate-900">{counts.admins}</p>
        </div>
      </div>

      {/* Alertas */}
      {error && (
        <div className="flex items-center gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <AlertCircle className="h-5 w-5 shrink-0 text-red-500" />
          <span>{error}</span>
        </div>
      )}
      {successMsg && (
        <div className="flex items-center gap-3 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
          <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-600" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Barra de Filtros e Busca */}
      <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Pesquisar por nome, e-mail ou localização..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-slate-50/50 py-2 pl-9 pr-4 text-sm text-slate-800 placeholder-slate-400 focus:border-sky-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-sky-500"
          />
        </div>
        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-slate-500">Filtrar por Perfil:</label>
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
          >
            <option value="todos">Todos ({counts.total})</option>
            <option value="Candidato">Candidatos ({counts.candidatos})</option>
            <option value="Empresa">Empresas ({counts.empresas})</option>
            <option value="Administrador">Administradores ({counts.admins})</option>
          </select>
        </div>
      </div>

      {/* Tabela de Utilizadores */}
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-slate-200 bg-slate-50/80 text-xs font-semibold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-4">Utilizador</th>
                <th className="px-6 py-4">Perfil / Cargo</th>
                <th className="px-6 py-4">Localização</th>
                <th className="px-6 py-4 text-right">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredUsers.map((user) => {
                const isCurrentAdmin = session?.user.id === user.id;
                const initials = user.nome
                  .split(" ")
                  .map((n) => n[0])
                  .slice(0, 2)
                  .join("")
                  .toUpperCase();

                return (
                  <tr key={user.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-700 border border-slate-200">
                          {initials}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-slate-900">{user.nome}</span>
                            {isCurrentAdmin && (
                              <span className="rounded bg-sky-100 px-1.5 py-0.5 text-[10px] font-bold text-sky-800">
                                Você
                              </span>
                            )}
                          </div>
                          <span className="text-xs text-slate-500">{user.email}</span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${getRoleBadge(user.tipo_perfil)}`}>
                          {user.tipo_perfil}
                        </span>
                        {!isCurrentAdmin && (
                          <select
                            disabled={updatingUserId === user.id}
                            value={user.tipo_perfil}
                            onChange={(e) => handleRoleChange(user, e.target.value)}
                            className="rounded border border-slate-200 bg-white px-2 py-1 text-xs text-slate-600 hover:border-slate-300 focus:border-sky-500 focus:outline-none"
                            title="Alterar perfil do utilizador"
                          >
                            <option value="Candidato">Mudar para Candidato</option>
                            <option value="Empresa">Mudar para Empresa</option>
                            <option value="Administrador">Mudar para Administrador</option>
                          </select>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-600">
                      {user.localizacao ? (
                        <span>{user.localizacao}</span>
                      ) : (
                        <span className="text-slate-400 italic">Não informada</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {!isCurrentAdmin ? (
                        <button
                          onClick={() => setUserToDelete(user)}
                          className="inline-flex items-center gap-1 rounded-md p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 transition-colors"
                          title="Excluir utilizador"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      ) : (
                        <span className="text-xs text-slate-400 italic">Protegido</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Estados vazios / Carregando */}
        {loading && (
          <div className="p-12 text-center text-sm text-slate-500">
            <RefreshCw className="mx-auto h-6 w-6 animate-spin text-sky-600 mb-2" />
            Carregando utilizadores...
          </div>
        )}

        {!loading && filteredUsers.length === 0 && (
          <div className="p-12 text-center">
            <p className="text-base font-semibold text-slate-800">Nenhum utilizador encontrado</p>
            <p className="mt-1 text-sm text-slate-500">
              {searchTerm || roleFilter !== "todos"
                ? "Tente ajustar os termos de pesquisa ou remover os filtros aplicados."
                : "Ainda não existem utilizadores registados na plataforma."}
            </p>
          </div>
        )}
      </div>

      {/* Modal de Confirmação de Exclusão */}
      {userToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-100 text-red-600 mb-4">
              <Trash2 className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Excluir Utilizador</h3>
            <p className="mt-2 text-sm text-slate-600">
              Tem a certeza de que deseja excluir o utilizador{" "}
              <strong className="text-slate-800">{userToDelete.nome}</strong> ({userToDelete.email})?
              Esta ação removerá permanentemente a conta e os dados associados.
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setUserToDelete(null)}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleDeleteUser}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 transition-colors"
              >
                Confirmar Exclusão
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
