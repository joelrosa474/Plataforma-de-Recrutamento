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

const highlights = [
  {
    icon: Clock3,
    title: "Candidaturas em tempo real",
    text: "Candidate-se em poucos minutos e acompanhe o estado das suas candidaturas em tempo real.",
  },
  {
    icon: UserRoundCheck,
    title: "Para todos os perfis",
    text: "Descubra oportunidades para todos os níveis de experiência, do primeiro emprego à liderança.",
  },
  {
    icon: BriefcaseBusiness,
    title: "Vagas sempre atualizadas",
    text: "Encontre vagas atualizadas diariamente nos principais setores da economia.",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-white text-slate-950">
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/95 backdrop-blur">
        <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-5 sm:px-8">
          <Link href="/" className="flex items-center gap-3" aria-label="Página inicial">
            <span className="flex h-10 w-10 items-end justify-center gap-1 rounded-lg bg-sky-50 px-2 py-2">
              <span className="h-6 w-2 rounded-full bg-sky-600" />
              <span className="h-8 w-2 rounded-full bg-sky-500" />
              <span className="h-5 w-2 rounded-full bg-sky-400" />
            </span>
            <span className="text-2xl font-bold tracking-tight text-slate-950">É Salú</span>
          </Link>



          <div className="flex items-center gap-3">
            <Link href="/auth?mode=register" className="hidden text-sm font-semibold text-slate-700 hover:text-sky-700 sm:inline-flex">
              Inscreva-se agora
            </Link>
            <Link
              href="/auth"
              className="inline-flex h-11 items-center justify-center rounded-md border border-sky-600 px-6 text-sm font-semibold text-sky-700 transition hover:bg-sky-50"
            >
              Entrar
            </Link>
          </div>
        </div>
      </header>

      <section className="relative overflow-hidden">
        <div className="absolute inset-x-0 top-0 h-56 bg-gradient-to-b from-sky-50 to-white" />
        <div className="relative mx-auto grid min-h-[calc(100vh-5rem)] max-w-7xl items-center gap-12 px-5 py-14 sm:px-8 lg:grid-cols-[1.02fr_0.98fr] lg:py-16">
          <div className="max-w-2xl">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-sky-200 bg-white px-4 py-2 text-sm font-semibold text-sky-700 shadow-sm">
              <Sparkles className="h-4 w-4" />
              Recrutamento digital para Angola
            </div>

            <h1 className="text-4xl font-bold leading-tight tracking-normal text-slate-950 sm:text-5xl lg:text-6xl">
              A principal plataforma de recrutamento de Angola
            </h1>

            <p className="mt-6 max-w-xl text-lg leading-8 text-slate-600">
              Conectamos empresas aos melhores talentos e profissionais às oportunidades certas. Explore milhares de vagas, candidate-se online e impulsione a sua carreira.
            </p>

            <div className="mt-9 max-w-2xl rounded-lg border border-slate-200 bg-white p-2 shadow-xl shadow-sky-950/5">
              <div className="flex flex-col gap-2 sm:flex-row">
                <label className="relative flex min-h-14 flex-1 items-center">
                  <Search className="pointer-events-none absolute left-4 h-5 w-5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Cargo, empresa ou palavra-chave"
                    className="h-14 w-full rounded-md border border-transparent bg-slate-50 pl-12 pr-4 text-sm font-medium text-slate-900 outline-none transition placeholder:text-slate-500 focus:border-sky-500 focus:bg-white"
                  />
                </label>
                <Link
                  href="/candidate/dashboard"
                  className="inline-flex h-14 items-center justify-center gap-2 rounded-md bg-sky-600 px-7 text-sm font-bold text-white transition hover:bg-sky-700"
                >
                  Procurar vagas
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>

            <div className="mt-8 flex flex-wrap gap-3 text-sm font-semibold text-slate-600">
              <span className="inline-flex items-center gap-2 rounded-md bg-slate-100 px-3 py-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                Empresas verificadas
              </span>
              <span className="inline-flex items-center gap-2 rounded-md bg-slate-100 px-3 py-2">
                <ShieldCheck className="h-4 w-4 text-sky-600" />
                Processo transparente
              </span>
            </div>
          </div>

          <div className="relative">
            <div className="absolute -left-8 top-8 hidden h-28 w-28 rounded-full border border-sky-200 lg:block" />
            <div className="absolute -right-4 bottom-12 hidden h-20 w-20 rounded-lg bg-emerald-100 lg:block" />
            <div className="relative overflow-hidden rounded-lg border border-slate-200 bg-sky-50 shadow-2xl shadow-slate-900/10">
              <Image
                src={foto2}
                alt="Profissional analisando perfis de candidatos"
                priority
                className="h-auto w-full object-cover"
                sizes="(min-width: 1024px) 48vw, 100vw"
              />
            </div>
            <div className="absolute -bottom-7 left-5 right-5 rounded-lg border border-slate-200 bg-white p-4 shadow-xl shadow-slate-900/10 sm:left-auto sm:w-80">
              <div className="flex items-start gap-3">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-emerald-100 text-emerald-700">
                  <Building2 className="h-5 w-5" />
                </span>
                <div>
                  <p className="text-sm font-bold text-slate-950">Empresas encontram talento mais rápido</p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">Triagem, publicação e acompanhamento num só lugar.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-y border-slate-200 bg-slate-50">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 py-14 sm:px-8 lg:grid-cols-[0.85fr_1.15fr] lg:items-center">
          <div className="overflow-hidden rounded-lg bg-white">
            <Image
              src={foto1}
              alt="Candidata acompanhando oportunidades online"
              className="h-auto w-full object-cover"
              sizes="(min-width: 1024px) 42vw, 100vw"
            />
          </div>

          <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-1">
            {highlights.map((item) => {
              const Icon = item.icon;
              return (
                <article key={item.title} className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
                  <Icon className="h-6 w-6 text-sky-600" />
                  <h2 className="mt-5 text-lg font-bold text-slate-950">{item.title}</h2>
                  <p className="mt-3 text-sm leading-6 text-slate-600">{item.text}</p>
                </article>
              );
            })}
          </div>
        </div>
      </section>
    </main>
  );
}
