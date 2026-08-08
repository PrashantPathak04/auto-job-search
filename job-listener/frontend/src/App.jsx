import React, { useEffect, useState } from 'react'

export default function App() {
  const [jobs, setJobs] = useState([])
  const [selectedJobIds, setSelectedJobIds] = useState(new Set())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [applyResult, setApplyResult] = useState(null)

  const [userDetails, setUserDetails] = useState({ fullName: '', email: '', phone: '', resumeUrl: '', coverLetter: '' })

  const handleApplySelected = async () => {
    setSubmitting(true)
    setApplyResult(null)
    const selectedJobs = jobs.filter((job, index) => selectedJobIds.has(index))
    const payload = { jobs: selectedJobs, userDetails }
    try {
      const res = await fetch('http://localhost:4000/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(`HTTP ${res.status}: ${text}`)
      }
      const body = await res.json()
      setApplyResult({ success: true, response: body })
    } catch (err) {
      setApplyResult({ success: false, error: err.message, payload })
    } finally {
      setSubmitting(false)
    }
  }

  useEffect(() => {
    const fetchJobs = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await fetch('http://localhost:4000/jobs')
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const body = await res.json()
        setJobs(body.jobs || [])
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchJobs()
  }, [])

  return (
    <div className="app">
      <header className="header">
        <h1>Job Listener — Dashboard</h1>
      </header>

      <main className="container">
        <section className="panel">
          <h2>Jobs</h2>

          <div style={{ marginBottom: 12 }}>
            <button disabled={submitting || selectedJobIds.size === 0} onClick={handleApplySelected} style={{ padding: '8px 12px', marginRight: 8 }}>
              {submitting ? 'Applying selected jobs...' : 'Apply Selected Jobs'}
            </button>
            {!jobs.length && <span style={{ marginLeft: 12, color: '#666' }}>Load jobs first to apply.</span>}
            {jobs.length > 0 && selectedJobIds.size === 0 && <span style={{ marginLeft: 12, color: '#666' }}>Select jobs to apply.</span>}
          </div>

          {/* <div style={{ marginBottom: 12, padding: 12, background: '#fbfcff', border: '1px solid #eef', borderRadius: 6 }}>
            
            {applyResult && (
              <div style={{ marginTop: 12 }}>
                {applyResult.success ? <pre style={{ background: '#f3fff3', padding: 8 }}>{JSON.stringify(applyResult.response, null, 2)}</pre> : <>
                  <div style={{ color: 'crimson' }}>Error: {applyResult.error}</div>
                  <div style={{ marginTop: 8 }}>
                    <div>Prepared payload (copy or inspect):</div>
                    <pre style={{ background: '#fff7f3', padding: 8 }}>{JSON.stringify(applyResult.payload, null, 2)}</pre>
                  </div>
                </>}</div>
            )}
          </div> */}

          {loading && <p>Loading jobs...</p>}
          {error && <p style={{ color: 'crimson' }}>Error: {error}</p>}

          {!loading && !error && (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {jobs.map((job, i) => (
                <li key={i} style={{ display: 'flex', alignItems: 'flex-start', padding: '12px 0', borderBottom: '1px solid #eee' }}>
                  <label style={{ display: 'flex', alignItems: 'center', marginRight: 12 }}>
                    <input
                      type="checkbox"
                      checked={selectedJobIds.has(i)}
                      onChange={(event) => {
                        const next = new Set(selectedJobIds)
                        if (event.target.checked) next.add(i)
                        else next.delete(i)
                        setSelectedJobIds(next)
                      }}
                      style={{ marginRight: 8 }}
                    />
                  </label>
                  <div>
                    <a href={job.url} target="_blank" rel="noreferrer" style={{ color: 'var(--accent)', fontWeight: 600 }}>
                      {job.title || '—'}
                    </a>
                    <div style={{ fontSize: 13, color: '#444' }}>{job.company || 'Unknown company'} — {job.location || 'Unknown location'}</div>
                  </div>
                </li>
              ))}
              {jobs.length === 0 && <li>No jobs found.</li>}
            </ul>
          )}

        </section>

        <section className="panel">
          <h2>Resume</h2>
          <p>Upload and optimization status will appear here.</p>
        </section>
      </main>
    </div>
  )
}
