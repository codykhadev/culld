import { thumbnailUrl } from "../api/client";
import type { PhotoResult } from "../types";
import { PhotoStatusBadges } from "./PhotoStatusBadges";

interface Props {
  photo: PhotoResult;
  kept: boolean;
  onToggleKeep: (photoId: string) => void;
  onOpen: (photoId: string) => void;
}

export function PhotoCard({ photo, kept, onToggleKeep, onOpen }: Props) {
  const failed = photo.status === "failed";

  return (
    <div
      className={`group relative overflow-hidden rounded-lg border bg-ink shadow-sm transition-all ${
        kept ? "border-cream/10" : "border-red-500/30"
      }`}
    >
      {photo.is_recommended_keeper && (
        <span className="absolute left-2 top-2 z-10 rounded-full bg-gold px-2 py-0.5 text-xs font-semibold text-ink shadow">
          Recommended
        </span>
      )}

      <div className={kept ? "" : "opacity-40"}>
        {failed ? (
          <div className="flex aspect-square w-full items-center justify-center bg-cream/5 p-2 text-center text-xs text-cream/30">
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
          <PhotoStatusBadges photo={photo} />
        </div>
      </div>

      <button
        type="button"
        onClick={() => onToggleKeep(photo.id)}
        className={`w-full border-t py-1.5 text-xs font-medium transition-colors ${
          kept
            ? "border-cream/10 text-cream/50 hover:bg-red-500/10 hover:text-red-400"
            : "border-red-500/20 bg-red-500/10 text-red-400 hover:bg-red-500/20"
        }`}
      >
        {kept ? "Remove" : "Removed — click to restore"}
      </button>
    </div>
  );
}
