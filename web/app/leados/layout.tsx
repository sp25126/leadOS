import ClientLayoutWrapper from "@/components/leados/ClientLayoutWrapper";
import ThemeProvider from "@/components/providers/ThemeProvider";
import DotGrid from "@/components/ui/DotGrid";
import ThemeTransition from "@/components/ui/ThemeTransition";

export const metadata = {
  title: "LeadOS — AI Lead Intelligence Platform",
  description: "5-stage AI-powered lead generation and enrichment pipeline. Hunt leads, enrich with Google Maps + OSINT, score with AI, and launch outreach. Demo by Saumy Vishwakarma.",
  openGraph: {
    title: "LeadOS — AI Lead Intelligence",
    description: "Demo AI lead generation platform. Contact for custom builds.",
    images: [{ url: "/images/og-image.png", width: 1200, height: 630 }],
  },
};

export default function LeadOSLayout({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <ClientLayoutWrapper>{children}</ClientLayoutWrapper>
    </ThemeProvider>
  );
}
