export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function fetchApi(endpoint: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...(options.headers as Record<string, string>),
  };

  if (options.body instanceof FormData) {
    // Let browser set Content-Type for FormData (multipart/form-data with boundary)
    delete headers["Content-Type"];
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401 && endpoint !== "/auth/login") {
      if (typeof window !== "undefined") {
        localStorage.removeItem("token");
        window.location.href = "/login";
      }
    }
    const errorData = await response.json().catch(() => ({}));
    // Handle both string detail and object detail (FastAPI structured errors)
    const detail = errorData.detail;
    let message = "An error occurred. Please try again.";
    if (typeof detail === "string") {
      message = detail;
    } else if (detail && typeof detail === "object" && detail.message) {
      message = detail.message;
    } else if (errorData.message) {
      message = errorData.message;
    }
    const err: any = new Error(message);
    err.detail = detail;
    err.status = response.status;
    throw err;
  }

  return response.json();
}
