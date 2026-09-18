import { useState } from "react";
import { createSession, uploadPhotos } from "./api/client";
import { PhotoGrid } from "./components/PhotoGrid";
import { PhotoLightbox } from "./components/PhotoLightbox";
import { UploadDropzone } from "./components/UploadDropzone";
import type { PhotoResult } from "./types";

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [photos, setPhotos] = useState<PhotoResult[]>([]);
  const [keptIds, setKeptIds] = useState<Set<string>>(new Set());
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const handleFilesSelected = async (files: File[]) => {
    setIsUploading(true);
    setError(null);
    try {
      const currentSessionId = sessionId ?? (await createSession()).session_id;
      if (!sessionId) setSessionId(currentSessionId);

      const updatedPhotos = await uploadPhotos(currentSessionId, files);
      setPhotos(updatedPhotos);
      setKeptIds((prev) => {
        const next = new Set(prev);
        for (const photo of updatedPhotos) {
          if (!next.has(photo.id)) next.add(photo.id); // default: everything kept
        }
        return next;
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong uploading your photos.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleToggleKeep = (photoId: string) => {
    setKeptIds((prev) => {
      const next = new Set(prev);
      if (next.has(photoId)) next.delete(photoId);
      else next.add(photoId);
      return next;
    });
  };

  const keptCount = photos.filter((p) => keptIds.has(p.id)).length;

  const handleOpen = (photoId: string) => {
    const index = photos.findIndex((p) => p.id === photoId);
    if (index !== -1) setOpenIndex(index);
  };

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-neutral-900">Photo Culling Assistant</h1>
        <p className="text-sm text-neutral-500">
          Upload a batch of photos — blurry shots, closed eyes, and near-duplicate bursts get flagged automatically.
        </p>
      </header>

      <UploadDropzone onFilesSelected={handleFilesSelected} disabled={isUploading} />

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      {photos.length > 0 && (
        <>
          <div className="my-4 flex items-center justify-between text-sm text-neutral-500">
            <span>
              {photos.length} photo{photos.length === 1 ? "" : "s"} · {keptCount} kept
            </span>
          </div>
          <PhotoGrid photos={photos} keptIds={keptIds} onToggleKeep={handleToggleKeep} onOpen={handleOpen} />
        </>
      )}

      {openIndex !== null && (
        <PhotoLightbox
          photos={photos}
          selectedIndex={openIndex}
          onClose={() => setOpenIndex(null)}
          onNavigate={setOpenIndex}
        />
      )}
    </main>
  );
}

export default App;
