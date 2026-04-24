import type { ChatResponse, PredictResponse } from "@/types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, body: { message: string }): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(payload?.detail ?? "The request failed. Please try again.");
  }

  return (await response.json()) as T;
}

export async function chat(message: string): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", { message });
}

export async function predict(message: string): Promise<PredictResponse> {
  return request<PredictResponse>("/api/predict", { message });
}
