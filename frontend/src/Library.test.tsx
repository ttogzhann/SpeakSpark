import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import Library from './Library'

const activities = [
  { id: 'builtin-one', title: 'Airport plans', level: 'A2', topic: 'Travel', type: 'Role-play', prompt: 'Ask for a flight.', is_builtin: true },
  { id: 'custom-one', title: 'My discussion', level: 'B1', topic: 'Work', type: 'Conversation Card', prompt: 'Discuss your ideal job.', is_builtin: false },
]

beforeEach(() => window.history.replaceState(null, '', '/'))
afterEach(() => { cleanup(); vi.unstubAllGlobals() })

function respond(data = activities) {
  const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => data })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

describe('Library', () => {
  it('requests backend data and presents both sources with their own metadata', async () => {
    const fetchMock = respond()
    render(<Library />)
    const list = await screen.findByRole('list', { name: 'Speaking activities' })
    expect(fetchMock).toHaveBeenCalledWith('/api/activities', { signal: expect.any(AbortSignal) })
    expect(within(list).getAllByRole('listitem')).toHaveLength(2)
    for (const activity of activities) {
      const card = within(list).getByRole('link', { name: new RegExp(activity.title) })
      for (const value of [activity.title, activity.level, activity.topic, activity.type]) expect(card).toHaveTextContent(value)
    }
  })

  it.each(activities)('opens the correct title and prompt for $id and returns to Library', async (activity) => {
    respond()
    render(<App />)
    fireEvent.click(await screen.findByRole('link', { name: new RegExp(activity.title) }))
    expect(await screen.findByText(activity.prompt)).toBeInTheDocument()
    expect(window.location.hash).toBe(`#/library/${activity.id}`)
    expect(screen.getByRole('heading', { name: activity.title })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Library' })).toHaveAttribute('aria-current', 'page')
    fireEvent.click(screen.getByRole('link', { name: 'Back to Library' }))
    expect(await screen.findByRole('list', { name: 'Speaking activities' })).toBeInTheDocument()
  })

  it('keeps pending loading separate from empty and error states', () => {
    vi.stubGlobal('fetch', vi.fn().mockReturnValue(new Promise(() => {})))
    render(<Library />)
    expect(screen.getByRole('status')).toHaveTextContent('Loading activities')
    expect(screen.queryByText(/no activities/)).not.toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('shows a successful empty collection without cards or an error', async () => {
    respond([])
    render(<Library />)
    expect(await screen.findByText('Your Library has no activities yet.')).toBeInTheDocument()
    expect(screen.queryByRole('list', { name: 'Speaking activities' })).not.toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it.each(['http', 'network'])('shows a helpful %s error without pretending the collection is empty', async (failure) => {
    vi.stubGlobal('fetch', failure === 'http'
      ? vi.fn().mockResolvedValue({ ok: false, status: 500 })
      : vi.fn().mockRejectedValue(new TypeError('Network unavailable')))
    render(<Library />)
    expect(await screen.findByRole('alert')).toHaveTextContent("We couldn't load the activities")
    expect(screen.queryByText(/no activities/)).not.toBeInTheDocument()
    expect(screen.queryByRole('list', { name: 'Speaking activities' })).not.toBeInTheDocument()
  })

  it('loads an activity destination directly and handles a missing activity', async () => {
    respond()
    render(<Library activityId="missing-id" />)
    expect(await screen.findByText('This activity is no longer available.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Back to Library' })).toHaveAttribute('href', '#/library')
  })

  it('offers the approved options and sends complete backend queries when changing and clearing filters', async () => {
    const fetchMock = respond()
    render(<Library />)
    await screen.findByRole('list', { name: 'Speaking activities' })
    const level = screen.getByRole('combobox', { name: 'Level' })
    const topic = screen.getByRole('combobox', { name: 'Topic' })
    const type = screen.getByRole('combobox', { name: 'Activity type' })
    expect(within(level).getAllByRole('option').map((option) => option.textContent)).toEqual(['All levels', 'A1', 'A2', 'B1', 'B2'])
    expect(within(topic).getAllByRole('option').map((option) => option.textContent)).toEqual(['All topics', 'Daily Life', 'Travel', 'Food', 'Education', 'Work', 'Hobbies', 'Technology', 'Relationships'])
    expect(within(type).getAllByRole('option').map((option) => option.textContent)).toEqual(['All types', 'Conversation Cards', 'Role-play Scenarios', 'Speaking Challenges'])
    fireEvent.change(level, { target: { value: 'A2' } })
    fireEvent.change(topic, { target: { value: 'Travel' } })
    fireEvent.change(type, { target: { value: 'Role-play Scenarios' } })
    await waitFor(() => expect(fetchMock).toHaveBeenLastCalledWith('/api/activities?level=A2&topic=Travel&type=Role-play+Scenarios', expect.any(Object)))
    // Render the backend response as supplied, even if a fixture does not match filters.
    expect(await screen.findByRole('link', { name: /My discussion/ })).toBeInTheDocument()
    fireEvent.change(topic, { target: { value: '' } })
    await waitFor(() => expect(fetchMock).toHaveBeenLastCalledWith('/api/activities?level=A2&type=Role-play+Scenarios', expect.any(Object)))
    fireEvent.click(screen.getByRole('button', { name: 'Clear all' }))
    await waitFor(() => expect(fetchMock).toHaveBeenLastCalledWith('/api/activities', expect.any(Object)))
    for (const control of [level, topic, type]) expect(control).toHaveValue('')
  })

  it('keeps controls available through filtered loading, zero matches, and failure without stale cards', async () => {
    const fetchMock = respond()
    render(<Library />)
    await screen.findByRole('link', { name: /Airport plans/ })
    let resolvePending!: (value: unknown) => void
    fetchMock.mockImplementationOnce(() => new Promise((resolve) => { resolvePending = resolve }))
    fireEvent.change(screen.getByRole('combobox', { name: 'Level' }), { target: { value: 'B2' } })
    expect(screen.getByRole('status')).toHaveTextContent('Loading')
    expect(screen.queryByRole('link', { name: /Airport plans/ })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Clear all' })).toBeInTheDocument()
    await act(async () => resolvePending({ ok: true, json: async () => [] }))
    expect(screen.getByRole('status')).toHaveTextContent('No activities match these filters')
    fetchMock.mockRejectedValueOnce(new Error('Network unavailable'))
    fireEvent.change(screen.getByRole('combobox', { name: 'Topic' }), { target: { value: 'Work' } })
    expect(await screen.findByRole('alert')).toBeInTheDocument()
    expect(screen.getByRole('combobox', { name: 'Level' })).toHaveValue('B2')
    fireEvent.click(screen.getByRole('button', { name: 'Clear all' }))
    expect(await screen.findByRole('link', { name: /Airport plans/ })).toBeInTheDocument()
  })

  it.each(['success', 'error'])('ignores an older request %s after a newer selection succeeds', async (outcome) => {
    let resolveOld!: (value: unknown) => void
    let rejectOld!: (reason: unknown) => void
    const fetchMock = vi.fn()
      .mockImplementationOnce(() => new Promise((resolve, reject) => { resolveOld = resolve; rejectOld = reject }))
      .mockResolvedValue({ ok: true, json: async () => [activities[1]] })
    vi.stubGlobal('fetch', fetchMock)
    render(<Library />)
    const oldSignal = fetchMock.mock.calls[0][1].signal as AbortSignal
    fireEvent.change(screen.getByRole('combobox', { name: 'Level' }), { target: { value: 'B1' } })
    expect(await screen.findByRole('link', { name: /My discussion/ })).toBeInTheDocument()
    expect(oldSignal.aborted).toBe(true)
    await act(async () => {
      if (outcome === 'success') resolveOld({ ok: true, json: async () => [activities[0]] })
      else rejectOld(new Error('Old failure'))
    })
    expect(screen.getByRole('link', { name: /My discussion/ })).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /Airport plans/ })).not.toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })
})
