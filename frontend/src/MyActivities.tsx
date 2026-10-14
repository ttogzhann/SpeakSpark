import { useEffect, useRef, useState } from 'react'
import type { Activity } from './activity'
import ActivityCard from './ActivityCard'
import ActivityForm from './ActivityForm'
import { useFavoriteRecordChange } from './Favorites'

export default function MyActivities() {
  const [activities, setActivities] = useState<Activity[]>([])
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading')
  const revision = useRef(0)
  const mounted = useRef(true)
  const [editing, setEditing] = useState<Activity>()
  const [deleting, setDeleting] = useState<Activity>()
  const [deletePending, setDeletePending] = useState(false)
  const [formPending, setFormPending] = useState(false)
  const [deleteError, setDeleteError] = useState('')
  const deleteGuard = useRef(false)
  const recordChanged = useFavoriteRecordChange()
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
    if (editing) {
      recordChanged?.(activity.id, activity)
      setEditing(undefined)
    }
  }
  async function remove() {
    if (!deleting || deleting.is_builtin || deleteGuard.current) return
    deleteGuard.current = true
    setDeletePending(true)
    setDeleteError('')
    try {
      const response = await fetch(`/api/activities/${encodeURIComponent(deleting.id)}`, { method: 'DELETE' })
      if (response.status !== 204) throw new Error('Delete failed')
      ++revision.current
      setActivities((current) => current.filter((activity) => activity.id !== deleting.id))
      recordChanged?.(deleting.id)
      if (editing?.id === deleting.id) setEditing(undefined)
      setDeleting(undefined)
    } catch {
      setDeleteError('Could not confirm deletion. Refresh My Activities to check the activity before trying again.')
    } finally {
      deleteGuard.current = false
      setDeletePending(false)
    }
  }
  return (
    <>
      <ActivityForm key={editing?.id ?? 'create'} initialActivity={editing} onCreated={created} onPendingChange={setFormPending} onCancel={editing ? () => setEditing(undefined) : undefined} />
      {deleting && <section aria-label="Delete confirmation" className="mt-6 rounded-lg border border-red-300 bg-white p-4 [overflow-wrap:anywhere]">
        <p>Delete "{deleting.title}"? This also removes it from Favorites.</p>
        <div className="mt-4 flex flex-wrap gap-3">
          <button type="button" disabled={deletePending || formPending} onClick={remove} className="rounded border border-red-500 px-4 py-3 font-semibold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-700">{deletePending ? 'Deleting activity...' : 'Confirm delete'}</button>
          <button type="button" disabled={deletePending || formPending} onClick={() => { setDeleting(undefined); setDeleteError('') }} className="rounded border px-4 py-3 focus-visible:outline-2 focus-visible:outline-indigo-700">Cancel deletion</button>
        </div>
        {deleteError && <p role="alert" className="mt-3 text-red-800">{deleteError}</p>}
      </section>}
      <section className="mt-10">
        <h2 className="text-xl font-bold">Your custom activities</h2>
        <button type="button" disabled={deletePending || formPending} onClick={load} className="mt-4 rounded-lg border border-slate-300 bg-white px-4 py-3 font-semibold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-700">Refresh My Activities</button>
        {status === 'loading' && <p role="status" className="mt-6">Loading your activities...</p>}
        {status === 'error' && <p role="alert" className="mt-6">We couldn't load your activities. Check the local backend and refresh My Activities to retry.</p>}
        {status === 'ready' && (activities.length === 0 ? <p role="status" className="mt-6">No custom activities yet. Create your first activity above.</p> : <ul aria-label="Your custom activities" className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">{activities.map((activity) => <li key={activity.id} className="min-w-0"><ActivityCard activity={activity} /><div className="mt-3 flex flex-wrap gap-3"><button type="button" disabled={deletePending || formPending} onClick={() => { if (!activity.is_builtin) setEditing(activity) }} className="rounded border px-4 py-3 focus-visible:outline-2 focus-visible:outline-indigo-700">Edit {activity.title}</button><button type="button" disabled={deletePending || formPending} onClick={() => { if (!activity.is_builtin) { setDeleting(activity); setDeleteError('') } }} className="rounded border px-4 py-3 focus-visible:outline-2 focus-visible:outline-indigo-700">Delete {activity.title}</button></div></li>)}</ul>)}
      </section>
    </>
  )
}
