import type { PhotoResult } from "../types";
import { PhotoCard } from "./PhotoCard";

interface Props {
  photos: PhotoResult[];
  keptIds: Set<string>;
  onToggleKeep: (photoId: string) => void;
  onOpen: (photoId: string) => void;
}

export function DuplicateGroup({ photos, keptIds, onToggleKeep, onOpen }: Props) {
  return (
    <div className="rounded-xl border border-dashed border-cream/20 bg-cream/5 p-3">
      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-cream/50">
        Burst group · {photos.length} similar shots
      </p>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
        {photos.map((photo) => (
          <PhotoCard
            key={photo.id}
            photo={photo}
            kept={keptIds.has(photo.id)}
            onToggleKeep={onToggleKeep}
            onOpen={onOpen}
          />
        ))}
      </div>
    </div>
  );
}
