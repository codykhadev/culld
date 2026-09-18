import type { ReactNode } from "react";
import { thumbnailUrl } from "../api/client";
import type { PhotoResult } from "../types";

interface Props {
  photo: PhotoResult;
  kept: boolean;
  onToggleKeep: (photoId: string) => void;
  onOpen: (photoId: string) => void;
}

function Badge({ tone, children }: { tone: "good" | "bad" | "neutral"; children: ReactNode }) {
  const toneClasses = {
    good: "bg-green-100 text-green-700",
    bad: "bg-red-100 text-red-700",
    neutral: "bg-neutral-100 text-neutral-600",
  }[tone];
  return <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${toneClasses}`}>{children}</span>;
}

export function PhotoCard({ photo, kept, onToggleKeep, onOpen }: Props) {
  const failed = photo.status === "failed";

  const eyesBadge =
    photo.eyes_state === "open" ? (
      <Badge tone="good">eyes open</Badge>
    ) : photo.eyes_state === "closed" ? (
      <Badge tone="bad">eyes closed</Badge>
    ) : (
      <Badge tone="neutral">no face</Badge>
    );

  return (
    <div
      className={`group relative overflow-hidden rounded-lg border bg-white shadow-sm transition-all ${
        kept ? "border-neutral-200" : "border-red-200 opacity-50"
      }`}
    >
      {photo.is_recommended_keeper && (
        <span className="absolute left-2 top-2 z-10 rounded-full bg-blue-600 px-2 py-0.5 text-xs font-semibold text-white shadow">
          Recommended
        </span>
      )}

      {failed ? (
        <div className="flex aspect-square w-full items-center justify-center bg-neutral-100 p-2 text-center text-xs text-neutral-400">
          Couldn't read this file
        </div>
      ) : (
        <img
          src={thumbnailUrl(photo.thumbnail_url)}
          alt={photo.filename}
          onClick={() => onOpen(photo.id)}
          className="aspect-square w-full cursor-pointer object-cover"
        />
      )}

      <div className="flex flex-wrap items-center gap-1 p-2">
        {failed ? (
          <Badge tone="bad">unreadable file</Badge>
        ) : (
          <>
            {photo.is_blurry ? <Badge tone="bad">blurry</Badge> : <Badge tone="good">sharp</Badge>}
            {eyesBadge}
          </>
        )}
      </div>

      <button
        type="button"
        onClick={() => onToggleKeep(photo.id)}
        className={`w-full border-t py-1.5 text-xs font-medium transition-colors ${
          kept
            ? "border-neutral-100 text-neutral-500 hover:bg-red-50 hover:text-red-600"
            : "border-red-100 bg-red-50 text-red-600 hover:bg-red-100"
        }`}
      >
        {kept ? "Keep" : "Rejected — click to restore"}
      </button>
    </div>
  );
}
