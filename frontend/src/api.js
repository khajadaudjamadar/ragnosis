const TOKEN_KEY = "ragnosis_token";
const USER_KEY = "ragnosis_user";

export const auth = {
  token: () => localStorage.getItem(TOKEN_KEY),
  user: () => JSON.parse(localStorage.getItem(USER_KEY) || "null"),
  save(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
};

async function request(path, { method = "GET", body, form } = {}) {
  const headers = {};
  if (auth.token()) headers.Authorization = `Bearer ${auth.token()}`;
  if (body) headers["Content-Type"] = "application/json";
  const res = await fetch(`/api${path}`, {
    method,
    headers,
    body: form || (body ? JSON.stringify(body) : undefined),
  });
  const data = await res.json().catch(() => ({}));
  if (res.status === 401 && auth.token()) {
    auth.clear();
    window.location.href = "/login";
  }
  if (!res.ok) throw new Error(data.error || data.msg || `Request failed (${res.status})`);
  return data;
}

export const api = {
  login: (email, password) => request("/auth/login", { method: "POST", body: { email, password } }),
  register: (payload) => request("/auth/register", { method: "POST", body: payload }),
  listReports: () => request("/reports"),
  getReport: (id) => request(`/reports/${id}`),
  uploadReport: (form) => request("/reports", { method: "POST", form }),
  deleteReport: (id) => request(`/reports/${id}`, { method: "DELETE" }),
  ask: (id, question) => request(`/reports/${id}/ask`, { method: "POST", body: { question } }),
  history: (id) => request(`/reports/${id}/history`),
};
