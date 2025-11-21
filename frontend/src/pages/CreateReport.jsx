// frontend/src/pages/CreateReport.jsx
import React, { useState } from "react";
import { createReport } from "../api";

export default function CreateReport() {
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [uploader, setUploader] = useState("demo_user");
  const [files, setFiles] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  function onFiles(e) {
    setFiles(Array.from(e.target.files));
  }

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    const fd = new FormData();
    fd.append("title", title);
    fd.append("description", desc);
    fd.append("uploader", uploader);
    for (const f of files) fd.append("files", f);
    try {
      const r = await createReport(fd);
      setResult(r);
    } catch (err) {
      alert("Upload failed: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold mb-4">Create Incident Report</h1>
      <form onSubmit={submit} className="bg-white p-6 rounded shadow">
        <label className="block mb-2">Title
          <input className="w-full p-2 border mt-1" value={title} onChange={(e)=>setTitle(e.target.value)} />
        </label>
        <label className="block mb-2">Description
          <textarea className="w-full p-2 border mt-1" value={desc} onChange={(e)=>setDesc(e.target.value)} />
        </label>
        <label className="block mb-2">Uploader
          <input className="w-full p-2 border mt-1" value={uploader} onChange={(e)=>setUploader(e.target.value)} />
        </label>
        <label className="block mb-4">Evidence files
          <input type="file" multiple onChange={onFiles} className="w-full mt-1" />
        </label>
        <button className="px-4 py-2 bg-indigo-600 text-white rounded">
          {loading ? "Submitting..." : "Submit"}
        </button>
      </form>

      {result && (
        <div className="mt-6 bg-white p-4 rounded shadow">
          <h2 className="font-semibold">Report created</h2>
          <pre className="text-sm">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
