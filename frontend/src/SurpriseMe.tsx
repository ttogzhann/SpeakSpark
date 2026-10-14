import { useEffect, useRef, useState } from 'react'
import type { Activity } from './activity'
import ActivityContent from './ActivityContent'

type RandomResult = { status: 'selected'; activity: Activity } | { status: 'exhausted' | 'no_matches'; activity: null }
type SelectionState = { status: 'idle' | 'loading' | 'error' } | RandomResult

export default function SurpriseMe() {
  const [level, setLevel] = useState('')
  const [type, setType] = useState('')
  const [state, setState] = useState<SelectionState>({ status: 'idle' })
  const [pending, setPending] = useState(false)
  const busy = useRef(false)
  const revision = useRef(0)
  const mounted = useRef(true)
  useEffect(() => {
    mounted.current = true
    return () => { mounted.current = false; ++revision.current }
  }, [])

  function changeFilter(key: 'level' | 'type', value: string) {
    ++revision.current
    if (key === 'level') setLevel(value)
    else setType(value)
    setState({ status: 'idle' })
  }
  async function select() {
    if (!['A1', 'A2', 'B1', 'B2'].includes(level) || busy.current) return
    busy.current = true
    setPending(true)
    const request = ++revision.current
    setState({ status: 'loading' })
    const parameters = new URLSearchParams({ level })
    if (type) parameters.set('type', type)
    try {
      const response = await fetch(`/api/random-activities/next?${parameters}`, { method: 'POST' })
      if (!response.ok) throw new Error('Selection failed')
      const result: RandomResult = await response.json()
      if (mounted.current && revision.current === request) setState(result)
    } catch {
      if (mounted.current && revision.current === request) setState({ status: 'error' })
    } finally {
      busy.current = false
      if (mounted.current) setPending(false)
    }
  }
  const controlClass = 'mt-2 block min-h-12 w-full min-w-0 rounded-lg border border-slate-300 bg-white px-3 font-normal focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-700'
  return (
    <section className="mt-8">
      <div className="grid gap-4 sm:grid-cols-3">
        <label className="min-w-0 font-semibold">Level (required)<select value={level} onChange={(event) => changeFilter('level', event.target.value)} className={controlClass}><option value="">Choose level</option>{['A1', 'A2', 'B1', 'B2'].map((value) => <option key={value}>{value}</option>)}</select></label>
        <label className="min-w-0 font-semibold">Activity type (optional)<select value={type} onChange={(event) => changeFilter('type', event.target.value)} className={controlClass}><option value="">All types</option>{['Conversation Cards', 'Role-play Scenarios', 'Speaking Challenges'].map((value) => <option key={value}>{value}</option>)}</select></label>
        <button type="button" disabled={!level || pending} onClick={select} className="min-h-12 self-end rounded-lg bg-indigo-700 px-4 py-3 font-semibold text-white disabled:opacity-60 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-700">{pending ? 'Selecting activity...' : state.status === 'selected' ? 'Next' : state.status === 'exhausted' ? 'Restart cycle' : 'Surprise Me'}</button>
      </div>
      {state.status === 'idle' && <p role="status" className="mt-6">Choose a level and select Surprise Me to begin a new selection.</p>}
      {(state.status === 'loading' || (pending && state.status === 'idle')) && <p role="status" className="mt-6">Selecting activity. Please wait before starting another request.</p>}
      {state.status === 'error' && <p role="alert" className="mt-6">We couldn't confirm the selection. Check the local backend, then try again. A request that reached the backend may have advanced the cycle.</p>}
      {state.status === 'no_matches' && <p role="status" className="mt-6">No activities match these filters. Try another level or activity type.</p>}
      {state.status === 'exhausted' && <p role="status" className="mt-6">You've seen every matching activity. Restart the cycle when you're ready.</p>}
      {state.status === 'selected' && <ActivityContent activity={state.activity} />}
    </section>
  )
}
