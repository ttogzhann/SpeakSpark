import type { Activity } from './activity'
import { FavoriteButton } from './Favorites'
import { FocusButton } from './FocusMode'

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

export default function ActivityContent({ activity, presentation = false }: { activity: Activity; presentation?: boolean }) {
  return (
<article className="mt-6 rounded-xl border border-slate-200 bg-white p-6 [overflow-wrap:anywhere]">
          <h2 className={presentation ? 'text-3xl font-bold sm:text-5xl' : 'text-2xl font-bold'}>{activity.title}</h2>
          <p className="mt-3 text-sm text-slate-600">{activity.level} / {activity.topic} / {activity.type}</p>
          <p className={`mt-6 whitespace-pre-wrap ${presentation ? 'text-2xl leading-relaxed sm:text-3xl' : 'text-lg'}`}>{activity.prompt}</p>
          {!presentation && <><FavoriteButton activity={activity} /><FocusButton activity={activity} /></>}
          {activity.type === 'Conversation Card' && <Guidance title="Follow-up questions" items={activity.follow_up_questions} />}
          {activity.type === 'Role-play' && (
            <>
              {!!activity.roles?.length && (
                <section className="mt-6">
                  <h3 className="text-lg font-semibold">Participant roles</h3>
                  <dl className="mt-2 space-y-3">
                    {activity.roles.map((role, index) => (
                      <div key={index}>
                        <dt className="whitespace-pre-wrap font-semibold">{role.participant}</dt>
                        <dd className="mt-1 whitespace-pre-wrap">{role.objective}</dd>
                      </div>
                    ))}
                  </dl>
                </section>
              )}
              <Guidance title="Useful phrases" items={activity.useful_phrases} />
              <Guidance title="Instructions" items={activity.instructions} />
            </>
          )}
          {activity.type === 'Speaking Challenge' && (
            <>
              <Guidance title="Instructions" items={activity.instructions} />
              <Guidance title="Supporting prompts" items={activity.follow_up_questions} />
            </>
          )}
        </article>
  )
}

