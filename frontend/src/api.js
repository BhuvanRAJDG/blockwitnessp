const API_BASE = "http://127.0.0.1:5001/api";

export async function createReport(formData) {
  const res = await fetch(`${API_BASE}/report`, {
    method: "POST",
    body: formData
  });
  return res.json();
}

export async function explorer() {
  const res = await fetch(`${API_BASE}/explorer`);
  return res.json();
}

export async function getBlock(idx) {
  const res = await fetch(`${API_BASE}/block/${idx}`);
  return res.json();
}

export async function verifyFile(formData) {
  const res = await fetch(`${API_BASE}/verify`, {
    method: "POST",
    body: formData
  });
  return res.json();
}
