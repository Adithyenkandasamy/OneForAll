"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Boxes,
  Activity,
  ShieldCheck,
  Cpu,
  BrainCircuit,
  Users,
  ArrowRight,
  Zap,
  BarChart3,
  Database,
  Layers,
  ChevronDown,
  Factory,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

/* ─── Animation helpers ──────────────────────────────────────── */
const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] },
  }),
};

const stagger = {
  visible: { transition: { staggerChildren: 0.08 } },
};

/* ─── Data ───────────────────────────────────────────────────── */
const features = [
  {
    icon: BrainCircuit,
    title: "AI Inventory Analysis",
    desc: "Ask natural-language questions about factory inventory. Get AI-generated risk detection, stock analysis, and reorder recommendations powered by Llama 3.3 70B.",
    accent: "from-violet-500/20 to-purple-600/20",
    iconColor: "text-violet-600",
  },
  {
    icon: Activity,
    title: "Real-Time Monitoring",
    desc: "Live machine telemetry via MQTT. Monitor temperature, vibration, pressure, and RPM across every machine on the factory floor in real time.",
    accent: "from-emerald-500/20 to-teal-600/20",
    iconColor: "text-emerald-600",
  },
  {
    icon: ShieldCheck,
    title: "Quality Assurance Agent",
    desc: "Deterministic risk engine evaluates sensor data against configurable thresholds. Automatic alerts when quality metrics exceed safe limits.",
    accent: "from-amber-500/20 to-orange-600/20",
    iconColor: "text-amber-600",
  },
  {
    icon: Cpu,
    title: "Predictive Maintenance",
    desc: "ML models predict machine failures before they happen. Vibration anomaly detection, torque drift tracking, and proactive service scheduling.",
    accent: "from-sky-500/20 to-blue-600/20",
    iconColor: "text-sky-600",
  },
  {
    icon: Sparkles,
    title: "Central Intelligence",
    desc: "Executive-level AI orchestrator providing cross-domain manufacturing insights. Unified chat interface for enterprise-wide intelligence queries.",
    accent: "from-pink-500/20 to-rose-600/20",
    iconColor: "text-pink-600",
  },
  {
    icon: Users,
    title: "Role-Based Access Control",
    desc: "Three-tier RBAC — Viewer, Operator, and Admin roles. Tool-level filtering ensures operators can update inventory while viewers stay read-only.",
    accent: "from-indigo-500/20 to-blue-600/20",
    iconColor: "text-indigo-600",
  },
];

const techStack = [
  { name: "FastAPI", category: "Backend" },
  { name: "Next.js 15", category: "Frontend" },
  { name: "Llama 3.3 70B", category: "AI/LLM" },
  { name: "MCP Protocol", category: "Integration" },
  { name: "Supabase", category: "Database" },
  { name: "MQTT", category: "IoT" },
  { name: "Google Sheets", category: "Data Source" },
  { name: "SQLAlchemy", category: "ORM" },
];

const architectureLayers = [
  {
    icon: Layers,
    label: "Frontend",
    detail: "Next.js 15 · React 19 · Tailwind v4 · shadcn/ui",
    color: "bg-gradient-to-r from-zinc-900 to-zinc-800",
  },
  {
    icon: Zap,
    label: "API Layer",
    detail: "FastAPI · JWT Auth · Rate Limiting · CORS",
    color: "bg-gradient-to-r from-zinc-800 to-zinc-700",
  },
  {
    icon: BrainCircuit,
    label: "AI Agents",
    detail: "Inventory Agent · Executive Agent · Quality Agent",
    color: "bg-gradient-to-r from-zinc-700 to-zinc-600",
  },
  {
    icon: BarChart3,
    label: "Shared Kernel",
    detail: "LLM Provider · MCP Client · Agent Runner · Event Bus",
    color: "bg-gradient-to-r from-zinc-600 to-zinc-500",
  },
  {
    icon: Database,
    label: "Data Layer",
    detail: "Supabase PostgreSQL · Google Sheets via MCP · MQTT Telemetry",
    color: "bg-gradient-to-r from-zinc-500 to-zinc-400",
  },
];

