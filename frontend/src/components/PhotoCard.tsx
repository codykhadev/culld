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
        <PhotoStatusBadges photo={photo} />
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
        {kept ? "Remove" : "Removed — click to restore"}
      </button>
    </div>
  );
}
