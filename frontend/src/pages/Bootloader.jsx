import React from "react";
import {
  Activity, ArrowUpRight, Bot, Boxes, Code2, Command, Database,
  ExternalLink, GitBranch, LayoutDashboard, Network, ShieldCheck,
  Sparkles, Workflow, Zap
} from "lucide-react";

const modules = [
  {
    id: "ai-chat",
    name: "AI Chat & Orchestrator",
    group: "INTELLIGENCE",
    description: "Chat and orchestration source exists in the private AP1 Ecosystem repository. Runtime connection to this console is not configured yet.",
    status: "PARTIAL",
    tone: "amber",
    icon: Bot,
    href: "https://github.com/amirulhafiz1132002-code/ap1-ecosystem",
    action: "Inspect source",
    evidence: "API source located: /api/chat and /api/orchestrate"
  },
  {
    id: "lovable",
    name: "Lovable Workstations",
    group: "EXTERNAL WORKSPACES",
    description: "Existing Lovable projects must be inventoried and their approved entry URLs confirmed before they can be registered here.",
    status: "NOT CONNECTED",
    tone: "slate",
    icon: Boxes,
    href: "https://lovable.dev/",
    action: "Open Lovable",
    evidence: "Workspace inventory unavailable during this audit"
  },
  {
    id: "developer",
    name: "Developer Workspace",
    group: "ENGINEERING",
    description: "AP1 Web Console repository and frontend source are available. Workspace tools and execution controls are not yet integrated.",
    status: "PARTIAL",
    tone: "amber",
    icon: Code2,
    href: "https://github.com/amirulhafiz1132002-code/AP1-WEB-Console",
    action: "Open repository",
    evidence: "React frontend + FastAPI backend source located"
  },
  {
    id: "amrhz-ai",
    name: "AMRHZ AI-13",
    group: "MODEL RUNTIME",
    description: "A separate model/runtime project under development. It is not currently integrated with AP1 and is not presented as live.",
    status: "DEVELOPMENT",
    tone: "blue",
    icon: Sparkles,
    href: "https://github.com/amirulhafiz1132002-code/AMRHZ-AI-13",
    action: "View project",
    evidence: "Repository documentation identifies Working Model v0.1"
  },
  {
    id: "research",
    name: "Research & Knowledge",
    group: "KNOWLEDGE",
    description: "Architecture, evidence, governance and research records remain in their source repositories. A unified search/API connection is pending.",
    status: "SOURCE AVAILABLE",
    tone: "blue",
    icon: Database,
    href: "https://github.com/amirulhafiz1132002-code/AMRHZAP1-REPOSITORY-SYSBLOG",
    action: "Open SYSBLOG",
    evidence: "Documentation repository located"
  },
  {
    id: "github",
    name: "GitHub Project Hub",
    group: "INTEGRATIONS",
    description: "Use the public GitHub account as the current project source directory. Live account actions are not exposed from this preview.",
    status: "SOURCE LINKED",
    tone: "green",
    icon: GitBranch,
    href: "https://github.com/amirulhafiz1132002-code",
    action: "Open GitHub",
    evidence: "37 accessible repositories enumerated"
  }
];

const toneStyles = {
  amber: "border-amber-400/25 bg-amber-400/10 text-amber-300",
  slate: "border-slate-500/30 bg-slate-500/10 text-slate-300",
  blue: "border-sky-400/25 bg-sky-400/10 text-sky-300",
  green: "border-emerald-400/25 bg-emerald-400/10 text-emerald-300"
};

