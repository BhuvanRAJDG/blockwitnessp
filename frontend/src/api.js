// frontend/src/api.js
const API_BASE = "/api";

// Using local proxy - configured in vite.config.js

async function fetchJson(url, opts = {}) {
  const res = await fetch(url, opts);
  if (!res.ok) {
    const txt = await res.text().catch(()=>"(no body)");
    throw new Error(`Request failed ${res.status} ${res.statusText} -> ${txt}`);
  }
  return res;
}

// -----------------
// REPORTS
// -----------------
export async function createReport(formData) {
  const res = await fetchJson(`${API_BASE}/report`, { method: "POST", body: formData });
  return res.json();
}

export async function searchReports(query) {
  const res = await fetchJson(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
  return res.json();
}

export async function downloadCertificate(reportId) {
  const url = `${API_BASE}/report/${encodeURIComponent(reportId)}/certificate`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Certificate download failed");
  return res.blob();
}

// -----------------
// BLOCKCHAIN DATA
// -----------------
export async function explorer() {
  const res = await fetchJson(`${API_BASE}/explorer`);
  return res.json();
}

export async function getBlock(idx) {
  const res = await fetchJson(`${API_BASE}/block/${idx}`);
  return res.json();
}

export async function getBlockQr(idx) {
  const res = await fetchJson(`${API_BASE}/block/${idx}/qr`);
  return res.json();
}

export async function getMerkleProof(blockIdx, leaf) {
  const url = `${API_BASE}/block/${blockIdx}/merkle?leaf=${encodeURIComponent(leaf || "")}`;
  const res = await fetchJson(url);
  return res.json();
}

export async function verifyFile(formData) {
  const res = await fetchJson(`${API_BASE}/verify`, { method: "POST", body: formData });
  return res.json();
}

// -----------------
// CHAIN OPERATIONS
// -----------------
export async function getTimeline() {
  const res = await fetchJson(`${API_BASE}/chain/timeline`);
  return res.json();
}

export async function verifyChain() {
  const res = await fetchJson(`${API_BASE}/chain/verify`);
  return res.json();
}

// -----------------
// AUTH
// -----------------
export async function register(email, username, password) {
  const res = await fetchJson(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, username, password })
  });
  return res.json();
}

export async function login(email, password) {
  const res = await fetchJson(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  return res.json();
}

export async function logout() {
  const res = await fetchJson(`${API_BASE}/auth/logout`, { method: "POST" });
  return res.json();
}

export async function getCurrentUser() {
  const res = await fetch(`${API_BASE}/auth/me`);
  return res.json();
}

export async function getGoogleAuthUrl() {
  const res = await fetchJson(`${API_BASE}/auth/google`);
  return res.json();
}
