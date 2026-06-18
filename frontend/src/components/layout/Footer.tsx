import { Link } from "react-router-dom";
import { User } from "lucide-react";
import { GithubIcon, InstagramIcon, LinkedinIcon } from "./BrandIcons";

const EXPLORE_LINKS = [
  { to: "/draft", label: "Draft Room" },
  { to: "/heroes", label: "Heroes" },
  { to: "/builds", label: "Builds" },
  { to: "/meta", label: "Meta" },
];

const SOCIAL_LINKS = [
  { href: "https://github.com/Aunkush21", label: "GitHub", icon: GithubIcon },
  { href: "https://www.instagram.com/_fried.rice21/", label: "Instagram", icon: InstagramIcon },
  {
    href: "https://www.linkedin.com/in/aunkush-barua-341351363/",
    label: "LinkedIn",
    icon: LinkedinIcon,
  },
  { href: "https://www.instagram.com/_fried.rice21/", label: "Portfolio", icon: User },
];

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="relative z-0 mt-20 border-t border-glass-border">
      <div className="mx-auto grid max-w-7xl gap-10 px-6 py-12 md:grid-cols-3">
        <div className="space-y-3">
          <p className="font-display text-xl font-bold uppercase tracking-wider text-accent">
            MythicMinds
          </p>
          <p className="max-w-sm text-sm text-muted">
            AI-powered draft intelligence, hero recommendations, and build optimization for Mobile
            Legends: Bang Bang.
          </p>
          <p className="max-w-sm text-xs text-muted">
            Unofficial fan project — not affiliated with or endorsed by Moonton.
          </p>
          <p className="max-w-sm text-xs text-muted">
            All Mobile Legends: Bang Bang assets, trademarks, and content belong to Moonton.
          </p>
        </div>

        <div className="space-y-3">
          <p className="text-sm font-semibold text-foreground">Explore</p>
          <nav className="flex flex-col gap-2">
            {EXPLORE_LINKS.map((link) => (
              <Link key={link.to} to={link.to} className="text-sm text-muted hover:text-accent">
                {link.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="space-y-3">
          <p className="text-sm font-semibold text-foreground">About Me</p>
          <div className="flex gap-3">
            {SOCIAL_LINKS.map((social) => (
              <a
                key={social.label}
                href={social.href}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={social.label}
                title={social.label}
                className="glass-panel flex h-10 w-10 items-center justify-center rounded-full text-muted transition-all hover:scale-110 hover:text-accent hover:border-accent/40 active:scale-90"
              >
                <social.icon size={18} />
              </a>
            ))}
          </div>
        </div>
      </div>

      <div className="border-t border-glass-border px-6 py-5 text-center text-xs text-muted">
        © {year} MythicMinds. All rights reserved.
      </div>
    </footer>
  );
}
