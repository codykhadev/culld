import { useState } from "react";
import { createSession, exportKeptPhotos, uploadPhotos } from "./api/client";
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
  const [isDownloading, setIsDownloading] = useState(false);

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

  const handleDownloadKept = async () => {
    if (!sessionId) return;
    const keptPhotoIds = photos.filter((p) => keptIds.has(p.id)).map((p) => p.id);
    if (keptPhotoIds.length === 0) return;

    setIsDownloading(true);
    setError(null);
    try {
      const blob = await exportKeptPhotos(sessionId, keptPhotoIds);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "kept_photos.zip";
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong downloading your photos.");
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <main className="relative mx-auto min-h-screen max-w-6xl px-4 py-8">
      <header className="mb-6">
        <h1 className="font-display text-[64px] font-semibold text-cream">Culld</h1>
        <p className="text-base text-cream/80">
          Upload photos. The blurry shots, closed eyes, and near-duplicate photos will get flagged automatically.
        </p>
      </header>

      {photos.length === 0 ? (
        <div className="absolute inset-0 flex items-center justify-center px-4">
          <UploadDropzone onFilesSelected={handleFilesSelected} disabled={isUploading} />
        </div>
      ) : (
        <UploadDropzone onFilesSelected={handleFilesSelected} disabled={isUploading} />
      )}

      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}

      {photos.length > 0 && (
        <>
          <div className="my-4 flex items-center justify-between text-sm text-cream/60">
            <span>
              {photos.length} photo{photos.length === 1 ? "" : "s"} · {keptCount} kept
            </span>
            <button
              type="button"
              onClick={handleDownloadKept}
              disabled={isDownloading || keptCount === 0}
              className="rounded-md bg-gold px-3 py-1.5 text-xs font-medium text-ink transition-colors duration-300 ease-in-out hover:bg-[#e6a600] disabled:cursor-not-allowed disabled:bg-neutral-700 disabled:text-neutral-400"
            >
              {isDownloading ? "Preparing…" : `Download ${keptCount} kept photo${keptCount === 1 ? "" : "s"}`}
            </button>
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
