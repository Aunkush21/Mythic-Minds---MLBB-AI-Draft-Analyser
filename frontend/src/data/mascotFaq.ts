export interface MascotFaqItem {
  id: string;
  question: string;
  answer: string;
}

export const MASCOT_FAQ: MascotFaqItem[] = [
  {
    id: "motive",
    question: "What's the motive behind this project?",
    answer:
      "Admin wanted one glass-paneled command center for drafting, theorycrafting, and hero comparisons — instead of alt-tabbing between five different wikis.",
  },
  {
    id: "engineering-vs-mlbb",
    question: "Does admin love engineering or playing MLBB more?",
    answer:
      "Tough one. Admin codes by day and queues ranked by night — but shipping a clean feature feels a lot like landing a penta, so engineering edges it out.",
  },
  {
    id: "married",
    question: "Is the admin married?",
    answer: "Nope, still single — currently in a very committed relationship with this codebase.",
  },
  {
    id: "favorite-role",
    question: "What's admin's favorite role?",
    answer: "Mid lane mage. Admin likes blowing things up from a safe distance — in lane and in life.",
  },
  {
    id: "favorite-hero",
    question: "What's admin's favorite hero?",
    answer: "Ask three times, get three different answers — but Yve and Lunox show up a lot.",
  },
  {
    id: "why-not-wiki",
    question: "Why not just use the Mobile Legends wiki?",
    answer: "Wikis are great for facts, not for decisions. This site is built for drafting and reacting in real time.",
  },
  {
    id: "tech-stack",
    question: "What tech powers this site?",
    answer: "React + TypeScript up front, Python crunching hero data in the back, wrapped in a very caffeinated glassmorphism theme.",
  },
  {
    id: "future-updates",
    question: "Will more features be added?",
    answer: "Constantly. Admin treats this project like a live-service game — new patches keep dropping.",
  },
  {
    id: "are-you-a-hero",
    question: "Are you an actual MLBB hero?",
    answer: "Not officially — I'm more of a fan-made recruit who's still hoping for a skin line someday.",
  },
  {
    id: "admin-rank",
    question: "What rank is admin?",
    answer: "High enough to have strong opinions, low enough to still rage about jungle steals.",
  },
];
