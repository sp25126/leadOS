const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function buildHeaders(keys: Partial<Record<string, string>> = {}): Record<string, string> {
  const h: Record<string, string> = {
    "Content-Type": "application/json",
    "X-API-Key": keys.apiKey || "saumyavishwam@gmail",
  };
  if (keys.geminiKey)     h["X-Gemini-Key"]      = keys.geminiKey;
  if (keys.groqKey)       h["X-Groq-Key"]        = keys.groqKey;
  if (keys.googleMapsKey) h["X-Google-Maps-Key"] = keys.googleMapsKey;
  if (keys.hunterKey)     h["X-Hunter-Key"]       = keys.hunterKey;
  return h;
}

async function handle(res: Response) {
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try { const j = await res.json(); msg = j.detail || j.message || msg; } catch {}
    throw new Error(msg);
  }
  return res.json();
}

export const api = {
  get:    (path: string, keys = {}) =>
    fetch(`${BASE}${path}`, { headers: buildHeaders(keys), cache: "no-store" }).then(handle),

  post:   (path: string, body: unknown, keys = {}) =>
    fetch(`${BASE}${path}`, {
      method: "POST", headers: buildHeaders(keys), body: JSON.stringify(body),
    }).then(handle),

  delete: (path: string, keys = {}) =>
    fetch(`${BASE}${path}`, { method: "DELETE", headers: buildHeaders(keys) }).then(handle),
};

// SWR fetcher factory
export const swrFetcher = (keys: Record<string, string>) =>
  (url: string) => api.get(url, keys);

// Compatibility aliases if needed
export const apiGet = api.get;
export const apiPost = api.post;
export const apiDelete = api.delete;
