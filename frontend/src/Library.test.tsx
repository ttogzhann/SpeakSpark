import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
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
})
