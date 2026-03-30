export type ThemeId = "cosmic" | "nord";

export interface ThemeConfig {
  id: ThemeId;
  name: string;
  tagline: string;

  // ── Color tokens ─────────────────────────────────────────
  colors: {
    background:      string;
    surface:         string;
    surfaceAlt:      string;
    border:          string;
    borderHover:     string;
    accent:          string;
    accentSoft:      string;   // accent @ 15% opacity
    accentSecondary: string;
    accentTertiary:  string;
    textPrimary:     string;
    textSecondary:   string;
    textMuted:       string;
    textGhost:       string;
    success:         string;
    error:           string;
    warning:         string;
    gradientPrimary: [string, string, string];  // 3-stop
    gradientHero:    [string, string, string];
  };

  // ── Typography ───────────────────────────────────────────
  typography: {
    fontDisplay:   string;   // CSS font-family for headings
    fontBody:      string;   // CSS font-family for body
    fontMono:      string;   // CSS font-family for code/ids
    trackingHero:  string;   // letter-spacing for hero title
    trackingBody:  string;
    lineHeightBody:string;
    weightDisplay: number;
    weightBody:    number;
  };

  // ── Shape ────────────────────────────────────────────────
  shape: {
    cardRadius:     string;
    inputRadius:    string;
    buttonRadius:   string;
    navRadius:      string;
    badgeRadius:    string;
  };

  // ── Motion ───────────────────────────────────────────────
  motion: {
    easing:        number[];   // cubic-bezier values [x1,y1,x2,y2]
    durationFast:  number;     // ms
    durationBase:  number;
    durationSlow:  number;
    hoverScale:    number;
    pressScale:    number;
    staggerDelay:  number;
  };

  // ── 3D Scene ─────────────────────────────────────────────
  scene: {
    particleColors:      string[];   // hex colors for particles
    particleSize:        number;
    particleCount:       number;
    particleShape:      "sphere" | "grid" | "helix" | "matrix";
    coreColor:           string;
    coreWireframe:       boolean;
    coreGeometry:       "icosahedron" | "octahedron" | "cube" | "torus";
    ringColors:          string[];
    ambientLightColor:   string;
    rotationSpeed:       number;
    mouseInfluence:      number;
    bloomStrength:       number;
  };

  // ── Layout ───────────────────────────────────────────────
  layout: {
    navPosition:        "top-center" | "top-left" | "bottom-center";
    cardPadding:        string;
    sectionGap:         string;
    contentMaxWidth:    string;
    gridCols:           number;   // default grid columns
    statCardLayout:     "horizontal" | "vertical";
  };

  // ── Shadows & Glow ───────────────────────────────────────
  fx: {
    cardShadow:      string;
    accentGlow:      string;
    buttonGlow:      string;
    cursorColor:     string;
    scanlines:       boolean;   // CRT scanline overlay
    gridDots:        boolean;   // dot-grid background texture
    noiseOverlay:    boolean;
    glitchOnHover:   boolean;
  };
}

// ════════════════════════════════════════════════════════════
// THEME 1: COSMIC DARK (existing — DO NOT change behavior)
// ════════════════════════════════════════════════════════════
export const cosmicDark: ThemeConfig = {
  id: "cosmic",
  name: "Cosmic Dark",
  tagline: "Deep space intelligence",

  colors: {
    background:      "#000000",
    surface:         "#0a0a0a",
    surfaceAlt:      "#111111",
    border:          "rgba(255,255,255,0.06)",
    borderHover:     "rgba(255,255,255,0.12)",
    accent:          "#7B2FFF",
    accentSoft:      "rgba(123,47,255,0.15)",
    accentSecondary: "#00E5FF",
    accentTertiary:  "#FF2D9B",
    textPrimary:     "#FFFFFF",
    textSecondary:   "rgba(255,255,255,0.5)",
    textMuted:       "rgba(255,255,255,0.25)",
    textGhost:       "rgba(255,255,255,0.08)",
    success:         "#10b981",
    error:           "#ef4444",
    warning:         "#f59e0b",
    gradientPrimary: ["#7B2FFF", "#00E5FF", "#FF2D9B"],
    gradientHero:    ["#7B2FFF", "#4F46E5", "#00E5FF"],
  },

  typography: {
    fontDisplay:    "'Inter', system-ui, sans-serif",
    fontBody:       "'Inter', system-ui, sans-serif",
    fontMono:       "'JetBrains Mono', monospace",
    trackingHero:   "-0.04em",
    trackingBody:   "-0.01em",
    lineHeightBody: "1.65",
    weightDisplay:  700,
    weightBody:     400,
  },

  shape: {
    cardRadius:   "16px",
    inputRadius:  "12px",
    buttonRadius: "9999px",
    navRadius:    "9999px",
    badgeRadius:  "9999px",
  },

  motion: {
    easing:       [0.16, 1, 0.3, 1],
    durationFast: 150,
    durationBase: 350,
    durationSlow: 700,
    hoverScale:   1.02,
    pressScale:   0.97,
    staggerDelay: 0.06,
  },

  scene: {
    particleColors:   ["#7B2FFF", "#00E5FF", "#FF2D9B", "#ffffff"],
    particleSize:     0.018,
    particleCount:    2000,
    particleShape:    "sphere",
    coreColor:        "#7B2FFF",
    coreWireframe:    true,
    coreGeometry:     "icosahedron",
    ringColors:       ["#7B2FFF", "#00E5FF", "#FF2D9B"],
    ambientLightColor:"#7B2FFF",
    rotationSpeed:    0.04,
    mouseInfluence:   0.3,
    bloomStrength:    1.5,
  },

  layout: {
    navPosition:     "top-center",
    cardPadding:     "24px",
    sectionGap:      "48px",
    contentMaxWidth: "1200px",
    gridCols:        4,
    statCardLayout:  "vertical",
  },

  fx: {
    cardShadow:   "none",
    accentGlow:   "0 0 40px rgba(123,47,255,0.15)",
    buttonGlow:   "0 0 20px rgba(123,47,255,0.4)",
    cursorColor:  "rgba(123,47,255,0.06)",
    scanlines:    false,
    gridDots:     false,
    noiseOverlay: true,
    glitchOnHover:false,
  },
};

