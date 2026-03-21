"use client";
import { motion } from "framer-motion";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect, useRef } from "react";
import { useThemeStore } from "@/lib/themes/theme-store";
import { LayoutDashboard, Search, Users, Send, History, Settings, Zap } from "lucide-react";
import { ThemeTrigger } from "./ThemeSwitcher";

const NAV = [
  { href: "/leados",          icon: LayoutDashboard, label: "Dashboard" },
  { href: "/leados/hunt",     icon: Search,          label: "Hunt"      },
  { href: "/leados/leads",    icon: Users,           label: "Leads"     },
  { href: "/leados/outreach", icon: Send,            label: "Broadcast" },
  { href: "/leados/history",  icon: History,         label: "History"   },
  { href: "/leados/settings", icon: Settings,        label: "Settings"  },
];

interface Props { bannerVisible?: boolean; }

export default function LeadOSNav({ bannerVisible = false }: Props) {
  const path = usePathname();
  const themeId = useThemeStore(s => s.theme.id);
  const isNord = themeId === "nord";
  const [visible, setVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      if (currentScrollY > lastScrollY && currentScrollY > 100) {
        setVisible(false);
      } else {
        setVisible(true);
      }
      setLastScrollY(currentScrollY);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, [lastScrollY]);

  const topOffset = bannerVisible ? 44 : 12;
  const hideY = -100;

  return (
    <>
      {/* Desktop nav */}
      <motion.nav
        initial={{ top: topOffset, x: "-50%" }}
        animate={{ 
          top: visible ? topOffset : hideY,
          opacity: visible ? 1 : 0,
          x: "-50%"
        }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="fixed left-1/2 z-[50] hidden lg:block"
      >
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="flex items-center gap-0.5 px-2 py-1.5 rounded-full"
          style={{
            background: "rgba(10,10,10,0.4)",
            border: "1px solid rgba(255,255,255,0.08)",
            backdropFilter: "blur(40px)",
            WebkitBackdropFilter: "blur(40px)",
            boxShadow: "0 0 0 1px rgba(255,255,255,0.03), 0 8px 32px rgba(0,0,0,0.5)",
          }}
        >
          {/* Background Image asset - Hidden in Nord */}
          {!isNord && (
            <div className="absolute inset-0 rounded-full overflow-hidden pointer-events-none opacity-[0.14]">
              <img 
                src="/images/hero-poster.png" 
                alt="" 
                className="w-full h-full object-cover"
              />
            </div>
          )}
          {/* Brand */}
          <Link href="/leados" className="flex items-center gap-2 px-3 py-1.5 mr-1">
            <motion.div
              className="w-5 h-5 rounded-md flex items-center justify-center"
              style={{ background: "linear-gradient(135deg, #7B2FFF, #00E5FF)" }}
              animate={{ boxShadow: [
                "0 0 8px rgba(123,47,255,0.4)",
                "0 0 16px rgba(123,47,255,0.7), 0 0 32px rgba(0,229,255,0.2)",
                "0 0 8px rgba(123,47,255,0.4)"
              ]}}
              transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
            >
              <Zap className="w-2.5 h-2.5 text-white" />
            </motion.div>
            <span className="text-white text-sm font-semibold tracking-[-0.02em]">LeadOS</span>
            <span className="text-[9px] px-1.5 py-0.5 rounded-full font-medium"
              style={{ background: "rgba(123,47,255,0.15)", color: "#a78bfa", border: "1px solid rgba(123,47,255,0.25)" }}>
              BETA
            </span>
          </Link>

          <div className="w-px h-4 mx-1" style={{ background: "rgba(255,255,255,0.05)" }} />

          {NAV.map(({ href, icon: Icon, label }) => {
            const active = path === href || (href !== "/leados" && path.startsWith(href));
            return (
              <Link key={href} href={href}
                className="relative flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs group"
              >
                {active && (
                  <motion.span
                    layoutId="nav-active"
                    className="absolute inset-0 rounded-full"
                    style={{ background: isNord ? "rgba(136,192,208,0.18)" : "rgba(255,255,255,0.07)" }}
                    transition={isNord ? { duration: 0.25, ease: "easeOut" } : { type: "spring", stiffness: 500, damping: 40 }}
                  />
                )}
                <Icon className={`w-3.5 h-3.5 relative z-10 transition-colors duration-200
                  ${active ? "text-white" : "text-white/30 group-hover:text-white/55"}`}
                />
                <span className={`relative z-10 transition-colors duration-200 tracking-[-0.01em]
                  ${active ? "text-white font-medium" : "text-white/30 group-hover:text-white/55"}`}>
                  {label}
                </span>
              </Link>
            );
          })}

          <div className="w-px h-4 mx-2" style={{ background: "rgba(255,255,255,0.05)" }} />
          <ThemeTrigger />
        </motion.div>
      </motion.nav>

      {/* Mobile bottom tab bar */}
      <nav className="fixed bottom-0 left-0 right-0 z-[60] lg:hidden"
        style={{
          paddingBottom: "env(safe-area-inset-bottom, 0px)",
          background: "rgba(5,5,5,0.92)",
          borderTop: "1px solid rgba(255,255,255,0.05)",
          backdropFilter: "blur(24px)",
        }}
      >
        <div className="flex items-center justify-around px-1 pt-2 pb-3">
          {NAV.map(({ href, icon: Icon, label }) => {
            const active = path === href || (href !== "/leados" && path.startsWith(href));
            return (
              <Link key={href} href={href}
                className="relative flex flex-col items-center gap-1 px-3 py-1 rounded-xl min-w-[52px]"
              >
                {active && (
                  <motion.span layoutId="mob-active"
                    className="absolute inset-0 rounded-xl"
                    style={{ background: isNord ? "rgba(136,192,208,0.15)" : "rgba(123,47,255,0.12)" }}
                    transition={isNord ? { duration: 0.25, ease: "easeOut" } : { type: "spring", stiffness: 500, damping: 40 }}
                  />
                )}
                <Icon className={`w-5 h-5 relative z-10 ${active ? "text-violet-400" : "text-white/25"}`} />
                <span className={`text-[9px] relative z-10 tracking-wide ${active ? "text-violet-300 font-medium" : "text-white/25"}`}>
                  {label}
                </span>
              </Link>
            );
          })}
        </div>
      </nav>
    </>
  );
}
