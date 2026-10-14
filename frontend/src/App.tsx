import { useEffect, useState } from 'react'
import Library from './Library'

const sections = [
  { path: '/library', title: 'Library', description: 'Find speaking activities for your next lesson.' },
  { path: '/surprise-me', title: 'Surprise Me', description: 'Discover a speaking activity for your students.' },
  { path: '/favorites', title: 'Favorites', description: 'Keep your saved speaking activities close at hand.' },
  { path: '/my-activities', title: 'My Activities', description: 'Make space for your own speaking activities.' },
] as const

function currentSection() {
  const path = window.location.hash.slice(1)
  const section = sections.find((item) => item.path === path || (item.path === '/library' && path.startsWith('/library/'))) ?? sections[0]
  let activityId: string | undefined
  if (path.startsWith('/library/')) {
    try { activityId = decodeURIComponent(path.slice('/library/'.length)) } catch { activityId = path.slice('/library/'.length) }
  }
  return { ...section, activityId }
}

export default function App() {
  const [section, setSection] = useState(currentSection)

  useEffect(() => {
    const updateSection = () => setSection(currentSection())
    window.addEventListener('hashchange', updateSection)
    return () => window.removeEventListener('hashchange', updateSection)
  }, [])

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-6 sm:px-8">
          <p className="text-2xl font-bold tracking-tight">SpeakSpark</p>
          <p className="mt-1 text-sm text-slate-600">Your speaking activity workspace.</p>
          <nav aria-label="Main navigation" className="mt-6 flex flex-wrap gap-2">
            {sections.map((item) => (
              <a
                key={item.path}
                href={`#${item.path}`}
                aria-current={item.path === section.path ? 'page' : undefined}
                className={`rounded-lg px-4 py-3 text-sm font-semibold transition-colors focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-indigo-700 ${
                  item.path === section.path
                    ? 'bg-indigo-700 text-white'
                    : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                {item.title}
              </a>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-8 sm:py-14">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">{section.title}</h1>
        <p className="mt-3 max-w-2xl text-lg text-slate-600">{section.description}</p>
        {section.path === '/library' && <Library activityId={section.activityId} />}
      </main>
    </div>
  )
}
