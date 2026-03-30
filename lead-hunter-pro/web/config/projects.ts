// THE SINGLE SOURCE OF TRUTH for all portfolio projects
// Add new project here — it auto-appears on /projects page
// Featured projects appear on homepage

export interface Project {
  slug: string;
  name: string;
  tagline: string;
  description: string;
  status: "LIVE" | "BETA" | "BUILDING" | "ARCHIVED";
  featured: boolean;
  liveUrl: string;
  githubUrl: string;
  videoUrl?: string;
  tech: string[];
  color: string;
  metrics?: { label: string; value: string }[];
}

export const projects: Project[] = [
  {
    slug: "leados",
    name: "LeadOS",
    tagline: "AI lead generation & autonomous outreach engine",
    description: "LeadOS is an enterprise-grade AI lead generation platform that automates the entire process of finding, enrichment, and contacting potential B2B leads via Email and WhatsApp.",
    status: "LIVE",
    featured: true,
    liveUrl: "https://webrox.xyz/leados",
    githubUrl: "https://github.com/sp25126/leados-agent",
    tech: ["FastAPI", "Next.js 14", "Gemini AI", "Supabase", "Cloudflare"],
    color: "indigo",
    metrics: [
      { label: "Leads/run", value: "80" },
      { label: "Enrichment", value: "Phone + Email" },
      { label: "Cost", value: "₹0/month" },
    ],
  },
  {
    slug: "api-hub",
    name: "Webrox API Hub",
    tagline: "The AI Lead Engine — Available as an API",
    description: "A public API platform that allows developers to plug AI lead generation into their own SaaS, CRM, or automation workflows.",
    status: "BETA",
    featured: true,
    liveUrl: "https://webrox.xyz/api-hub",
    githubUrl: "https://github.com/sp25126/leados-agent",
    tech: ["FastAPI", "Next.js 14", "Cloudflare Workers", "Supabase"],
    color: "purple",
    metrics: [
      { label: "Uptime", value: "99.9%" },
      { label: "Latency", value: "<200ms" },
    ],
  },
];
