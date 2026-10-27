"use client";

import { FormEvent, useState } from "react";
import { Bot, MessageCircle, Send, X } from "lucide-react";

type Message = { from: "bot" | "user"; text: string };

const quickQuestions = ["Como me candidato?", "Como criar vaga?", "Onde acompanho a candidatura?"];

function answer(question: string) {
  const text = question.toLowerCase();
  if (text.includes("candidat")) return "Crie ou aceda à sua conta de candidato, procure uma vaga, clique em “Candidatar-me” e envie o seu currículo em PDF. Depois acompanhe o estado em Minhas Candidaturas.";
  if (text.includes("vaga") || text.includes("empresa")) return "Com uma conta de empresa, entre no Painel da Empresa e aceda a Minhas Vagas para publicar, editar, pausar ou fechar oportunidades.";
  if (text.includes("acompan") || text.includes("estado") || text.includes("entrevista")) return "Aceda a Minhas Candidaturas para ver o estado da triagem, entrevistas agendadas, notas e links enviados pela empresa.";
  if (text.includes("perfil") || text.includes("currículo") || text.includes("cv")) return "Em Meu Perfil, complete localização, experiência, competências e links profissionais. Um perfil atualizado melhora as recomendações de vagas.";
  if (text.includes("senha") || text.includes("entrar") || text.includes("login")) return "Na página Entrar, use “Esqueci a palavra-passe” para receber as instruções de recuperação.";
  return "Posso ajudar com candidaturas, vagas, entrevistas, perfil e acesso à conta. Pode reformular a sua pergunta com um destes temas?";
}

export function HelpChatbot() {
  const [open, setOpen] = useState(false);
  const [value, setValue] = useState("");
  const [messages, setMessages] = useState<Message[]>([{ from: "bot", text: "Olá! Sou o assistente da Salú. Como posso ajudar?" }]);

  function send(question: string) {
    const trimmed = question.trim();
    if (!trimmed) return;
    setMessages((items) => [...items, { from: "user", text: trimmed }, { from: "bot", text: answer(trimmed) }]);
    setValue("");
  }

  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); send(value); }

  return (
    <div className="fixed bottom-4 right-4 z-50 sm:bottom-6 sm:right-6">
      {open && (
        <section aria-label="Assistente de ajuda" className="mb-3 flex w-[calc(100vw-2rem)] max-w-sm flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">
          <header className="flex items-center justify-between bg-sky-700 px-4 py-3 text-white"><div className="flex items-center gap-2"><Bot className="h-5 w-5" /><div><p className="text-sm font-bold">Assistente Salú</p><p className="text-[11px] text-sky-100">Ajuda rápida</p></div></div><button onClick={() => setOpen(false)} aria-label="Fechar assistente" className="rounded p-1 hover:bg-white/10"><X className="h-4 w-4" /></button></header>
          <div className="max-h-72 space-y-3 overflow-y-auto bg-slate-50 p-4">{messages.map((message, index) => <p key={index} className={`w-fit max-w-[90%] rounded-xl px-3 py-2 text-xs leading-relaxed ${message.from === "bot" ? "bg-white text-slate-700 shadow-sm" : "ml-auto bg-sky-600 text-white"}`}>{message.text}</p>)}</div>
          <div className="border-t border-slate-100 p-3"><div className="mb-2 flex flex-wrap gap-1.5">{quickQuestions.map((question) => <button key={question} onClick={() => send(question)} className="rounded-full border border-sky-200 bg-sky-50 px-2 py-1 text-[11px] font-semibold text-sky-700 hover:bg-sky-100">{question}</button>)}</div><form onSubmit={submit} className="flex gap-2"><input value={value} onChange={(event) => setValue(event.target.value)} placeholder="Escreva a sua dúvida…" className="min-w-0 flex-1 rounded-lg border border-slate-300 px-3 py-2 text-xs outline-none focus:border-sky-500" /><button aria-label="Enviar mensagem" className="rounded-lg bg-sky-600 p-2 text-white hover:bg-sky-700"><Send className="h-4 w-4" /></button></form></div>
        </section>
      )}
      <button onClick={() => setOpen((current) => !current)} aria-label={open ? "Fechar chat" : "Abrir chat de ajuda"} className="flex h-14 w-14 items-center justify-center rounded-full bg-sky-600 text-white shadow-lg shadow-sky-900/25 transition hover:bg-sky-700"><MessageCircle className="h-6 w-6" /></button>
    </div>
  );
}