function StatusPill({ status, tone }) {
  return (
    <span className={`inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-[10px] font-semibold tracking-[0.12em] ${toneStyles[tone]}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
}

export function Bootloader() {
  return (
    <main className="min-h-screen bg-[#080d18] text-slate-100">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="absolute -right-40 top-1/3 h-96 w-96 rounded-full bg-indigo-500/10 blur-3xl" />
        <div className="absolute inset-0 opacity-[0.12]" style={{ backgroundImage: "linear-gradient(rgba(148,163,184,.18) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,.18) 1px, transparent 1px)", backgroundSize: "48px 48px" }} />
      </div>

      <div className="relative mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <header className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-5">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-300/30 bg-cyan-300/10 text-cyan-200">
              <Command size={22} />
            </div>
            <div>
              <p className="text-xs font-bold tracking-[0.28em] text-cyan-300">AMRHZ / AP1</p>
              <h1 className="text-lg font-semibold tracking-wide">UNIFIED BOOTLOADER</h1>
            </div>
          </div>
          <a href="https://amirulhafiz1132002-code.github.io/AP1-WEB-Console/" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 rounded-lg border border-white/15 px-3 py-2 text-xs font-medium text-slate-300 transition hover:border-cyan-300/40 hover:text-cyan-200">
            Public showcase <ExternalLink size={14} />
          </a>
        </header>

        <section className="grid gap-8 py-10 lg:grid-cols-[1.25fr_.75fr] lg:items-end">
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/5 px-3 py-1.5 text-[10px] font-semibold tracking-[0.2em] text-cyan-200">
              <Activity size={13} /> MODULE CONTROL PLANE · PREVIEW
            </div>
            <h2 className="max-w-3xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
              One entry point.<br />
              <span className="bg-gradient-to-r from-cyan-300 to-indigo-300 bg-clip-text text-transparent">Connected capabilities.</span>
            </h2>
            <p className="mt-5 max-w-2xl text-sm leading-7 text-slate-400 sm:text-base">
              AP1 is being organized as a unified access layer for existing workspaces, AI services and development systems. This preview shows source-backed module states; it does not claim that unconnected services are operational.
            </p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 shadow-2xl shadow-black/20">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold tracking-[0.18em] text-slate-400">BOOT STATUS</span>
              <span className="rounded-full border border-amber-300/20 bg-amber-300/10 px-2.5 py-1 text-[10px] font-semibold tracking-wider text-amber-200">INTEGRATION IN PROGRESS</span>
            </div>
            <div className="mt-5 grid grid-cols-3 gap-3">
              <div><p className="text-2xl font-semibold">06</p><p className="mt-1 text-[10px] uppercase tracking-wider text-slate-500">Registered</p></div>
              <div><p className="text-2xl font-semibold text-amber-300">03</p><p className="mt-1 text-[10px] uppercase tracking-wider text-slate-500">Partial / pending</p></div>
              <div><p className="text-2xl font-semibold text-emerald-300">01</p><p className="mt-1 text-[10px] uppercase tracking-wider text-slate-500">Source linked</p></div>
            </div>
            <p className="mt-5 border-t border-white/10 pt-4 text-xs leading-5 text-slate-500">
              Counts describe this static registry snapshot, not live service telemetry.
            </p>
          </div>
        </section>

        <section className="mb-10">
          <div className="mb-4 flex items-end justify-between gap-3">
            <div>
              <p className="text-[10px] font-semibold tracking-[0.24em] text-cyan-300">MODULE REGISTRY</p>
              <h3 className="mt-1 text-xl font-semibold">Workspaces & capabilities</h3>
            </div>
            <span className="text-xs text-slate-500">Source-audited snapshot</span>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {modules.map((module) => {
              const Icon = module.icon;
              return (
                <article key={module.id} className="group flex min-h-[260px] flex-col rounded-2xl border border-white/10 bg-[#111a2a]/85 p-5 transition duration-200 hover:-translate-y-1 hover:border-cyan-300/30 hover:bg-[#142037]">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.04] text-cyan-200">
                      <Icon size={19} />
                    </div>
                    <StatusPill status={module.status} tone={module.tone} />
                  </div>
                  <p className="mt-5 text-[10px] font-semibold tracking-[0.2em] text-slate-500">{module.group}</p>
                  <h4 className="mt-1 text-lg font-semibold">{module.name}</h4>
                  <p className="mt-2 flex-1 text-xs leading-6 text-slate-400">{module.description}</p>
                  <div className="mt-4 border-t border-white/10 pt-3">
                    <p className="text-[10px] leading-5 text-slate-500">{module.evidence}</p>
                    <a href={module.href} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-2 text-xs font-semibold text-cyan-200 transition hover:text-white">
                      {module.action} <ArrowUpRight size={14} />
                    </a>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-5">
            <div className="flex items-center gap-2 text-cyan-200"><Network size={17} /><h3 className="text-sm font-semibold">Integration sequence</h3></div>
            <ol className="mt-4 space-y-3 text-xs text-slate-400">
              <li className="flex gap-3"><span className="text-cyan-300">01</span> Inventory existing projects and verify entry points.</li>
              <li className="flex gap-3"><span className="text-cyan-300">02</span> Register modules with access and connection metadata.</li>
              <li className="flex gap-3"><span className="text-cyan-300">03</span> Connect shared identity, API routing and event contracts.</li>
              <li className="flex gap-3"><span className="text-cyan-300">04</span> Verify each module independently before marking it connected.</li>
            </ol>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-5">
            <div className="flex items-center gap-2 text-emerald-200"><ShieldCheck size={17} /><h3 className="text-sm font-semibold">Governance boundary</h3></div>
            <p className="mt-4 text-xs leading-6 text-slate-400">
              AP1 does not silently merge, deploy, execute external actions or expose provider credentials. Module access will use explicit permissions and server-side secrets. A displayed module is not proof of a working connection.
            </p>
            <div className="mt-4 flex flex-wrap gap-2 text-[10px] font-semibold tracking-wider text-slate-500">
              <span className="rounded-md border border-white/10 px-2 py-1">REAL STATE</span>
              <span className="rounded-md border border-white/10 px-2 py-1">EVIDENCE</span>
              <span className="rounded-md border border-white/10 px-2 py-1">HUMAN CONTROL</span>
            </div>
          </div>
        </section>

        <footer className="mt-10 flex flex-wrap items-center justify-between gap-3 border-t border-white/10 py-5 text-[10px] tracking-wider text-slate-600">
          <span>AMRHZ AP1 · UNIFIED WORKSPACE FOUNDATION</span>
          <span className="inline-flex items-center gap-2"><Workflow size={13} /> AUDIT → PRIORITIZE → EXECUTE → VERIFY</span>
        </footer>
      </div>
    </main>
  );
}
