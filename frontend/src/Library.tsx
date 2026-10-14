import { useEffect, useState } from 'react'

export interface Activity {
  id: string
  title: string
  level: string
  topic: string
  type: string
  prompt: string
  is_builtin: boolean
}

type LibraryState =
  | { status: 'loading' }
  | { status: 'error' }
  | { status: 'ready'; activities: Activity[] }

export default function Library({ activityId }: { activityId?: string }) {
  const [state, setState] = useState<LibraryState>({ status: 'loading' })

  useEffect(() => {
    const controller = new AbortController()
    fetch('/api/activities', { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error('Activity request failed')
        return response.json() as Promise<Activity[]>
      })
      .then((activities) => {
        if (!controller.signal.aborted) setState({ status: 'ready', activities })
      })
      .catch(() => {
        if (!controller.signal.aborted) setState({ status: 'error' })
      })
    return () => controller.abort()
  }, [])

  if (state.status === 'loading') return <p role="status" className="mt-8">Loading activities...</p>
  if (state.status === 'error') return <p role="alert" className="mt-8">We couldn't load the activities. Check that the local backend is running, then reload to try again.</p>

  if (activityId) {
    const activity = state.activities.find((item) => item.id === activityId)
    return (
      <section className="mt-8">
        <a href="#/library" className="font-semibold text-indigo-700 underline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-indigo-700">Back to Library</a>
        {activity ? (
          <article className="mt-6 rounded-xl border border-slate-200 bg-white p-6 [overflow-wrap:anywhere]">
            <h2 className="text-2xl font-bold">{activity.title}</h2>
            <p className="mt-3 text-sm text-slate-600">{activity.level} � {activity.topic} � {activity.type}</p>
            <p className="mt-6 whitespace-pre-wrap text-lg">{activity.prompt}</p>
          </article>
        ) : <p role="status" className="mt-6">This activity is no longer available.</p>}
      </section>
    )
  }

  if (state.activities.length === 0) return <p role="status" className="mt-8">Your Library has no activities yet.</p>

  return (
    <ul aria-label="Speaking activities" className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {state.activities.map((activity) => (
        <li key={activity.id} className="min-w-0">
          <a href={`#/library/${encodeURIComponent(activity.id)}`} className="block h-full rounded-xl border border-slate-200 bg-white p-6 [overflow-wrap:anywhere] hover:border-indigo-400 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-indigo-700">
            <h2 className="text-xl font-semibold text-indigo-800">{activity.title}</h2>
            <dl className="mt-4 space-y-2 text-sm text-slate-600">
              <div><dt className="inline font-semibold">Level: </dt><dd className="inline">{activity.level}</dd></div>
              <div><dt className="inline font-semibold">Topic: </dt><dd className="inline">{activity.topic}</dd></div>
              <div><dt className="inline font-semibold">Type: </dt><dd className="inline">{activity.type}</dd></div>
            </dl>
          </a>
        </li>
      ))}
    </ul>
  )
}

