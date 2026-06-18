import type { ReactNode } from "react";
import { NavBar } from "./NavBar";
import { SceneBackground } from "./SceneBackground";
import { Footer } from "./Footer";
import { MascotCompanion } from "@/components/mascot/MascotCompanion";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="relative flex min-h-screen flex-col overflow-x-hidden">
      <SceneBackground />
      <div
        className="pointer-events-none fixed -left-32 top-24 -z-10 h-80 w-80 rounded-full bg-accent/10 blur-3xl"
        aria-hidden
      />
      <div
        className="pointer-events-none fixed -right-24 top-1/2 -z-10 h-96 w-96 rounded-full bg-gold/8 blur-3xl"
        aria-hidden
      />
      <div
        className="pointer-events-none fixed bottom-0 left-1/3 -z-10 h-72 w-72 rounded-full bg-ally/8 blur-3xl"
        aria-hidden
      />
      <NavBar />
      <main className="relative z-0 mx-auto w-full max-w-7xl flex-1 px-6 py-8">{children}</main>
      <Footer />
      <MascotCompanion />
    </div>
  );
}
