import { createContext, useContext, useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import type { Activity } from './activity'
import ActivityCard from './ActivityCard'

type FavoritesContextValue = {
  activities: Activity[]
  status: 'loading' | 'ready' | 'error'
  pending: Set<string>
  errors: Record<string, string>
  refresh: () => void
  toggle: (activity: Activity) => void
}
const FavoritesContext = createContext<FavoritesContextValue | null>(null)

export function FavoritesProvider({ children }: { children: ReactNode }) {
  const [activities, setActivities] = useState<Activity[]>([])
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading')
  const [pending, setPending] = useState(new Set<string>())
  const [errors, setErrors] = useState<Record<string, string>>({})
  const pendingRef = useRef(new Set<string>())
  const revision = useRef(0)
  const mounted = useRef(true)

  function refresh() {
    if (pendingRef.current.size) return
    const requestRevision = ++revision.current
    setStatus('loading')
    fetch('/api/favorites')
      .then(async (response) => {
        if (!response.ok) throw new Error('Favorites request failed')
        const records: Activity[] = await response.json()
        if (mounted.current && revision.current === requestRevision) {
          setActivities(records)
          setStatus('ready')
        }
      })
      .catch(() => {
        if (mounted.current && revision.current === requestRevision) setStatus('error')
      })
  }

  useEffect(() => {
    mounted.current = true
    refresh()
    return () => { mounted.current = false; ++revision.current }
  }, [])

  async function toggle(activity: Activity) {
    if (status !== 'ready' || pendingRef.current.has(activity.id)) return
    const saved = activities.some((item) => item.id === activity.id)
    pendingRef.current.add(activity.id)
    setPending(new Set(pendingRef.current))
    setErrors((current) => ({ ...current, [activity.id]: '' }))
    ++revision.current
    try {
      const response = await fetch(saved ? `/api/favorites/${encodeURIComponent(activity.id)}` : '/api/favorites', saved
        ? { method: 'DELETE' }
        : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ activity_id: activity.id }) })
      if (!response.ok) throw new Error('Favorite update failed')
      if (!mounted.current) return
      ++revision.current
      setActivities((current) => saved ? current.filter((item) => item.id !== activity.id) : [...current.filter((item) => item.id !== activity.id), activity])
    } catch {
      if (mounted.current) setErrors((current) => ({ ...current, [activity.id]: "Couldn't update this Favorite. Please try again." }))
    } finally {
      pendingRef.current.delete(activity.id)
      if (mounted.current) setPending(new Set(pendingRef.current))
    }
  }

  return <FavoritesContext.Provider value={{ activities, status, pending, errors, refresh, toggle }}>{children}</FavoritesContext.Provider>
}

export function FavoriteButton({ activity }: { activity: Activity }) {
  const favorites = useContext(FavoritesContext)
  if (!favorites) return null
  const saved = favorites.activities.some((item) => item.id === activity.id)
  const busy = favorites.pending.has(activity.id)
  return (
    <div className="mt-4">
      <button type="button" disabled={favorites.status !== 'ready' || busy} aria-pressed={favorites.status === 'ready' ? saved : undefined}
        onClick={() => favorites.toggle(activity)} className="min-h-11 rounded-lg border border-indigo-300 bg-white px-4 py-2 text-sm font-semibold text-indigo-800 disabled:opacity-60 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-700">
        {favorites.status === 'loading' ? 'Loading Favorites...' : favorites.status === 'error' ? 'Favorite status unavailable' : busy ? 'Updating Favorite...' : saved ? 'Remove from Favorites' : 'Add to Favorites'}
        <span className="sr-only">: {activity.title}</span>
      </button>
      {favorites.status === 'error' && <button type="button" onClick={favorites.refresh} className="ml-2 rounded px-2 py-2 text-sm underline focus-visible:outline-2 focus-visible:outline-indigo-700">Retry Favorites</button>}
      {favorites.errors[activity.id] && <p role="alert" className="mt-2 text-sm text-red-800">{favorites.errors[activity.id]}</p>}
    </div>
  )
}

export default function Favorites() {
  const favorites = useContext(FavoritesContext)!
  useEffect(() => { favorites.refresh() }, [])
  return (
    <section className="mt-8">
      <button type="button" disabled={favorites.pending.size > 0} onClick={favorites.refresh} className="rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm font-semibold disabled:opacity-60 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-700">Refresh Favorites</button>
      {favorites.status === 'loading' && <p role="status" className="mt-6">Loading Favorites...</p>}
      {favorites.status === 'error' && <p role="alert" className="mt-6">We couldn't load Favorites. Check the local backend and refresh Favorites to try again.</p>}
      {favorites.status === 'ready' && (favorites.activities.length === 0
        ? <p role="status" className="mt-6">No Favorites yet. Save activities from Library to find them here.</p>
        : <ul aria-label="Favorite activities" className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">{favorites.activities.map((activity) => <li key={activity.id} className="min-w-0"><ActivityCard activity={activity} /></li>)}</ul>)}
    </section>
  )
}
