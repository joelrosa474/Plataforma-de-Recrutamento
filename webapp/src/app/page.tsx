import Image from "next/image";
import Link from "next/link";
import {
  ArrowRight,
  BriefcaseBusiness,
  Building2,
  CheckCircle2,
  Clock3,
  Search,
  ShieldCheck,
  Sparkles,
  UserRoundCheck,
} from "lucide-react";
import foto1 from "@/fotos/foto1.jpg";
import foto2 from "@/fotos/foto2.jpg";
import logoSalu from "@/fotos/Salú (2).png";

const highlights = [
  {
    icon: Clock3,
    title: "Candidaturas em tempo real",
    text: "Candidate-se em poucos minutos e acompanhe o estado das suas candidaturas em tempo real com notificações instantâneas.",
  },
  {
    icon: UserRoundCheck,
    title: "Para todos os perfis",
    text: "Descubra oportunidades para todos os níveis de experiência, do primeiro emprego à liderança executiva.",
  },
  {
    icon: BriefcaseBusiness,
    title: "Vagas sempre atualizadas",
    text: "Encontre vagas atualizadas diariamente nos principais setores da economia em Luanda e em todo o país.",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-white text-slate-950 flex flex-col">
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/95 backdrop-blur">
        <div className="mx-auto flex h-16 sm:h-20 max-w-7xl items-center justify-between px-4 sm:px-8">
          <Link href="/" className="flex items-center gap-2.5 sm:gap-3" aria-label="Página inicial">
            <Image src={logoSalu} alt="Salú" priority className="h-11 w-auto sm:h-14" />
          </Link>

          <div className="flex items-center gap-2 sm:gap-3">
            <Link
              href="/auth?mode=register"
              className="text-xs sm:text-sm font-semibold text-slate-700 hover:text-sky-700 px-2 sm:px-3 py-2 transition"
            >
              Inscreva-se
            </Link>
            <Link
              href="/auth"
              className="inline-flex h-9 sm:h-11 items-center justify-center rounded-lg border border-sky-600 px-4 sm:px-6 text-xs sm:text-sm font-semibold text-sky-700 transition hover:bg-sky-50"
            >
              Entrar
            </Link>
          </div>
        </div>
      </header>

      <section className="relative overflow-hidden flex-1">
        <div className="absolute inset-x-0 top-0 h-56 bg-gradient-to-b from-sky-50 to-white" />
        <div className="relative mx-auto grid max-w-7xl items-center gap-10 px-4 py-10 sm:px-8 sm:py-14 lg:grid-cols-[1.05fr_0.95fr] lg:py-16">
          <div className="max-w-2xl">
            <div className="mb-4 sm:mb-6 inline-flex items-center gap-2 rounded-full border border-sky-200 bg-white px-3.5 py-1.5 text-xs sm:text-sm font-semibold text-sky-700 shadow-sm">
              <Sparkles className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
              Recrutamento digital para Angola
            </div>

            <h1 className="text-3xl font-bold leading-tight tracking-tight text-slate-950 sm:text-5xl lg:text-6xl">
              A principal plataforma de recrutamento de Angola
            </h1>

            <p className="mt-4 sm:mt-6 max-w-xl text-base sm:text-lg leading-relaxed text-slate-600">
              Conectamos empresas aos melhores talentos e profissionais às oportunidades certas. Explore milhares de vagas, candidate-se online e impulsione a sua carreira.
            </p>

            <div className="mt-8 max-w-2xl rounded-2xl border border-slate-200 bg-white p-2 sm:p-2.5 shadow-xl shadow-sky-950/5">
              <div className="flex flex-col gap-2 sm:flex-row">
                <label className="relative flex min-h-12 sm:min-h-14 flex-1 items-center">
                  <Search className="pointer-events-none absolute left-3.5 sm:left-4 h-5 w-5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Cargo, empresa ou palavra-chave..."
                    className="h-12 sm:h-14 w-full rounded-xl border border-transparent bg-slate-50 pl-11 sm:pl-12 pr-4 text-base sm:text-sm font-medium text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-sky-500 focus:bg-white"
                  />
                </label>
                <Link
                  href="/candidate/dashboard"
                  className="inline-flex h-12 sm:h-14 items-center justify-center gap-2 rounded-xl bg-sky-600 px-6 sm:px-7 text-sm font-bold text-white transition hover:bg-sky-700 shadow-sm"
                >
                  Procurar vagas
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>

            <div className="mt-6 sm:mt-8 flex flex-wrap gap-2.5 sm:gap-3 text-xs sm:text-sm font-semibold text-slate-600">
              <span className="inline-flex items-center gap-2 rounded-lg bg-slate-100 px-3 py-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                Empresas verificadas
              </span>
              <span className="inline-flex items-center gap-2 rounded-lg bg-slate-100 px-3 py-2">
                <ShieldCheck className="h-4 w-4 text-sky-600" />
                Processo transparente
              </span>
            </div>
          </div>

          <div className="relative mb-8 lg:mb-0">
            <div className="absolute -left-8 top-8 hidden h-28 w-28 rounded-full border border-sky-200 lg:block" />
            <div className="absolute -right-4 bottom-12 hidden h-20 w-20 rounded-lg bg-emerald-100 lg:block" />
            <div className="relative overflow-hidden rounded-2xl border border-slate-200 bg-sky-50 shadow-2xl shadow-slate-900/10">
              <Image
                src={foto2}
                alt="Profissional analisando perfis de candidatos"
                priority
                className="h-auto w-full object-cover"
                sizes="(min-width: 1024px) 48vw, 100vw"
              />
            </div>
            <div className="mt-4 sm:absolute sm:-bottom-7 sm:left-auto sm:right-5 sm:w-80 rounded-xl border border-slate-200 bg-white p-4 shadow-xl shadow-slate-900/10">
              <div className="flex items-start gap-3">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
                  <Building2 className="h-5 w-5" />
                </span>
                <div>
                  <p className="text-sm font-bold text-slate-950">Empresas encontram talento mais rápido</p>
                  <p className="mt-1 text-xs sm:text-sm leading-relaxed text-slate-600">Triagem inteligente, publicação e acompanhamento num só lugar.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-y border-slate-200 bg-slate-50 py-12 sm:py-16">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 sm:px-8 lg:grid-cols-[0.85fr_1.15fr] lg:items-center">
          <div className="overflow-hidden rounded-2xl bg-white shadow-sm border border-slate-200">
            <Image
              src={foto1}
              alt="Candidata acompanhando oportunidades online"
              className="h-auto w-full object-cover"
              sizes="(min-width: 1024px) 42vw, 100vw"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
            {highlights.map((item) => {
              const Icon = item.icon;
              return (
                <article key={item.title} className="rounded-xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm transition hover:border-sky-200 hover:shadow-md">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-50 text-sky-600">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h2 className="mt-4 text-base sm:text-lg font-bold text-slate-950">{item.title}</h2>
                  <p className="mt-2 text-xs sm:text-sm leading-relaxed text-slate-600">{item.text}</p>
                </article>
              );
            })}
          </div>
        </div>
      </section>
    </main>
  );
}
