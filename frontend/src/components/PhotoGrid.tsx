import type { PhotoResult } from "../types";
import { DuplicateGroup } from "./DuplicateGroup";
import { PhotoCard } from "./PhotoCard";

interface Props {
  photos: PhotoResult[];
  keptIds: Set<string>;
  onToggleKeep: (photoId: string) => void;
  onOpen: (photoId: string) => void;
}

export function PhotoGrid({ photos, keptIds, onToggleKeep, onOpen }: Props) {
  const grouped = new Map<string, PhotoResult[]>();
  const standalone: PhotoResult[] = [];

  for (const photo of photos) {
    if (photo.group_id) {
      const existing = grouped.get(photo.group_id) ?? [];
      existing.push(photo);
      grouped.set(photo.group_id, existing);
    } else {
      standalone.push(photo);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      {[...grouped.values()].map((groupPhotos) => (
        <DuplicateGroup
          key={groupPhotos[0].group_id}
          photos={groupPhotos}
          keptIds={keptIds}
          onToggleKeep={onToggleKeep}
          onOpen={onOpen}
        />
      ))}

      {standalone.length > 0 && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {standalone.map((photo) => (
            <PhotoCard
              key={photo.id}
              photo={photo}
              kept={keptIds.has(photo.id)}
              onToggleKeep={onToggleKeep}
              onOpen={onOpen}
            />
          ))}
        </div>
      )}
    </div>
  );
}
