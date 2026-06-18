import { useRef } from "react";
import { Link } from "react-router-dom";
import gsap from "gsap";

export function Logo() {
  const mythicRef = useRef<HTMLSpanElement>(null);
  const mindsRef = useRef<HTMLSpanElement>(null);
  const timelineRef = useRef<gsap.core.Timeline | null>(null);

  const collide = () => {
    const mythic = mythicRef.current;
    const minds = mindsRef.current;
    if (!mythic || !minds) return;

    timelineRef.current?.kill();
    const tl = gsap.timeline();
    timelineRef.current = tl;

    tl.set(mythic, { x: 70, opacity: 0 })
      .set(minds, { x: -70, opacity: 0 })
      .to(
        mythic,
        {
          keyframes: [
            { x: 0, opacity: 1, duration: 0.4, ease: "power3.in" },
            { x: -5, duration: 0.06, ease: "power1.out" },
            { x: 3, duration: 0.06, ease: "power1.out" },
            { x: 0, duration: 0.08, ease: "power1.out" },
          ],
        },
        0
      )
      .to(
        minds,
        {
          keyframes: [
            { x: 0, opacity: 1, duration: 0.4, ease: "power3.in" },
            { x: 5, duration: 0.06, ease: "power1.out" },
            { x: -3, duration: 0.06, ease: "power1.out" },
            { x: 0, duration: 0.08, ease: "power1.out" },
          ],
        },
        0
      )
      .to([mythic, minds], { scale: 1.12, duration: 0.08, ease: "power1.out" }, 0.36)
      .to([mythic, minds], { scale: 1, duration: 0.3, ease: "elastic.out(1, 0.45)" }, 0.44);
  };

  return (
    <Link
      to="/"
      onMouseEnter={collide}
      className="font-display text-2xl font-bold uppercase tracking-wider text-accent select-none"
      style={{ textShadow: "0 0 18px rgba(45, 212, 240, 0.45)" }}
    >
      <span ref={mythicRef} className="inline-block">
        Mythic
      </span>
      <span ref={mindsRef} className="inline-block">
        Minds
      </span>
    </Link>
  );
}