/* ─── Page ───────────────────────────────────────────────────── */
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white text-zinc-900 overflow-x-hidden">
      {/* ── Navbar ─────────────────────────────────────────── */}
      <nav className="fixed top-0 inset-x-0 z-50 backdrop-blur-xl bg-white/70 border-b border-zinc-200/60">
        <div className="max-w-6xl mx-auto flex items-center justify-between px-6 h-16">
          <Link href="/landing" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-900 text-white font-bold text-sm">
              O
            </div>
            <span className="text-lg font-semibold tracking-tight">
              OneForAll AI
            </span>
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm" className="text-zinc-600 hover:text-zinc-900">
                Sign In
              </Button>
            </Link>
            <Link href="/login">
              <Button size="sm" className="bg-zinc-900 text-white hover:bg-zinc-800 shadow-sm">
                Get Started
                <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ───────────────────────────────────────────── */}
      <section className="relative pt-32 pb-24 px-6">
        {/* Subtle gradient orbs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-[800px] h-[600px] rounded-full bg-gradient-to-br from-violet-100/40 via-sky-100/30 to-transparent blur-3xl" />
          <div className="absolute top-1/3 -right-32 w-[400px] h-[400px] rounded-full bg-gradient-to-bl from-amber-100/30 to-transparent blur-3xl" />
        </div>

        <motion.div
          className="max-w-4xl mx-auto text-center relative z-10"
          initial="hidden"
          animate="visible"
          variants={stagger}
        >
          <motion.div variants={fadeUp} custom={0}>
            <Badge
              variant="outline"
              className="px-4 py-1.5 text-xs font-medium tracking-wide border-zinc-300 text-zinc-600 mb-8 inline-flex items-center gap-1.5"
            >
              <Factory className="h-3 w-3" />
              AI-Powered Manufacturing Intelligence
            </Badge>
          </motion.div>

          <motion.h1
            variants={fadeUp}
            custom={1}
            className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.08] mb-6"
          >
            Transform your factory
            <br />
            <span className="bg-gradient-to-r from-violet-600 via-sky-600 to-emerald-600 bg-clip-text text-transparent">
              with intelligent AI
            </span>
          </motion.h1>

          <motion.p
            variants={fadeUp}
            custom={2}
            className="text-lg sm:text-xl text-zinc-500 max-w-2xl mx-auto leading-relaxed mb-10"
          >
            OneForAll AI connects your Google Sheets inventory, live machine
            telemetry, and quality metrics into a unified AI assistant. Ask
            questions in plain English — get analysis, risk detection, and
            recommendations instantly.
          </motion.p>

          <motion.div
            variants={fadeUp}
            custom={3}
            className="flex flex-wrap justify-center gap-4"
          >
            <Link href="/login">
              <Button
                size="lg"
                className="bg-zinc-900 text-white hover:bg-zinc-800 shadow-lg shadow-zinc-900/10 px-8 h-12 text-base"
              >
                Start Using OneForAll
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <a href="#features">
              <Button
                variant="outline"
                size="lg"
                className="border-zinc-300 text-zinc-700 hover:bg-zinc-50 px-8 h-12 text-base"
              >
                Learn More
                <ChevronDown className="ml-2 h-4 w-4" />
              </Button>
            </a>
          </motion.div>
        </motion.div>
      </section>

      {/* ── Features ───────────────────────────────────────── */}
      <section id="features" className="py-24 px-6 bg-zinc-50/60">
        <motion.div
          className="max-w-6xl mx-auto"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={stagger}
        >
          <motion.div variants={fadeUp} custom={0} className="text-center mb-16">
            <Badge
              variant="outline"
              className="px-4 py-1.5 text-xs font-medium tracking-wide border-zinc-300 text-zinc-500 mb-4 inline-block"
            >
              Core Capabilities
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Six intelligent agents, one platform
            </h2>
            <p className="text-zinc-500 max-w-xl mx-auto text-lg">
              Each agent is an isolated, composable module with its own MCP
              tools, risk engine, and domain knowledge.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                variants={fadeUp}
                custom={i + 1}
                className="group relative rounded-2xl border border-zinc-200/80 bg-white p-7 hover:shadow-lg hover:shadow-zinc-200/50 transition-all duration-300 hover:-translate-y-0.5"
              >
                <div
                  className={`inline-flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-br ${f.accent} mb-5`}
                >
                  <f.icon className={`h-5 w-5 ${f.iconColor}`} />
                </div>
                <h3 className="text-lg font-semibold mb-2 tracking-tight">
                  {f.title}
                </h3>
                <p className="text-sm text-zinc-500 leading-relaxed">
                  {f.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ── Architecture ───────────────────────────────────── */}
      <section className="py-24 px-6">
        <motion.div
          className="max-w-4xl mx-auto"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={stagger}
        >
          <motion.div variants={fadeUp} custom={0} className="text-center mb-16">
            <Badge
              variant="outline"
              className="px-4 py-1.5 text-xs font-medium tracking-wide border-zinc-300 text-zinc-500 mb-4 inline-block"
            >
              System Design
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Clean, hexagonal architecture
            </h2>
            <p className="text-zinc-500 max-w-xl mx-auto text-lg">
              Dependency injection, strategy pattern, and MCP isolation keep
              every layer independently testable and swappable.
            </p>
          </motion.div>

          <div className="space-y-3">
            {architectureLayers.map((layer, i) => (
              <motion.div
                key={layer.label}
                variants={fadeUp}
                custom={i + 1}
                className={`${layer.color} text-white rounded-xl px-7 py-5 flex items-center gap-5 shadow-sm`}
              >
                <layer.icon className="h-6 w-6 shrink-0 opacity-80" />
                <div>
                  <p className="font-semibold text-sm tracking-wide">
                    {layer.label}
                  </p>
                  <p className="text-xs opacity-70 mt-0.5">{layer.detail}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ── Data Flow ──────────────────────────────────────── */}
      <section className="py-24 px-6 bg-zinc-50/60">
        <motion.div
          className="max-w-5xl mx-auto"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={stagger}
        >
          <motion.div variants={fadeUp} custom={0} className="text-center mb-16">
            <Badge
              variant="outline"
              className="px-4 py-1.5 text-xs font-medium tracking-wide border-zinc-300 text-zinc-500 mb-4 inline-block"
            >
              How It Works
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              From question to insight in seconds
            </h2>
            <p className="text-zinc-500 max-w-xl mx-auto text-lg">
              Ask a plain-English question. The AI agent determines which tools
              to call, fetches live data, and delivers analyzed results.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              {
                step: "01",
                title: "Ask a Question",
                desc: '"Which materials are below minimum stock?"',
              },
              {
                step: "02",
                title: "AI Selects Tools",
                desc: "LLM decides to call get_low_stock via MCP protocol.",
              },
              {
                step: "03",
                title: "Live Data Fetched",
                desc: "MCP server queries Google Sheets in an isolated subprocess.",
              },
              {
                step: "04",
                title: "Insight Delivered",
                desc: "AI analyzes results, flags risks, and recommends actions.",
              },
            ].map((s, i) => (
              <motion.div
                key={s.step}
                variants={fadeUp}
                custom={i + 1}
                className="text-center p-6 rounded-2xl border border-zinc-200/80 bg-white"
              >
                <div className="text-3xl font-bold text-zinc-200 mb-3">
                  {s.step}
                </div>
                <h4 className="font-semibold text-base mb-2">{s.title}</h4>
                <p className="text-sm text-zinc-500 leading-relaxed">
                  {s.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ── Tech Stack ─────────────────────────────────────── */}
      <section className="py-24 px-6">
        <motion.div
          className="max-w-4xl mx-auto text-center"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={stagger}
        >
          <motion.div variants={fadeUp} custom={0}>
            <Badge
              variant="outline"
              className="px-4 py-1.5 text-xs font-medium tracking-wide border-zinc-300 text-zinc-500 mb-4 inline-block"
            >
              Technology
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-12">
              Built with modern, proven tools
            </h2>
          </motion.div>

          <motion.div
            variants={fadeUp}
            custom={1}
            className="flex flex-wrap justify-center gap-3"
          >
            {techStack.map((t) => (
              <div
                key={t.name}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full border border-zinc-200 bg-white text-sm font-medium text-zinc-700 hover:shadow-md hover:border-zinc-300 transition-all duration-200"
              >
                <span className="text-[10px] uppercase tracking-wider text-zinc-400 font-semibold">
                  {t.category}
                </span>
                <span className="w-px h-3.5 bg-zinc-200" />
                {t.name}
              </div>
            ))}
          </motion.div>
        </motion.div>
      </section>

      {/* ── CTA ────────────────────────────────────────────── */}
      <section className="py-24 px-6">
        <motion.div
          className="max-w-3xl mx-auto text-center"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={stagger}
        >
          <motion.div
            variants={fadeUp}
            custom={0}
            className="rounded-3xl bg-zinc-900 text-white p-12 sm:p-16 relative overflow-hidden"
          >
            {/* Accent glow */}
            <div className="absolute -top-20 -right-20 w-64 h-64 rounded-full bg-violet-500/10 blur-3xl pointer-events-none" />
            <div className="absolute -bottom-20 -left-20 w-64 h-64 rounded-full bg-sky-500/10 blur-3xl pointer-events-none" />

            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4 relative z-10">
              Ready to upgrade your factory?
            </h2>
            <p className="text-zinc-400 text-lg mb-8 max-w-lg mx-auto relative z-10">
              Sign in to access AI-powered analytics, real-time monitoring, and
              predictive maintenance — all in one platform.
            </p>
            <Link href="/login" className="relative z-10">
              <Button
                size="lg"
                className="bg-white text-zinc-900 hover:bg-zinc-100 shadow-lg px-10 h-12 text-base font-semibold"
              >
                Get Started Now
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* ── Footer ─────────────────────────────────────────── */}
      <footer className="border-t border-zinc-200 py-10 px-6">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-zinc-900 text-white font-bold text-[10px]">
              O
            </div>
            <span className="text-sm font-medium text-zinc-500">
              OneForAll AI
            </span>
          </div>
          <p className="text-xs text-zinc-400">
            © {new Date().getFullYear()} OneForAll Corp. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
