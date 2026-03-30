"use client";
import { useState, useRef } from "react";
import { motion } from "framer-motion";
import emailjs from "@emailjs/browser";
import GlassCard from "@/components/ui/GlassCard";
import SendButton from "@/components/ui/SendButton";
import { toast } from "sonner";
import {
  Mail, Github, MessageCircle, User, FileText,
  Building, ArrowRight, Sparkles, Phone,
} from "lucide-react";

// ── EmailJS config ──────────────────────────────────────────
const EJS_SERVICE  = process.env.NEXT_PUBLIC_EMAILJS_SERVICE  || "YOUR_SERVICE_ID";
const EJS_TEMPLATE = process.env.NEXT_PUBLIC_EMAILJS_TEMPLATE || "YOUR_TEMPLATE_ID";
const EJS_KEY      = process.env.NEXT_PUBLIC_EMAILJS_KEY      || "YOUR_PUBLIC_KEY";
// ───────────────────────────────────────────────────────────

const PROJECT_TYPES = [
  "Lead Generation System",
  "AI Outreach Automation",
  "N8N Workflow Automation",
  "WhatsApp Bot / Automation",
  "Full-Stack Web App",
  "AI Agent Development",
  "Custom CRM / Dashboard",
  "Other",
];

const CONTACT_LINKS = [
  {
    icon: Mail,
    label: "Email",
    value: "saumyavishwam@gmail.com",
    href: "mailto:saumyavishwam@gmail.com",
    color: "#7B2FFF",
    desc: "Direct email — replies within 24h",
  },
  {
    icon: MessageCircle,
    label: "WhatsApp",
    value: "+91 886-655-3976",
    href: "https://wa.me/918866553976?text=Hi%2C%20I%20want%20to%20hire%20you%20for%20a%20project",
    color: "#25D366",
    desc: "Fastest response — usually within 2h",
  },
  {
    icon: Github,
    label: "GitHub",
    value: "github.com/saumyavishwam",
    href: "https://github.com/saumyavishwam",
    color: "#e2e8f0",
    desc: "See my code and projects",
  },
];

