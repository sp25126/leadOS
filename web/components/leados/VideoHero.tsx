"use client";
import { useRef, useEffect, useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";

interface Props {
  videoSrc?: string;   // /videos/hero-orb.mp4
  posterSrc?: string;  // /images/hero-poster.jpg
  children?: React.ReactNode;
}

export default function VideoHero({ videoSrc, posterSrc, children }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [videoReady, setVideoReady] = useState(false);

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;
    v.muted = true;
    v.playsInline = true;
    v.loop = true;
    v.play().then(() => setVideoReady(true)).catch(() => setVideoReady(false));
  }, []);

  return (
    <div className="relative w-full h-full overflow-hidden">
      {/* Video background */}
      {videoSrc && (
        <motion.video
          ref={videoRef}
          src={videoSrc}
          playsInline muted loop autoPlay 
          preload="metadata"
          className="absolute inset-0 w-full h-full object-cover"
          initial={{ opacity: 0 }}
          animate={{ opacity: videoReady ? 0.35 : 0 }}
          transition={{ duration: 1.5 }}
          style={{ mixBlendMode: "screen" }}
        />
      )}

      {/* Optimized Poster Image while video loads */}
      {posterSrc && !videoReady && (
        <Image
          src={posterSrc}
          alt="Hero Background"
          fill
          priority
          className="object-cover opacity-50"
        />
      )}

      {/* CSS fallback gradient (shows when no video or while loading) */}
      {!videoReady && (
        <div
          className="absolute inset-0"
          style={{
            background:
              "radial-gradient(ellipse 120% 80% at 60% 40%, rgba(123,47,255,0.12) 0%, rgba(0,229,255,0.06) 40%, transparent 70%)",
          }}
        />
      )}

      {/* Dark vignette overlay */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 80% 70% at 50% 50%, transparent 20%, rgba(0,0,0,0.6) 70%, #000 100%)",
        }}
      />

      {/* Content on top */}
      <div className="relative z-10 w-full h-full">{children}</div>
    </div>
  );
}
