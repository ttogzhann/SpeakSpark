import { createContext, useContext, useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import type { Activity } from './activity'
import ActivityContent from './ActivityContent'

const FocusContext = createContext<((activity: Activity) => void) | null>(null)

export function FocusProvider({ children }: { children: ReactNode }) {
  const [activity, setActivity] = useState<Activity>()
  const returnFocus = useRef<HTMLElement | null>(null)
  const exitButton = useRef<HTMLButtonElement>(null)
  function enter(selected: Activity) {
    returnFocus.current = document.activeElement instanceof HTMLElement ? document.activeElement : null
    setActivity(selected)
  }
  function exit() {
    setActivity(undefined)
    requestAnimationFrame(() => returnFocus.current?.focus())
  }
  useEffect(() => {
    if (!activity) return
    exitButton.current?.focus()
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { event.preventDefault(); exit() }
    }
    window.addEventListener('keydown', onKey)
    window.addEventListener('hashchange', exit)
    return () => { window.removeEventListener('keydown', onKey); window.removeEventListener('hashchange', exit) }
  }, [activity])
  return (
    <FocusContext.Provider value={enter}>
      <div hidden={!!activity} inert={!!activity}>{children}</div>
      {activity && <main aria-label="Focus Mode" className="min-h-screen bg-slate-50 px-4 py-6 text-slate-900 sm:px-8 sm:py-10">
        <div className="mx-auto max-w-5xl">
          <button ref={exitButton} type="button" onClick={exit} className="rounded-lg border border-slate-300 bg-white px-4 py-3 font-semibold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-700">Exit Focus Mode</button>
          <ActivityContent activity={activity} presentation />
        </div>
      </main>}
    </FocusContext.Provider>
  )
}

export function FocusButton({ activity }: { activity: Activity }) {
  const enter = useContext(FocusContext)
  if (!enter) return null
  return <button type="button" onClick={() => enter(activity)} className="mt-4 rounded-lg bg-indigo-700 px-4 py-3 font-semibold text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-700">Enter Focus Mode</button>
}
