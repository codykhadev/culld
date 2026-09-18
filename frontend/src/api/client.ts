import type { PhotoResult, SessionCreateResult, SessionResultsResponse } from "../types";

const API_BASE_URL = "http://localhost:8000";

export async function checkHealth(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.status}`);
  }
  return res.json();
}

export async function createSession(): Promise<SessionCreateResult> {
  const res = await fetch(`${API_BASE_URL}/sessions`, { method: "POST" });
  if (!res.ok) {
    throw new Error(`Failed to create session: ${res.status}`);
  }
  return res.json();
}

export async function uploadPhotos(sessionId: string, files: File[]): Promise<PhotoResult[]> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }

  const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/photos`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    throw new Error(`Failed to upload photos: ${res.status}`);
  }
  return res.json();
}

export async function getResults(sessionId: string): Promise<SessionResultsResponse> {
  const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/results`);
  if (!res.ok) {
    throw new Error(`Failed to fetch results: ${res.status}`);
  }
  return res.json();
}

export function thumbnailUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

export async function exportKeptPhotos(sessionId: string, photoIds: string[]): Promise<Blob> {
  const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ photo_ids: photoIds }),
  });
  if (!res.ok) {
    throw new Error(`Failed to export photos: ${res.status}`);
  }
  return res.blob();
}
