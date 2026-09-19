import { useRef, useState } from "react";
import type { DragEvent } from "react";

interface Props {
  onFilesSelected: (files: File[]) => void;
  disabled?: boolean;
}

export function UploadDropzone({ onFilesSelected, disabled }: Props) {
  const [isDraggingOver, setIsDraggingOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDraggingOver(false);
    if (disabled) return;
    const files = Array.from(event.dataTransfer.files).filter((f) => f.type.startsWith("image/"));
    if (files.length > 0) onFilesSelected(files);
  };

  return (
    <div
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setIsDraggingOver(true);
      }}
      onDragLeave={() => setIsDraggingOver(false)}
      onDrop={handleDrop}
      className={`relative mx-auto flex w-full max-w-xl cursor-pointer flex-col items-center justify-center overflow-hidden rounded-lg border-2 border-solid bg-ink p-10 text-center transition-colors ${
        disabled
          ? "cursor-not-allowed border-cream/10 text-cream/30"
          : isDraggingOver
            ? "border-gold text-gold"
            : "diagonal-fill text-cream/60"
      }`}
    >
      <p className="text-[24px] font-medium text-cream">
        {disabled ? "Analyzing photos…" : "Drag photos here or click to select"}
      </p>
      <p className="mt-1 text-[18px] text-cream/80">JPG or PNG</p>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        multiple
        hidden
        disabled={disabled}
        onChange={(e) => {
          const files = Array.from(e.target.files ?? []);
          if (files.length > 0) onFilesSelected(files);
          e.target.value = ""; // allow re-selecting the same file(s) later
        }}
      />
    </div>
  );
}
