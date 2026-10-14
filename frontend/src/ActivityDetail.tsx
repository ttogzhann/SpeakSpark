import { useEffect, useState } from 'react'
import type { Activity } from './activity'
import ActivityContent from './ActivityContent'

type DetailState =
  | { status: 'loading'; id: string }
  | { status: 'unavailable'; id: string }
  | { status: 'error'; id: string }
  | { status: 'ready'; id: string; activity: Activity }

export default function ActivityDetail({ activityId }: { activityId: string }) {
  const [state, setState] = useState<DetailState>({ status: 'loading', id: activityId })
  useEffect(() => {
    const controller = new AbortController()
    setState({ status: 'loading', id: activityId })
    fetch(`/api/activities/${encodeURIComponent(activityId)}`, { signal: controller.signal })
      .then(async (response) => {
        if (controller.signal.aborted) return
        if (response.status === 404 || response.status === 422) {
          setState({ status: 'unavailable', id: activityId })
          return
        }
        if (!response.ok) throw new Error('Detail request failed')
        const activity: Activity = await response.json()
        if (!controller.signal.aborted) setState({ status: 'ready', id: activityId, activity })
      })
      .catch(() => {
        if (!controller.signal.aborted) setState({ status: 'error', id: activityId })
      })
    return () => controller.abort()
  }, [activityId])

  const current = state.id === activityId ? state : { status: 'loading' as const, id: activityId }
  return (
    <section className="mt-8">
      <a href="#/library" className="font-semibold text-indigo-700 underline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-indigo-700">Back to Library</a>
      {current.status === 'loading' && <p role="status" className="mt-6">Loading activity...</p>}
      {current.status === 'unavailable' && <p role="alert" className="mt-6">This activity is no longer available. Return to Library to choose another activity.</p>}
      {current.status === 'error' && <p role="alert" className="mt-6">We couldn't load this activity. Check the local backend and reload, or return to Library.</p>}
      {current.status === 'ready' && <ActivityContent activity={current.activity} />}
    </section>
  )
}
