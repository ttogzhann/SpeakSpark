import { act, cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import ActivityDetail from './ActivityDetail'
import App from './App'
import type { Activity } from './activity'

const base: Activity = { id: 'custom-detail', title: 'A complete task', level: 'B1', topic: 'Work', type: 'Conversation Card', prompt: 'First line\nSecond line', is_builtin: false }
const guidance = { follow_up_questions: ['Follow this question'], useful_phrases: ['Please help'], instructions: ['Take turns'], roles: [{ participant: 'Tutor', objective: 'Ask about the plan' }] }
function respond(activity: Activity) {
  const mock = vi.fn().mockResolvedValue({ ok: true, json: async () => activity })
  vi.stubGlobal('fetch', mock)
  return mock
}
afterEach(() => { cleanup(); vi.unstubAllGlobals(); window.history.replaceState(null, '', '/') })

describe('Activity details', () => {
  it.each([true, false])('loads a direct route independently of Library for built-in=%s', async (isBuiltin) => {
    const mock = respond({ ...base, is_builtin: isBuiltin })
    window.history.replaceState(null, '', '/#/library/custom-detail')
    render(<App />)
    expect(await screen.findByRole('heading', { name: base.title })).toBeInTheDocument()
    expect(mock).toHaveBeenCalledWith('/api/activities/custom-detail', { signal: expect.any(AbortSignal) })
    expect(mock).toHaveBeenCalledTimes(1)
    expect(screen.getByText(/First line/).textContent).toBe(base.prompt)
    expect(screen.getByText('B1 / Work / Conversation Card')).toBeInTheDocument()
  })

  it.each([
    ['Conversation Card', ['Follow-up questions'], ['Participant roles', 'Useful phrases', 'Instructions', 'Supporting prompts']],
    ['Role-play', ['Participant roles', 'Useful phrases', 'Instructions'], ['Follow-up questions', 'Supporting prompts']],
    ['Speaking Challenge', ['Instructions', 'Supporting prompts'], ['Follow-up questions', 'Participant roles', 'Useful phrases']],
  ] as const)('renders only applicable %s guidance', async (type, shown, hidden) => {
    respond({ ...base, ...guidance, type })
    render(<ActivityDetail activityId={base.id} />)
    await screen.findByRole('heading', { name: base.title })
    for (const title of shown) expect(screen.getByRole('heading', { name: title })).toBeInTheDocument()
    for (const title of hidden) expect(screen.queryByRole('heading', { name: title })).not.toBeInTheDocument()
    if (type === 'Role-play') {
      expect(screen.getByText('Tutor')).toBeInTheDocument()
      expect(screen.getByText('Ask about the plan')).toBeInTheDocument()
    }
  })

  it.each(['Conversation Card', 'Role-play', 'Speaking Challenge'] as const)('omits missing and empty %s guidance without losing required content', async (type) => {
    respond({ ...base, type, follow_up_questions: [], instructions: [] })
    render(<ActivityDetail activityId={base.id} />)
    await screen.findByRole('heading', { name: base.title })
    expect(screen.getAllByRole('heading')).toHaveLength(1)
    expect(screen.getByText(/First line/)).toBeInTheDocument()
  })

  it('offers a return action while loading', () => {
    vi.stubGlobal('fetch', vi.fn().mockReturnValue(new Promise(() => {})))
    render(<ActivityDetail activityId={base.id} />)
    expect(screen.getByRole('status')).toHaveTextContent('Loading activity')
    expect(screen.getByRole('link', { name: 'Back to Library' })).toHaveAttribute('href', '#/library')
  })

  it.each([404, 422, 500, 'network'])('shows a helpful error with return action for %s', async (failure) => {
    vi.stubGlobal('fetch', failure === 'network' ? vi.fn().mockRejectedValue(new Error('offline')) : vi.fn().mockResolvedValue({ ok: false, status: failure }))
    render(<ActivityDetail activityId={base.id} />)
    expect(await screen.findByRole('alert')).toHaveTextContent(failure === 404 || failure === 422 ? 'no longer available' : "couldn't load this activity")
    expect(screen.queryByRole('heading')).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Back to Library' })).toBeInTheDocument()
  })

  it.each(['success', 'error'])('ignores stale detail %s when the ID changes', async (outcome) => {
    let resolveOld!: (value: unknown) => void
    let rejectOld!: (reason: unknown) => void
    vi.stubGlobal('fetch', vi.fn()
      .mockImplementationOnce(() => new Promise((resolve, reject) => { resolveOld = resolve; rejectOld = reject }))
      .mockResolvedValue({ ok: true, json: async () => ({ ...base, id: 'latest', title: 'Latest activity' }) }))
    const view = render(<ActivityDetail activityId="older" />)
    view.rerender(<ActivityDetail activityId="latest" />)
    await screen.findByRole('heading', { name: 'Latest activity' })
    await act(async () => {
      if (outcome === 'success') resolveOld({ ok: true, json: async () => base })
      else rejectOld(new Error('Older failure'))
    })
    expect(screen.getByRole('heading', { name: 'Latest activity' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: base.title })).not.toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })
})
