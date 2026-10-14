import { useEffect, useRef, useState } from 'react'
import type { Activity } from './activity'
import ActivityCard from './ActivityCard'
import ActivityForm from './ActivityForm'

export default function MyActivities() {
  const [activities, setActivities] = useState<Activity[]>([])
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading')
  const revision = useRef(0)
  const mounted = useRef(true)
  function load() {
    const current = ++revision.current
    setStatus('loading')
    fetch('/api/activities').then(async (response) => {
      if (!response.ok) throw new Error('List failed')
      const records: Activity[] = await response.json()
      if (mounted.current && revision.current === current) {
        setActivities(records.filter((activity) => !activity.is_builtin))
        setStatus('ready')
      }
    }).catch(() => { if (mounted.current && revision.current === current) setStatus('error') })
  }
  useEffect(() => {
    mounted.current = true
    load()
    return () => { mounted.current = false; ++revision.current }
  }, [])
  function created(activity: Activity) {
    ++revision.current
    setActivities((current) => [...current.filter((item) => item.id !== activity.id), activity])
    setStatus('ready')
  }
  return (
    <>
      <ActivityForm onCreated={created} />
      <section className="mt-10">
        <h2 className="text-xl font-bold">Your custom activities</h2>
        <button type="button" onClick={load} className="mt-4 rounded-lg border border-slate-300 bg-white px-4 py-3 font-semibold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-700">Refresh My Activities</button>
        {status === 'loading' && <p role="status" className="mt-6">Loading your activities...</p>}
        {status === 'error' && <p role="alert" className="mt-6">We couldn't load your activities. Check the local backend and refresh My Activities to retry.</p>}
        {status === 'ready' && (activities.length === 0 ? <p role="status" className="mt-6">No custom activities yet. Create your first activity above.</p> : <ul aria-label="Your custom activities" className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">{activities.map((activity) => <li key={activity.id} className="min-w-0"><ActivityCard activity={activity} /></li>)}</ul>)}
      </section>
    </>
  )
}
