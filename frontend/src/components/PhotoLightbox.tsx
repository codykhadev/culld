import { useEffect } from "react";
import { thumbnailUrl } from "../api/client";
import type { PhotoResult } from "../types";

interface Props {
  photos: PhotoResult[];
  selectedIndex: number;
  onClose: () => void;
  onNavigate: (index: number) => void;
}

export function PhotoLightbox({ photos, selectedIndex, onClose, onNavigate }: Props) {
  const photo = photos[selectedIndex];

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      } else if (event.key === "ArrowRight") {
        onNavigate((selectedIndex + 1) % photos.length);
      } else if (event.key === "ArrowLeft") {
        onNavigate((selectedIndex - 1 + photos.length) % photos.length);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedIndex, photos.length, onClose, onNavigate]);

  if (!photo) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/90 p-4"
      onClick={onClose}
    >
      <button
        type="button"
        onClick={onClose}
        className="absolute right-4 top-4 text-3xl leading-none text-white/80 hover:text-white"
        aria-label="Close"
      >
        ×
      </button>

      <button
        type="button"
        onClick={(event) => {
          event.stopPropagation();
          onNavigate((selectedIndex - 1 + photos.length) % photos.length);
        }}
        className="absolute left-2 top-1/2 -translate-y-1/2 px-3 py-6 text-4xl text-white/70 hover:text-white sm:left-4"
        aria-label="Previous photo"
      >
        ‹
      </button>
      <button
        type="button"
        onClick={(event) => {
          event.stopPropagation();
          onNavigate((selectedIndex + 1) % photos.length);
        }}
        className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-6 text-4xl text-white/70 hover:text-white sm:right-4"
        aria-label="Next photo"
      >
        ›
      </button>

      <img
        src={thumbnailUrl(photo.original_url)}
        alt={photo.filename}
        onClick={(event) => event.stopPropagation()}
        className="max-h-[85vh] max-w-[90vw] rounded-lg object-contain shadow-2xl"
      />

      <div className="mt-3 text-sm text-white/80" onClick={(event) => event.stopPropagation()}>
        {photo.filename} · {selectedIndex + 1} / {photos.length}
      </div>
    </div>
  );
}
