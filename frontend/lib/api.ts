import type { ChatResponse } from "@/types/api";

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
    const errorData = (await response.json().catch(() => null)) as { 
      error?: { message: string }; 
      detail?: string | { error?: { message: string } } 
    } | null;
    
    // Support both standard FastAPI detail and our custom structured error
    let message = "The request failed. Please try again.";
    if (errorData?.error?.message) {
      message = errorData.error.message;
    } else if (typeof errorData?.detail === "string") {
      message = errorData.detail;
    } else if (typeof errorData?.detail === "object" && errorData?.detail?.error?.message) {
       message = errorData.detail.error.message;
    }

    throw new Error(message);
  }

  return (await response.json()) as T;
}

export async function chat(message: string): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", { message });
}
