// frontend/src/pages/Explorer.jsx
import React, { useEffect, useState } from "react";
import { explorer, getBlock, getBlockQr } from "../api";
import { useLocation } from "react-router-dom";

export default function Explorer() {
  const [blocks, setBlocks] = useState([]);
  const [detail, setDetail] = useState(null);
  const [qrData, setQrData] = useState(null);
  const [qrLoading, setQrLoading] = useState(false);
  const location = useLocation();

  useEffect(()=>{ loadBlocks(); }, []);

  useEffect(()=>{
    const params = new URLSearchParams(location.search);
    const blockParam = params.get("block");
    if (blockParam) openBlock(Number(blockParam));
  }, [location.search]);

  async function loadBlocks(){
    try {
      const data = await explorer();
      setBlocks(data);
    } catch(err) {
      alert("Failed to load blocks: " + err.message);
    }
  }

  async function openBlock(idx){
    try {
      const d = await getBlock(idx);
      setDetail(d);
      setQrData(null);
    } catch(err) {
      alert("Failed to open block: " + err.message);
    }
  }

  async function showQr(idx){
    try {
      setQrLoading(true);
      const r = await getBlockQr(idx);
      setQrData(r);
    } catch(err){
      alert("Failed to fetch QR: " + err.message);
    } finally {
      setQrLoading(false);
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Block Explorer</h1>
      <div className="grid grid-cols-3 gap-4">
        <div>
          {blocks.map(b => (
            <div key={b.idx} className="p-3 bg-white rounded shadow mb-2">
              <div className="font-semibold">Block #{b.idx}</div>
              <div className="text-xs text-gray-600">Hash: {b.block_hash?.slice(0,12)}...</div>
              <div className="mt-2 flex gap-2">
                <button onClick={()=>openBlock(b.idx)} className="text-indigo-600 underline">View</button>
                <button onClick={()=>showQr(b.idx)} className="text-green-600 underline">Show QR</button>
              </div>
            </div>
          ))}
        </div>

        <div className="col-span-2">
          {detail ? (
            <div className="bg-white p-4 rounded shadow">
              <h2 className="font-bold">Block #{detail.idx}</h2>
              <div className="mt-2"><strong>Timestamp:</strong> {detail.timestamp}</div>
              <div><strong>Block Hash:</strong> {detail.block_hash}</div>
              <div><strong>Previous Hash:</strong> {detail.previous_hash}</div>
              <div><strong>Merkle Root:</strong> {detail.merkle_root}</div>

              <h3 className="mt-4 font-semibold">Transactions</h3>
              <pre className="text-sm bg-slate-50 p-2 rounded">{JSON.stringify(detail.transactions, null, 2)}</pre>

              <div className="mt-4">
                <h4 className="font-semibold">QR Verification</h4>
                <div className="mt-2">
                  {qrLoading && <div className="text-sm">Loading QR...</div>}
                  {qrData && (
                    <div className="p-3 bg-gray-50 rounded inline-block">
                      {qrData.qr_base64 ? <img alt="qr" src={`data:image/png;base64,${qrData.qr_base64}`} /> : <div className="text-sm">QR not available</div>}
                      <div className="text-xs text-gray-600 mt-2">
                        Or open: <a className="text-indigo-600" href={qrData.verification_url} target="_blank" rel="noreferrer">{qrData.verification_url}</a>
                      </div>
                    </div>
                  )}
                  {!qrLoading && !qrData && <div className="text-xs text-gray-500">Click "Show QR" on any block entry to view its verification QR.</div>}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-gray-600">Select a block to view details</div>
          )}
        </div>
      </div>
    </div>
  );
}
