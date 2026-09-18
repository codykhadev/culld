import type { ReactNode } from "react";

interface Props {
  tone: "good" | "bad" | "neutral";
  children: ReactNode;
}

export function Badge({ tone, children }: Props) {
  const toneClasses = {
    good: "bg-green-100 text-green-700",
    bad: "bg-red-100 text-red-700",
    neutral: "bg-neutral-100 text-neutral-600",
  }[tone];
  return <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${toneClasses}`}>{children}</span>;
}
