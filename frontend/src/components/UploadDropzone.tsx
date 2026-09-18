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
      className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-10 text-center transition-colors ${
        disabled
          ? "cursor-not-allowed border-neutral-200 bg-neutral-50 text-neutral-400"
          : isDraggingOver
            ? "border-blue-400 bg-blue-50 text-blue-600"
            : "border-neutral-300 text-neutral-500 hover:border-neutral-400"
      }`}
    >
      <p className="text-sm font-medium">
        {disabled ? "Analyzing photos…" : "Drag photos here, or click to select"}
      </p>
      <p className="mt-1 text-xs text-neutral-400">JPG or PNG, any batch size</p>
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
