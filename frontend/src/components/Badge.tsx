import type { ReactNode } from "react";

interface Props {
  tone: "good" | "bad" | "neutral";
  children: ReactNode;
}

export function Badge({ tone, children }: Props) {
  const toneClasses = {
    good: "bg-green-500/15 text-green-400",
    bad: "bg-red-500/15 text-red-400",
    neutral: "bg-cream/10 text-cream/60",
  }[tone];
  return <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${toneClasses}`}>{children}</span>;
}
