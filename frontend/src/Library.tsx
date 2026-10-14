import { useEffect, useState } from 'react'

import type { Activity } from './activity'
import ActivityDetail from './ActivityDetail'
import ActivityCard from './ActivityCard'

const filterOptions = {
  level: ['A1', 'A2', 'B1', 'B2'],
  topic: ['Daily Life', 'Travel', 'Food', 'Education', 'Work', 'Hobbies', 'Technology', 'Relationships'],
  type: ['Conversation Cards', 'Role-play Scenarios', 'Speaking Challenges'],
}
const emptyFilters = { level: '', topic: '', type: '' }

type LibraryState =
  | { status: 'loading'; query: string }
  | { status: 'error'; query: string }
  | { status: 'ready'; query: string; activities: Activity[] }

export default function Library({ activityId }: { activityId?: string }) {
  const [filters, setFilters] = useState(emptyFilters)
  const parameters = new URLSearchParams()
  for (const key of ['level', 'topic', 'type'] as const) {
    if (filters[key]) parameters.set(key, filters[key])
  }
  const query = parameters.toString()
  const [state, setState] = useState<LibraryState>({ status: 'loading', query })

  useEffect(() => {
    if (activityId) return
    const controller = new AbortController()
    setState({ status: 'loading', query })
    fetch(`/api/activities${query ? `?${query}` : ''}`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error('Activity request failed')
        return response.json() as Promise<Activity[]>
      })
      .then((activities) => {
        if (!controller.signal.aborted) setState({ status: 'ready', query, activities })
      })
      .catch(() => {
        if (!controller.signal.aborted) setState({ status: 'error', query })
      })
    return () => controller.abort()
  }, [query, !!activityId])

  if (activityId) return <ActivityDetail activityId={activityId} />

  const current: LibraryState = state.query === query ? state : { status: 'loading', query }
  let content
  if (current.status === 'loading') {
    content = <p role="status" className="mt-8">Loading activities...</p>
  } else if (current.status === 'error') {
    content = <p role="alert" className="mt-8">We couldn't load the activities. Check that the local backend is running, then change filters or reload to try again.</p>
  } else if (current.activities.length === 0) {
    content = <p role="status" className="mt-8">{query ? 'No activities match these filters. Try changing or clearing them.' : 'Your Library has no activities yet.'}</p>
  } else {
    content = (
      <ul aria-label="Speaking activities" className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {current.activities.map((activity) => (
          <li key={activity.id} className="min-w-0">
            <ActivityCard activity={activity} />
          </li>
        ))}
      </ul>
    )
  }

  return (
    <section className="mt-8">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {(['level', 'topic', 'type'] as const).map((key) => (
            <label key={key} className="min-w-0 text-sm font-semibold">
              {key === 'level' ? 'Level' : key === 'topic' ? 'Topic' : 'Activity type'}
              <select value={filters[key]} onChange={(event) => setFilters({ ...filters, [key]: event.target.value })} className="mt-2 block min-h-12 w-full min-w-0 rounded-lg border border-slate-300 bg-white px-3 text-sm font-normal focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-700">
                <option value="">{key === 'level' ? 'All levels' : key === 'topic' ? 'All topics' : 'All types'}</option>
                {filterOptions[key].map((value) => <option key={value} value={value}>{value}</option>)}
              </select>
            </label>
          ))}
          <button type="button" onClick={() => setFilters(emptyFilters)} className="min-h-12 self-end rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm font-semibold hover:bg-slate-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-700">Clear all</button>
        </div>
      {content}
    </section>
  )
}
