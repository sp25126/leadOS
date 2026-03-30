"use client";
import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { Points, PointMaterial } from "@react-three/drei";
import * as THREE from "three";
import { useThemeStore } from "@/lib/themes/theme-store";

// Helper: hex to THREE.Color
const hex2color = (hex: string) => new THREE.Color(hex);

// ── Particle geometry factories ─────────────────────────────
function buildSpherePositions(count: number) {
  const pos = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const theta = Math.random() * Math.PI * 2;
    const phi   = Math.acos(2 * Math.random() - 1);
    const r     = 2.5 + Math.random() * 2.5;
    pos[i*3]   = r * Math.sin(phi) * Math.cos(theta);
    pos[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
    pos[i*3+2] = r * Math.cos(phi);
  }
  return pos;
}

function buildHelixPositions(count: number) {
  const pos = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const t     = (i / count) * Math.PI * 20;
    const strand = i % 2 === 0 ? 0 : Math.PI; // double helix
    const r     = 2.2 + Math.random() * 0.4;
    pos[i*3]   = r * Math.cos(t + strand);
    pos[i*3+1] = (i / count) * 10 - 5;        // vertical spread
    pos[i*3+2] = r * Math.sin(t + strand);
  }
  return pos;
}

function buildMatrixPositions(count: number) {
  // Columns of falling points — Matrix rain in 3D
  const cols = 40;
  const pos  = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const col   = i % cols;
    const xSpread = 8;
    pos[i*3]   = (col / cols) * xSpread - xSpread / 2;
    pos[i*3+1] = (Math.random() * 2 - 1) * 5;  // random y
    pos[i*3+2] = (Math.random() - 0.5) * 4;
  }
  return pos;
}

function buildGridPositions(count: number) {
  // Flat 2D grid in 3D space
  const side = Math.ceil(Math.sqrt(count));
  const pos  = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const x = (i % side) / side * 8 - 4;
    const z = Math.floor(i / side) / side * 8 - 4;
    pos[i*3]   = x;
    pos[i*3+1] = (Math.random() - 0.5) * 0.5;
    pos[i*3+2] = z;
  }
  return pos;
}

// ── Theme-aware Particles ────────────────────────────────────
export function ThemedParticles({
  mouseX, mouseY,
}: {
  mouseX: React.MutableRefObject<number>;
  mouseY: React.MutableRefObject<number>;
}) {
  const ref    = useRef<THREE.Points>(null!);
  const scene  = useThemeStore(s => s.theme.scene);

  const [positions, colors] = useMemo(() => {
    const count = scene.particleCount;

    const pos = (() => {
      switch (scene.particleShape) {
        case "helix":  return buildHelixPositions(count);
        case "matrix": return buildMatrixPositions(count);
        case "grid":   return buildGridPositions(count);
        default:       return buildSpherePositions(count);
      }
    })();

    const col = new Float32Array(count * 3);
    const palette = scene.particleColors.map(hex2color);
    for (let i = 0; i < count; i++) {
      const c = palette[i % palette.length];
      col[i*3]   = c.r;
      col[i*3+1] = c.g;
      col[i*3+2] = c.b;
    }

    return [pos, col];
  }, [scene.particleShape, scene.particleCount, scene.particleColors]);

  useFrame(({ clock }) => {
    if (!ref.current) return;
    const t = clock.getElapsedTime();

    // Matrix theme: rain effect — particles fall on Y
    if (scene.particleShape === "matrix") {
      const pos = ref.current.geometry.attributes.position.array as Float32Array;
      for (let i = 0; i < scene.particleCount; i++) {
        pos[i*3+1] -= 0.02; // fall down
        if (pos[i*3+1] < -5) pos[i*3+1] = 5; // reset to top
      }
      ref.current.geometry.attributes.position.needsUpdate = true;
    }

    ref.current.rotation.y = t * scene.rotationSpeed
      + mouseX.current * scene.mouseInfluence;
    ref.current.rotation.x = mouseY.current * (scene.mouseInfluence * 0.6);

    // Helix: gentle vertical oscillation
    if (scene.particleShape === "helix") {
      ref.current.position.y = Math.sin(t * 0.3) * 0.2;
    }
  });

  return (
    <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        vertexColors
        size={scene.particleSize}
        sizeAttenuation
        depthWrite={false}
        transparent
        opacity={0.9}
        blending={THREE.AdditiveBlending}
      />
    </Points>
  );
}

