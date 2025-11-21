import React, {useEffect, useState} from 'react'
import { explorer, getBlock } from '../api'

export default function Explorer(){
  const [blocks,setBlocks] = useState([])
  const [detail, setDetail] = useState(null)

  useEffect(()=>{ load() },[])
  async function load(){
    const data = await explorer()
    setBlocks(data)
  }
  async function open(idx){
    const d = await getBlock(idx)
    setDetail(d)
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Block Explorer</h1>
      <div className="grid grid-cols-3 gap-4">
        <div>
          {blocks.map(b => (
            <div key={b.idx} className="p-3 bg-white rounded shadow mb-2">
              <div className="font-semibold">Block #{b.idx}</div>
              <div className="text-xs">Hash: {b.block_hash.slice(0,12)}</div>
              <button className="text-indigo-600 mt-2" onClick={()=>open(b.idx)}>
                Open
              </button>
            </div>
          ))}
        </div>

        <div className="col-span-2">
          {detail ? (
            <div className="bg-white p-4 rounded shadow">
              <h2 className="font-semibold">Block #{detail.idx}</h2>
              <div><strong>Timestamp:</strong> {detail.timestamp}</div>
              <div><strong>Block Hash:</strong> {detail.block_hash}</div>
              <div><strong>Merkle Root:</strong> {detail.merkle_root}</div>
              <h3 className="mt-4 font-semibold">Transactions</h3>
              <pre>{JSON.stringify(detail.transactions, null, 2)}</pre>
            </div>
          ) : (
            <div className="text-gray-600">Select a block</div>
          )}
        </div>
      </div>
    </div>
  )
}