// ════════════════════════════════════════════════════════════
// THEME 2: NORD ICE
// Arctic calm. Crystalline slate. Breathable white space.
// Inspired by nordtheme.com — Polar Night + Frost + Snow Storm
// ════════════════════════════════════════════════════════════
export const nordIce: ThemeConfig = {
  id: "nord",
  name: "Nord Ice",
  tagline: "Arctic clarity",

  colors: {
    background:      "#0F111A",    // Deeper Nord slate-blue instead of black
    surface:         "#161922",    // Adjusted Nord surface
    surfaceAlt:      "#1A1D27",    // Adjusted Nord surface alt
    border:          "rgba(236,239,244,0.08)",   // Nord Snow Storm 3 @ 8%
    borderHover:     "rgba(136,192,208,0.25)",   // Nord Frost 2 @ 25%
    accent:          "#88C0D0",    // Nord Frost 2
    accentSoft:      "rgba(208,135,112,0.15)",   // Nord Aurora Pink/Orange soft
    accentSecondary: "#81A1C3",    // Nord Frost 3
    accentTertiary:  "#B48EAD",    // Nord Aurora purple
    textPrimary:     "#ECEFF4",    // Nord Snow Storm 3
    textSecondary:   "#9AADBE",    // Frost muted
    textMuted:       "rgba(154,173,190,0.4)",
    textGhost:       "rgba(236,239,244,0.06)",
    success:         "#A3BE8C",    // Nord Aurora green
    error:           "#BF616A",    // Nord Aurora red
    warning:         "#EBCB8B",    // Nord Aurora yellow
    gradientPrimary: ["#ECEFF4", "#D08770", "#B48EAD"], // White + Pink/Peach + Purple
    gradientHero:    ["#88C0D0", "#D08770", "#ECEFF4"],
  },

  typography: {
    fontDisplay:    "'DM Sans', system-ui, sans-serif",
    fontBody:       "'DM Sans', system-ui, sans-serif",
    fontMono:       "'JetBrains Mono', monospace",
    trackingHero:   "-0.02em",     // looser than Cosmic — breathable
    trackingBody:   "0em",
    lineHeightBody: "1.75",        // more open line height
    weightDisplay:  600,           // medium-bold, not ultra-bold
    weightBody:     400,
  },

  shape: {
    cardRadius:   "20px",          // softer curves everywhere
    inputRadius:  "14px",
    buttonRadius: "14px",          // NOT pill — rectangular-round
    navRadius:    "16px",          // NOT full pill — rectangular nav
    badgeRadius:  "6px",           // small square badges
  },

  motion: {
    easing:       [0.25, 0.46, 0.45, 0.94],  // easeOutQuad — calm, not elastic
    durationFast: 200,
    durationBase: 450,             // slightly slower, more graceful
    durationSlow: 900,
    hoverScale:   1.01,            // subtle — no aggressive zoom
    pressScale:   0.98,
    staggerDelay: 0.09,            // slower stagger — calmer feel
  },

  scene: {
    particleColors:    ["#ECEFF4", "#D08770", "#88C0D0", "#B48EAD", "#E5E9F0"], // White + Pink/Peach + Nord Blues
    particleSize:      0.012,
    particleCount:     3000,
    particleShape:     "helix",
    coreColor:         "#ECEFF4",    // WHITE core
    coreWireframe:     false,
    coreGeometry:      "octahedron",
    ringColors:        ["#ECEFF4", "#D08770", "#88C0D0"], // White + Pink + Blue
    ambientLightColor: "#D08770",    // Pink/Peach ambient light
    rotationSpeed:     0.02,       // very slow — glacial calm
    mouseInfluence:    0.15,       // subtle mouse response
    bloomStrength:     0.8,
  },

  layout: {
    navPosition:     "top-left",   // LEFT-ALIGNED nav — different placement
    cardPadding:     "28px",       // more generous padding
    sectionGap:      "64px",       // more breathable section gaps
    contentMaxWidth: "1100px",     // narrower column for readability
    gridCols:        3,            // 3-col stat grid instead of 4
    statCardLayout:  "horizontal", // stat cards are horizontal rows
  },

  fx: {
    cardShadow:
      "0 4px 24px rgba(0,0,0,0.3), 0 1px 0 rgba(236,239,244,0.04) inset",
    accentGlow:    "0 0 32px rgba(136,192,208,0.08)",
    buttonGlow:    "0 4px 16px rgba(136,192,208,0.25)",
    cursorColor:   "rgba(136,192,208,0.05)",
    scanlines:     false,
    gridDots:      true,           // subtle dot grid — maps/data feel
    noiseOverlay:  false,          // CLEAN — no noise
    glitchOnHover: false,
  },
};

export const THEMES: ThemeConfig[] = [cosmicDark, nordIce];
export type { ThemeConfig as ThemeData };
