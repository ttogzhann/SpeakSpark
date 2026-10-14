import type { Activity } from './activity'
import { FavoriteButton } from './Favorites'

export default function ActivityCard({ activity }: { activity: Activity }) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-6 [overflow-wrap:anywhere]">
      <a href={`#/library/${encodeURIComponent(activity.id)}`} className="block rounded hover:text-indigo-600 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-indigo-700">
        <h2 className="text-xl font-semibold text-indigo-800">{activity.title}</h2>
        <dl className="mt-4 space-y-2 text-sm text-slate-600">
          <div><dt className="inline font-semibold">Level: </dt><dd className="inline">{activity.level}</dd></div>
          <div><dt className="inline font-semibold">Topic: </dt><dd className="inline">{activity.topic}</dd></div>
          <div><dt className="inline font-semibold">Type: </dt><dd className="inline">{activity.type}</dd></div>
        </dl>
      </a>
      <FavoriteButton activity={activity} />
    </article>
  )
}