// ── Theme-aware Core ─────────────────────────────────────────
export function ThemedCore() {
  const orbRef  = useRef<THREE.Mesh>(null!);
  const glowRef = useRef<THREE.Mesh>(null!);
  const s       = useThemeStore(st => st.theme.scene);

  const geometry = useMemo(() => {
    switch (s.coreGeometry) {
      case "octahedron": return <octahedronGeometry args={[0.55, 0]} />;
      case "cube":       return <boxGeometry args={[0.8, 0.8, 0.8]} />;
      case "torus":      return <torusGeometry args={[0.45, 0.15, 16, 50]} />;
      default:           return <icosahedronGeometry args={[0.55, 1]} />;
    }
  }, [s.coreGeometry]);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (orbRef.current) {
      orbRef.current.rotation.y = t * s.rotationSpeed * 8;
      orbRef.current.rotation.z = t * s.rotationSpeed * 4;
      // Cube: also rotate X for tumbling effect
      if (s.coreGeometry === "cube") {
        orbRef.current.rotation.x = t * s.rotationSpeed * 5;
      }
    }
    if (glowRef.current) {
      const pulse = 1 + Math.sin(t * (s.coreGeometry === "cube" ? 2 : 1.2)) * 0.06;
      glowRef.current.scale.setScalar(pulse);
    }
  });

  const coreColor = useMemo(() => hex2color(s.coreColor), [s.coreColor]);
  const [rc1, rc2, rc3] = useMemo(() => s.ringColors.map(hex2color), [s.ringColors]);

  return (
    <group>
      <mesh ref={glowRef}>
        <sphereGeometry args={[0.9, 16, 16]} />
        <meshBasicMaterial color={coreColor} transparent opacity={0.05} side={THREE.BackSide} />
      </mesh>

      <mesh ref={orbRef}>
        {geometry}
        <meshBasicMaterial
          color={coreColor}
          wireframe={s.coreWireframe}
          transparent
          opacity={s.coreWireframe ? 0.4 : 0.7}
        />
      </mesh>

      <pointLight color={coreColor}  intensity={3.0}  distance={6} />
      <pointLight color={rc1 || coreColor}  intensity={1.2}  distance={4} position={[2.5, 1, 0]} />
      <pointLight color={rc2 || coreColor}  intensity={0.9}  distance={3} position={[-2, -1.5, 1]} />
    </group>
  );
}

// ── Theme-aware Orbital Rings ────────────────────────────────
export function ThemedRings() {
  const r1 = useRef<THREE.Mesh>(null!);
  const r2 = useRef<THREE.Mesh>(null!);
  const r3 = useRef<THREE.Mesh>(null!);
  const s  = useThemeStore(st => st.theme.scene);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    const speed = s.rotationSpeed * 5;
    if (r1.current) r1.current.rotation.z = t * speed;
    if (r2.current) {
      r2.current.rotation.x = t * speed * 0.75;
      r2.current.rotation.y = t * speed * 0.5;
    }
    if (r3.current) r3.current.rotation.y = -t * speed * 1.25;

    // Nord Ice: rings move slowly apart (breathe)
    if (s.coreGeometry === "octahedron") {
      const breathe = 1 + Math.sin(t * 0.5) * 0.05;
      if (r2.current) r2.current.scale.setScalar(breathe);
    }
  });

  const [c1, c2, c3] = useMemo(() => s.ringColors.map(hex2color), [s.ringColors]);

  return (
    <group>
      <mesh ref={r1}>
        <torusGeometry args={[1.1, 0.005, 8, 120]} />
        <meshBasicMaterial color={c1} transparent opacity={0.35} side={THREE.DoubleSide} />
      </mesh>
      <mesh ref={r2}>
        <torusGeometry args={[1.6, 0.004, 8, 120]} />
        <meshBasicMaterial color={c2} transparent opacity={0.22} side={THREE.DoubleSide} />
      </mesh>
      <mesh ref={r3} rotation={[Math.PI / 4, 0, 0]}>
        <torusGeometry args={[2.0, 0.003, 8, 120]} />
        <meshBasicMaterial color={c3} transparent opacity={0.15} side={THREE.DoubleSide} />
      </mesh>
    </group>
  );
}