export default function ContactPage() {
  const formRef = useRef<HTMLFormElement>(null);
  const [form, setForm] = useState({
    from_name: "", from_email: "", company: "", project_type: "", message: "",
  });
  const [submitting, setSubmitting] = useState(false);

  const sendEmail = async () => {
    if (!form.from_name || !form.from_email || !form.message) {
      toast.error("Fill in name, email and message");
      return;
    }
    if (!/^\S+@\S+\.\S+$/.test(form.from_email)) {
      toast.error("Invalid email address");
      return;
    }

    setSubmitting(true);
    try {
      await emailjs.send(
        EJS_SERVICE, EJS_TEMPLATE,
        {
          from_name:    form.from_name,
          from_email:   form.from_email,
          company:      form.company || "Not specified",
          project_type: form.project_type || "Not specified",
          message:      form.message,
          to_email:     "saumyavishwam@gmail.com",
        },
        EJS_KEY
      );
      toast.success("Message sent! I'll reply within 24 hours.");
      setForm({ from_name:"", from_email:"", company:"", project_type:"", message:"" });
    } catch (err: any) {
      toast.error("Failed to send — try WhatsApp or direct email");
    } finally {
      setSubmitting(false);
    }
  };

  const field = "w-full bg-white/[0.03] border border-white/[0.07] rounded-xl px-4 py-3 text-white text-sm placeholder-white/15 outline-none focus:border-violet-500/40 transition-colors";

  return (
    <div className="max-w-5xl mx-auto px-6 py-12 pb-24 lg:pb-12">

      {/* Header */}
      <motion.div
        initial={{ opacity:0, y:20 }}
        animate={{ opacity:1, y:0 }}
        transition={{ duration:0.6, ease:[0.16,1,0.3,1] }}
        className="text-center mb-14"
      >
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-violet-500/20 bg-violet-500/8 text-xs text-violet-400 mb-4">
          <Sparkles className="w-3 h-3" /> Open for Custom Projects
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-4">
          Want something{" "}
          <span
            className="text-transparent bg-clip-text"
            style={{ backgroundImage:"linear-gradient(135deg,#7B2FFF,#00E5FF,#FF2D9B)" }}
          >
            custom-built?
          </span>
        </h1>
        <p className="text-white/35 text-base max-w-lg mx-auto leading-relaxed">
          LeadOS is a demo. I build production-grade AI automation systems, lead generation
          pipelines, N8N workflows, and full-stack apps. Let's talk about your project.
        </p>

        {/* Demo disclaimer */}
        <div
          className="mt-6 inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs text-amber-300/70"
          style={{ background:"rgba(245,158,11,0.06)", border:"1px solid rgba(245,158,11,0.15)" }}
        >
          ⚠️ This website is a <strong className="text-amber-300">portfolio demo only</strong> —
          not fully production grade. Contact me for enterprise-grade solutions.
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">

        {/* Contact links (left) */}
        <div className="lg:col-span-2 space-y-4">
          <p className="text-[10px] uppercase tracking-widest text-white/20 mb-3">Reach me directly</p>
          {CONTACT_LINKS.map((link, i) => {
            const Icon = link.icon;
            return (
              <GlassCard key={link.label} delay={i*0.08} tilt className="group">
                <a href={link.href} target="_blank" className="flex items-center gap-4 p-4">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{ background: `${link.color}15`, border: `1px solid ${link.color}25` }}
                  >
                    <Icon className="w-4 h-4" style={{ color:link.color }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-white text-sm font-medium">{link.label}</div>
                    <div className="text-white/30 text-xs truncate">{link.value}</div>
                    <div className="text-white/20 text-[10px] mt-0.5">{link.desc}</div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-white/10 group-hover:text-white/30 group-hover:translate-x-0.5 transition-all flex-shrink-0" />
                </a>
              </GlassCard>
            );
          })}

          {/* What I build */}
          <GlassCard delay={0.3} className="p-0 overflow-hidden group">
            <div className="p-5">
              <p className="text-[10px] uppercase tracking-widest text-white/20 mb-3">What I build</p>
              <div className="space-y-2">
                {[
                  "AI Lead Gen & Enrichment Pipelines",
                  "N8N Workflow Automation",
                  "WhatsApp + Email Outreach Bots",
                  "Full-Stack SaaS Products",
                  "AI Voice Agents (VAPI/Twilio)",
                  "Custom CRM Dashboards",
                ].map((item) => (
                  <div key={item} className="flex items-center gap-2 text-xs text-white/40">
                    <span className="w-1 h-1 rounded-full bg-violet-400 flex-shrink-0" />
                    {item}
                  </div>
                ))}
              </div>
            </div>
            
            {/* Mobile Mockup Asset */}
            <div className="relative h-48 mt-2 overflow-hidden border-t border-white/5">
              <img 
                src="/images/mobile-mockup.png" 
                alt="Mobile Optimization" 
                className="w-full h-full object-cover grayscale opacity-40 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-700 scale-110 group-hover:scale-100"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black to-transparent" />
              <div className="absolute bottom-4 left-5">
                <div className="text-[10px] font-black text-white uppercase tracking-widest">Mobile Optimized</div>
                <div className="text-[8px] text-white/40 uppercase tracking-widest mt-1">Responsive Terminal UI</div>
              </div>
            </div>
          </GlassCard>
        </div>

        {/* Contact form (right) */}
        <div className="lg:col-span-3">
          <GlassCard className="p-4 md:p-6">
            <h3 className="text-white font-medium mb-5">Send me a message</h3>
            <form ref={formRef} className="space-y-4">

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-[11px] text-white/30 flex items-center gap-1 mb-1.5 focus-within:text-violet-400 transition-colors">
                    <User className="w-3 h-3" /> Your Name *
                  </label>
                  <input
                    value={form.from_name}
                    onChange={e => setForm({...form, from_name: e.target.value})}
                    placeholder="Rahul Sharma"
                    className={field}
                  />
                </div>
                <div>
                  <label className="text-[11px] text-white/30 flex items-center gap-1 mb-1.5 focus-within:text-violet-400 transition-colors">
                    <Mail className="w-3 h-3" /> Email *
                  </label>
                  <input
                    type="email"
                    value={form.from_email}
                    onChange={e => setForm({...form, from_email: e.target.value})}
                    placeholder="rahul@company.com"
                    className={field}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-[11px] text-white/30 flex items-center gap-1 mb-1.5 focus-within:text-violet-400 transition-colors">
                    <Building className="w-3 h-3" /> Company / Project
                  </label>
                  <input
                    value={form.company}
                    onChange={e => setForm({...form, company: e.target.value})}
                    placeholder="Acme Corp (optional)"
                    className={field}
                  />
                </div>
                <div>
                  <label className="text-[11px] text-white/30 flex items-center gap-1 mb-1.5 focus-within:text-violet-400 transition-colors">
                    <Sparkles className="w-3 h-3" /> Project Type
                  </label>
                  <select
                    value={form.project_type}
                    onChange={e => setForm({...form, project_type: e.target.value})}
                    className={field}
                  >
                    <option value="">— Select type —</option>
                    {PROJECT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
              </div>

              <div>
                <label className="text-[11px] text-white/30 flex items-center gap-1 mb-1.5 focus-within:text-violet-400 transition-colors">
                  <FileText className="w-3 h-3" /> Tell me about your project *
                </label>
                <textarea
                  value={form.message}
                  onChange={e => setForm({...form, message: e.target.value})}
                  placeholder="What do you want to build? What problem are you solving? Budget range? Timeline?"
                  rows={5}
                  className={`${field} resize-none`}
                />
              </div>

              {/* USE UIVERSE SEND BUTTON HERE */}
              <div className="flex flex-col md:flex-row items-center justify-between pt-1 gap-4">
                <p className="text-[10px] text-white/20 text-center md:text-left">
                  Sent to saumyavishwam@gmail.com · Reply in 24h
                </p>
                <SendButton onClick={sendEmail} label={submitting ? "Sending..." : "Send Message"} />
              </div>
            </form>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
