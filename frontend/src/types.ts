export type EyesState = "open" | "closed" | "no_face_detected";
export type PhotoStatus = "pending" | "analyzed" | "failed";

export interface PhotoResult {
  id: string;
  filename: string;
  status: PhotoStatus;
  thumbnail_url: string;
  original_url: string;
  blur_score: number | null;
  is_blurry: boolean | null;
  eyes_state: EyesState | null;
  group_id: string | null;
  is_recommended_keeper: boolean | null;
}

export interface SessionCreateResult {
  session_id: string;
}

export interface SessionResultsResponse {
  session_id: string;
  photos: PhotoResult[];
}
