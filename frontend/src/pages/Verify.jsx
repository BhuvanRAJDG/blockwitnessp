import React, {useState} from 'react'
import { verifyFile } from '../api'

export default function Verify(){
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)

  async function submit(e){
    e.preventDefault()
    if (!file) return
    const fd = new FormData()
    fd.append("file", file)
    const r = await verifyFile(fd)
    setResult(r)
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Verify Evidence</h1>
      <form onSubmit={submit} className="bg-white p-4 rounded shadow">
        <input type="file" onChange={e=>setFile(e.target.files[0])}/>
        <button className="px-3 py-2 bg-green-600 text-white rounded ml-3">
          Verify
        </button>
      </form>
      {result && (
        <div className="bg-white p-4 rounded shadow mt-4">
          <h3 className="font-semibold">Result</h3>
          <pre className="text-sm">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
