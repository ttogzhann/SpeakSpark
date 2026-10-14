import { useEffect, useState } from 'react'
import type { Activity } from './activity'

type DetailState =
  | { status: 'loading'; id: string }
  | { status: 'unavailable'; id: string }
  | { status: 'error'; id: string }
  | { status: 'ready'; id: string; activity: Activity }

function Guidance({ title, items }: { title: string; items?: string[] }) {
  if (!items?.length) return null
  return (
    <section className="mt-6">
      <h3 className="text-lg font-semibold">{title}</h3>
      <ul className="mt-2 list-disc space-y-2 pl-6">
        {items.map((item, index) => <li key={index} className="whitespace-pre-wrap">{item}</li>)}
      </ul>
    </section>
  )
}

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
      {current.status === 'ready' && (
        <article className="mt-6 rounded-xl border border-slate-200 bg-white p-6 [overflow-wrap:anywhere]">
          <h2 className="text-2xl font-bold">{current.activity.title}</h2>
          <p className="mt-3 text-sm text-slate-600">{current.activity.level} / {current.activity.topic} / {current.activity.type}</p>
          <p className="mt-6 whitespace-pre-wrap text-lg">{current.activity.prompt}</p>
          {current.activity.type === 'Conversation Card' && <Guidance title="Follow-up questions" items={current.activity.follow_up_questions} />}
          {current.activity.type === 'Role-play' && (
            <>
              {!!current.activity.roles?.length && (
                <section className="mt-6">
                  <h3 className="text-lg font-semibold">Participant roles</h3>
                  <dl className="mt-2 space-y-3">
                    {current.activity.roles.map((role, index) => (
                      <div key={index}>
                        <dt className="whitespace-pre-wrap font-semibold">{role.participant}</dt>
                        <dd className="mt-1 whitespace-pre-wrap">{role.objective}</dd>
                      </div>
                    ))}
                  </dl>
                </section>
              )}
              <Guidance title="Useful phrases" items={current.activity.useful_phrases} />
              <Guidance title="Instructions" items={current.activity.instructions} />
            </>
          )}
          {current.activity.type === 'Speaking Challenge' && (
            <>
              <Guidance title="Instructions" items={current.activity.instructions} />
              <Guidance title="Supporting prompts" items={current.activity.follow_up_questions} />
            </>
          )}
        </article>
      )}
    </section>
  )
}
