import type { PhotoResult } from "../types";
import { Badge } from "./Badge";

export function PhotoStatusBadges({ photo }: { photo: PhotoResult }) {
  if (photo.status === "failed") {
    return <Badge tone="bad">unreadable file</Badge>;
  }

  return (
    <>
      {photo.is_blurry ? <Badge tone="bad">blurry</Badge> : <Badge tone="good">sharp</Badge>}
      {photo.eyes_state === "open" ? (
        <Badge tone="good">eyes open</Badge>
      ) : photo.eyes_state === "closed" ? (
        <Badge tone="bad">eyes closed</Badge>
      ) : (
        <Badge tone="neutral">no face</Badge>
      )}
    </>
  );
}
