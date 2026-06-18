import { motion } from "framer-motion";
import { useUiStore } from "@/store/uiStore";

export function SceneBackground() {
  const theme = useUiStore((s) => s.theme);
  const isDark = theme === "dark";

  return (
    <div className="pointer-events-none fixed inset-0 -z-20 overflow-hidden" aria-hidden>
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: "url(/assets/backgrounds/land-of-dawn.jpg)",
          filter: "blur(3px) saturate(85%)",
          transform: "scale(1.02)",
        }}
      />
      <motion.div
        className="absolute inset-0"
        animate={{
          background: isDark
            ? "linear-gradient(180deg, rgba(5,11,20,0.78) 0%, rgba(10,24,34,0.6) 50%, rgba(5,11,20,0.82) 100%)"
            : "linear-gradient(180deg, rgba(244,248,250,0.88) 0%, rgba(244,248,250,0.78) 50%, rgba(244,248,250,0.9) 100%)",
        }}
        transition={{ duration: 1.2, ease: "easeInOut" }}
      />
    </div>
  );
}
