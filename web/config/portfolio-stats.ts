// web/config/portfolio-stats.ts
// Static configuration for portfolio pages to ensure zero-backend dependency.

export const PORTFOLIO_STATS = {
  totalLeads: 125430,
  campaignsActive: 48,
  successRate: "94.2%",
  avgEnrichmentTime: "1.2s",
  outreachSent: 84200,
  membersServed: 240,
  topLocations: ["San Francisco", "London", "Bangalore", "Dubai"],
  recentSectors: ["SaaS", "Real Estate", "Healthcare", "E-commerce"],
}

export const PORTFOLIO_CONFIG = {
  siteName: "Lead Hunter Pro",
  tagline: "Enterprise-Grade Lead Discovery & Enrichment",
  contactEmails: {
    sales: "sales@leadhunter.pro",
    support: "support@leadhunter.pro"
  },
  socialLinks: {
    linkedin: "https://linkedin.com/company/leadhunter",
    twitter: "https://twitter.com/leadhunter"
  }
}
