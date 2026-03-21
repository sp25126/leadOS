"use client";
import { useEffect, useState } from "react";
import LeadOSNav from "@/components/leados/LeadOSNav";
import CursorSpotlight from "@/components/ui/CursorSpotlight";
import { Toaster } from "sonner";
import DemoBanner from "@/components/leados/DemoBanner";
import ThemeTransition from "@/components/ui/ThemeTransition";
import DotGrid from "@/components/ui/DotGrid";

export default function ClientLayoutWrapper({ children }: { children: React.ReactNode }) {
  const [bannerVisible, setBannerVisible] = useState(true);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setBannerVisible(!sessionStorage.getItem("leados-demo-banner"));
    }
    let lenis: any;
    import("lenis").then(({ default: Lenis }) => {
      lenis = new Lenis({ 
        lerp: 0.075, 
        smoothWheel: true,
        syncTouch: true,
      });
      const raf = (time: number) => { 
        lenis.raf(time); 
        requestAnimationFrame(raf); 
      };
      requestAnimationFrame(raf);
    });
    return () => lenis?.destroy();
  }, []);

  return (
    <>
      <ThemeTransition />
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <DotGrid />
      </div>
      <CursorSpotlight />
      <DemoBanner onVisibilityChange={setBannerVisible} />
      <LeadOSNav bannerVisible={bannerVisible} />
      
      <main 
        className="relative z-10"
        style={{
          paddingTop: bannerVisible ? "92px" : "80px",
        }}
      >
        {children}
      </main>

      <Toaster
        theme="dark"
        position="bottom-right"
        offset={16}
        toastOptions={{
          style: {
            background: "rgba(10,10,10,0.95)",
            border: "1px solid rgba(255,255,255,0.08)",
            backdropFilter: "blur(24px)",
            WebkitBackdropFilter: "blur(24px)",
            color: "#fff",
            borderRadius: "14px",
            fontSize: "13px",
          },
        }}
      />
    </>
  );
}
