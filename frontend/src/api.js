// frontend/src/api.js
const API_BASE = "http://127.0.0.1:5001/api";

async function fetchJson(url, opts = {}) {
  const res = await fetch(url, opts);
  // better error messages for debugging
  if (!res.ok) {
    const txt = await res.text().catch(()=>"(no body)");
    throw new Error(`Request failed ${res.status} ${res.statusText} -> ${txt}`);
  }
  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    const txt = await res.text().catch(()=>"(no body)");
    throw new Error(`Expected JSON but got: ${txt}`);
  }
  return res.json();
}

export async function createReport(formData) {
  return fetchJson(`${API_BASE}/report`, { method: "POST", body: formData });
}

export async function explorer() {
  return fetchJson(`${API_BASE}/explorer`);
}

export async function getBlock(idx) {
  return fetchJson(`${API_BASE}/block/${idx}`);
}

export async function verifyFile(formData) {
  return fetchJson(`${API_BASE}/verify`, { method: "POST", body: formData });
}

export async function getBlockQr(idx) {
  return fetchJson(`${API_BASE}/block/${idx}/qr`);
}

export async function searchReports(query) {
  return fetchJson(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
}
