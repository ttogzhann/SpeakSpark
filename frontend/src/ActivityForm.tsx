import { useRef, useState } from 'react'
import type { FormEvent } from 'react'
import type { Activity } from './activity'

const levels = ['A1', 'A2', 'B1', 'B2']
const topics = ['Daily Life', 'Travel', 'Food', 'Education', 'Work', 'Hobbies', 'Technology', 'Relationships']
const types = ['Conversation Card', 'Role-play', 'Speaking Challenge']
const fieldClass = 'mt-2 block min-h-11 w-full min-w-0 rounded-lg border border-slate-300 bg-white px-3 py-2 font-normal focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-700'
const buttonClass = 'min-h-11 rounded-lg border border-indigo-300 bg-white px-4 py-2 font-semibold text-indigo-800 disabled:opacity-60 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-700'
const lines = (value: string) => value.split('\n').map((item) => item.trim()).filter(Boolean)

export default function ActivityForm({ onCreated }: { onCreated: (activity: Activity) => void }) {
  const [title, setTitle] = useState('')
  const [level, setLevel] = useState('')
  const [topic, setTopic] = useState('')
  const [type, setType] = useState('')
  const [prompt, setPrompt] = useState('')
  const [questions, setQuestions] = useState('')
  const [phrases, setPhrases] = useState('')
  const [instructions, setInstructions] = useState('')
  const [roles, setRoles] = useState([{ participant: '', objective: '' }])
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)
  const [pending, setPending] = useState(false)
  const pendingRef = useRef(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (pendingRef.current) return
    setError('')
    setSaved(false)
    if (!title.trim() || !prompt.trim() || !levels.includes(level) || !topics.includes(topic) || !types.includes(type)) {
      setError('Enter a title and speaking prompt, and choose a supported level, topic, and activity type.')
      return
    }
    const nonemptyRoles = roles.map((role) => ({ participant: role.participant.trim(), objective: role.objective.trim() })).filter((role) => role.participant || role.objective)
    if (type === 'Role-play' && nonemptyRoles.some((role) => !role.participant || !role.objective)) {
      setError('Complete both participant and objective for each role, or leave both blank.')
      return
    }
    const payload = {
      title: title.trim(), level, topic, type, prompt: prompt.trim(),
      follow_up_questions: type === 'Role-play' ? [] : lines(questions),
      useful_phrases: type === 'Role-play' ? lines(phrases) : [],
      roles: type === 'Role-play' ? nonemptyRoles : [],
      instructions: type === 'Conversation Card' ? [] : lines(instructions),
    }
    pendingRef.current = true
    setPending(true)
    try {
      const response = await fetch('/api/activities', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      if (response.status !== 201) {
        setError(response.status === 422 ? 'The backend rejected these values. Check the required fields and optional role pairs, then correct and try again.' : 'The backend could not save this activity. Your entries are preserved; try again when it is available.')
        return
      }
      const activity: Activity = await response.json()
      onCreated(activity)
      setSaved(true)
      setTitle(''); setLevel(''); setTopic(''); setType(''); setPrompt(''); setQuestions(''); setPhrases(''); setInstructions(''); setRoles([{ participant: '', objective: '' }])
    } catch {
      setError('We could not confirm the save. Your entries are preserved. Refresh My Activities to check whether it was saved before trying again.')
    } finally {
      pendingRef.current = false
      setPending(false)
    }
  }

  return (
    <form onSubmit={submit} noValidate className="mt-8 min-w-0 rounded-xl border border-slate-200 bg-white p-4 sm:p-6">
      <h2 className="text-xl font-bold">Create an activity</h2>
      <p className="mt-2 text-sm text-slate-600">Title, level, topic, activity type, and speaking prompt are required. Optional lists use one item per line.</p>
      <fieldset disabled={pending} className="mt-6 min-w-0 space-y-4">
        <label className="block font-semibold">Title<input required value={title} onChange={(event) => setTitle(event.target.value)} className={fieldClass} /></label>
        <div className="grid min-w-0 gap-4 md:grid-cols-3">
          <label className="min-w-0 font-semibold">Level<select required value={level} onChange={(event) => setLevel(event.target.value)} className={fieldClass}><option value="">Choose level</option>{levels.map((value) => <option key={value}>{value}</option>)}</select></label>
          <label className="min-w-0 font-semibold">Topic<select required value={topic} onChange={(event) => setTopic(event.target.value)} className={fieldClass}><option value="">Choose topic</option>{topics.map((value) => <option key={value}>{value}</option>)}</select></label>
          <label className="min-w-0 font-semibold">Activity type<select required value={type} onChange={(event) => setType(event.target.value)} className={fieldClass}><option value="">Choose type</option>{types.map((value) => <option key={value}>{value}</option>)}</select></label>
        </div>
        <label className="block font-semibold">Speaking prompt<textarea required rows={4} value={prompt} onChange={(event) => setPrompt(event.target.value)} className={fieldClass} /></label>
        {(type === 'Conversation Card' || type === 'Speaking Challenge') && <label className="block font-semibold">{type === 'Conversation Card' ? 'Follow-up questions (optional)' : 'Supporting prompts (optional)'}<textarea rows={3} value={questions} onChange={(event) => setQuestions(event.target.value)} className={fieldClass} /></label>}
        {type === 'Role-play' && (
          <section>
            <h3 className="font-semibold">Participant roles (optional)</h3>
            {roles.map((role, index) => (
              <div key={index} className="mt-3 grid min-w-0 gap-3 rounded-lg border border-slate-200 p-3 md:grid-cols-2">
                <label className="min-w-0 font-semibold">Participant {index + 1}<input value={role.participant} onChange={(event) => setRoles(roles.map((item, position) => position === index ? { ...item, participant: event.target.value } : item))} className={fieldClass} /></label>
                <label className="min-w-0 font-semibold">Objective {index + 1}<textarea rows={2} value={role.objective} onChange={(event) => setRoles(roles.map((item, position) => position === index ? { ...item, objective: event.target.value } : item))} className={fieldClass} /></label>
                <button type="button" onClick={() => setRoles(roles.filter((_, position) => position !== index))} className={buttonClass}>Remove role {index + 1}</button>
              </div>
            ))}
            <button type="button" onClick={() => setRoles([...roles, { participant: '', objective: '' }])} className={`mt-3 ${buttonClass}`}>Add role</button>
            <label className="mt-4 block font-semibold">Useful phrases (optional)<textarea rows={3} value={phrases} onChange={(event) => setPhrases(event.target.value)} className={fieldClass} /></label>
          </section>
        )}
        {(type === 'Role-play' || type === 'Speaking Challenge') && <label className="block font-semibold">Instructions (optional)<textarea rows={3} value={instructions} onChange={(event) => setInstructions(event.target.value)} className={fieldClass} /></label>}
        <button type="submit" className={buttonClass}>{pending ? 'Saving activity...' : 'Create activity'}</button>
      </fieldset>
      {pending && <p role="status" className="mt-4">Saving activity...</p>}
      {error && <p role="alert" className="mt-4 text-red-800">{error}</p>}
      {saved && <p role="status" className="mt-4 text-green-800">Activity saved. Find it below or in Library.</p>}
    </form>
  )
}
