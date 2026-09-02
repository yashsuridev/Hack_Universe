/**
 * HeroNetworkCanvas.tsx
 *
 * Lazy-loaded Three.js canvas containing the animated NetworkMesh.
 * Imported dynamically from HeroSection so it is code-split.
 */

import { useRef, useMemo, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Line, Sphere } from '@react-three/drei';
import * as THREE from 'three';

/* ─────────────────────────────────────────────
   Constants
───────────────────────────────────────────── */
const NODE_COUNT = 50;
const SPREAD = 4.5;          // random placement radius
const CONNECT_DIST = 1.6;    // max distance to draw a line between nodes
const ACCENT = '#00ffc8';
const MAX_TILT = 0.15;       // radians for mouse parallax

/* ─────────────────────────────────────────────
   Helper – random float in [-half, half]
───────────────────────────────────────────── */
const rand = (half: number) => (Math.random() - 0.5) * 2 * half;

/* ─────────────────────────────────────────────
   NetworkMesh – inner Three.js scene object
───────────────────────────────────────────── */
function NetworkMesh() {
  const groupRef = useRef<THREE.Group>(null!);
  const mouseRef = useRef({ x: 0, y: 0 });

  /* Build 50 random 3-D points once */
  const nodes = useMemo<THREE.Vector3[]>(() => {
    return Array.from({ length: NODE_COUNT }, () =>
      new THREE.Vector3(rand(SPREAD), rand(SPREAD * 0.6), rand(SPREAD * 0.4))
    );
  }, []);

  /* Pair nodes that are within CONNECT_DIST of each other */
  const edges = useMemo<[THREE.Vector3, THREE.Vector3][]>(() => {
    const pairs: [THREE.Vector3, THREE.Vector3][] = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        if (nodes[i].distanceTo(nodes[j]) < CONNECT_DIST) {
          pairs.push([nodes[i], nodes[j]]);
        }
      }
    }
    return pairs;
  }, [nodes]);

  /* Mouse parallax listener */
  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      // normalise to [-1, 1]
      mouseRef.current.x = (e.clientX / window.innerWidth - 0.5) * 2;
      mouseRef.current.y = (e.clientY / window.innerHeight - 0.5) * 2;
    };
    window.addEventListener('mousemove', onMove, { passive: true });
    return () => window.removeEventListener('mousemove', onMove);
  }, []);

  /* Per-frame animation */
  useFrame(() => {
    if (!groupRef.current) return;

    // Slow auto-rotation
    groupRef.current.rotation.y += 0.001;
    groupRef.current.rotation.x += 0.0003;

    // Mouse parallax – lerp toward target tilt
    const targetX = mouseRef.current.y * MAX_TILT;
    const targetY = mouseRef.current.x * MAX_TILT;
    groupRef.current.rotation.x +=
      (targetX - groupRef.current.rotation.x) * 0.04;
    groupRef.current.rotation.y +=
      (targetY - groupRef.current.rotation.y) * 0.04;
  });

  return (
    <group ref={groupRef}>
      {/* Nodes */}
      {nodes.map((pos, i) => (
        <Sphere key={`node-${i}`} args={[0.04, 8, 8]} position={pos}>
          <meshStandardMaterial
            color={ACCENT}
            emissive={ACCENT}
            emissiveIntensity={1.2}
            roughness={0.2}
            metalness={0.5}
          />
        </Sphere>
      ))}

      {/* Edges */}
      {edges.map(([a, b], i) => (
        <Line
          key={`edge-${i}`}
          points={[a, b]}
          color={ACCENT}
          lineWidth={0.4}
          transparent
          opacity={0.18}
        />
      ))}
    </group>
  );
}

/* ─────────────────────────────────────────────
   Ambient / point lights
───────────────────────────────────────────── */
function SceneLights() {
  return (
    <>
      <ambientLight intensity={0.3} />
      <pointLight position={[5, 5, 5]} intensity={1.2} color={ACCENT} />
      <pointLight position={[-5, -5, -3]} intensity={0.6} color="#0040ff" />
    </>
  );
}

/* ─────────────────────────────────────────────
   Exported Canvas wrapper (the lazy chunk)
───────────────────────────────────────────── */
export function HeroNetworkCanvas() {
  return (
    <Canvas
      camera={{ position: [0, 0, 6], fov: 55 }}
      dpr={[1, 1.5]}
      style={{
        position: 'absolute',
        inset: 0,
        zIndex: 3,
        background: 'transparent',
      }}
      gl={{ alpha: true, antialias: true }}
    >
      <SceneLights />
      <NetworkMesh />
    </Canvas>
  );
}
