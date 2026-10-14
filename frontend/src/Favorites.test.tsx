import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import Favorites, { FavoriteButton, FavoritesProvider } from './Favorites'
import type { Activity } from './activity'

const records: Activity[] = [
  { id: 'builtin-save', title: 'Built-in task', level: 'A2', topic: 'Travel', type: 'Role-play', prompt: 'Ask for directions.', is_builtin: true },
  { id: 'custom-save', title: 'Custom task', level: 'B1', topic: 'Work', type: 'Conversation Card', prompt: 'Discuss work.', is_builtin: false },
]
beforeEach(() => window.history.replaceState(null, '', '/'))
afterEach(() => { cleanup(); vi.unstubAllGlobals() })

function backend(initial: Activity[] = []) {
  let saved = [...initial]
  const mock = vi.fn().mockImplementation(async (url: string, options?: RequestInit) => {
    if (options?.method === 'POST') {
      const id = JSON.parse(options.body as string).activity_id
      saved = [...saved.filter((item) => item.id !== id), records.find((item) => item.id === id)!]
      return { ok: true, status: 201 }
    }
    if (options?.method === 'DELETE') {
      saved = saved.filter((item) => item.id !== url.split('/').at(-1))
      return { ok: true }
    }
    return { ok: true, json: async () => url === '/api/favorites' ? [...saved] : url.startsWith('/api/activities/') ? records.find((item) => item.id === url.split('/').at(-1)) : records }
  })
  vi.stubGlobal('fetch', mock)
  return mock
}

function button(title: string, saved = false) {
  return screen.getAllByRole('button', { name: `${saved ? 'Remove from' : 'Add to'} Favorites: ${title}` })[0]
}

describe('Favorites', () => {
  it.each(records)('keeps Library, detail and Favorites consistent for $id and persists across remount', async (activity) => {
    const mock = backend()
    const view = render(<App />)
    await screen.findByRole('link', { name: new RegExp(activity.title) })
    await waitFor(() => expect(button(activity.title)).toBeEnabled())
    fireEvent.click(button(activity.title))
    await waitFor(() => expect(button(activity.title, true)).toHaveAttribute('aria-pressed', 'true'))
    expect(mock).toHaveBeenCalledWith('/api/favorites', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ activity_id: activity.id }) })
    fireEvent.click(screen.getByRole('link', { name: new RegExp(activity.title) }))
    await screen.findByText(activity.prompt)
    expect(button(activity.title, true)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('link', { name: 'Favorites' }))
    const list = await screen.findByRole('list', { name: 'Favorite activities' })
    expect(within(list).getByRole('link', { name: new RegExp(activity.title) })).toHaveTextContent(activity.level)
    expect(within(list).getByRole('link', { name: new RegExp(activity.title) })).toHaveTextContent(activity.topic)
    view.unmount()
    render(<App />)
    await screen.findByRole('list', { name: 'Favorite activities' })
    fireEvent.click(button(activity.title, true))
    expect(await screen.findByText(/No Favorites yet/)).toBeInTheDocument()
    expect(mock).toHaveBeenCalledWith(`/api/favorites/${activity.id}`, { method: 'DELETE' })
    fireEvent.click(screen.getByRole('link', { name: 'Library' }))
    await screen.findByRole('link', { name: new RegExp(activity.title) })
    expect(button(activity.title)).toHaveAttribute('aria-pressed', 'false')
  })

  it('shows loading without false unsaved status or an empty state', () => {
    vi.stubGlobal('fetch', vi.fn().mockReturnValue(new Promise(() => {})))
    render(<FavoritesProvider><Favorites /><FavoriteButton activity={records[0]} /></FavoritesProvider>)
    expect(screen.getByRole('status')).toHaveTextContent('Loading Favorites')
    expect(screen.getByRole('button', { name: /Loading Favorites.*Built-in task/ })).toBeDisabled()
    expect(screen.queryByRole('button', { name: /Add to Favorites/ })).not.toBeInTheDocument()
    expect(screen.queryByText(/No Favorites yet/)).not.toBeInTheDocument()
  })

  it.each(['http', 'network'])('shows a truthful %s membership failure and retry', async (failure) => {
    const mock = failure === 'http' ? vi.fn().mockResolvedValue({ ok: false }) : vi.fn().mockRejectedValue(new Error('Offline'))
    vi.stubGlobal('fetch', mock)
    render(<FavoritesProvider><Favorites /><FavoriteButton activity={records[0]} /></FavoritesProvider>)
    expect(await screen.findByRole('alert')).toHaveTextContent("couldn't load Favorites")
    expect(screen.getByRole('button', { name: /Favorite status unavailable/ })).toBeDisabled()
    expect(screen.queryByText(/No Favorites yet/)).not.toBeInTheDocument()
    mock.mockResolvedValue({ ok: true, json: async () => [records[0]] })
    fireEvent.click(screen.getByRole('button', { name: 'Retry Favorites' }))
    await waitFor(() => expect(button(records[0].title, true)).toBeEnabled())
  })

  it.each(['add', 'remove'])('prevents duplicate pending %s and retains membership after failure', async (action) => {
    const mock = backend(action === 'remove' ? [records[0]] : [])
    render(<FavoritesProvider><FavoriteButton activity={records[0]} /></FavoritesProvider>)
    await waitFor(() => expect(button(records[0].title, action === 'remove')).toBeEnabled())
    let rejectWrite!: (error: unknown) => void
    mock.mockImplementationOnce(() => new Promise((_, reject) => { rejectWrite = reject }))
    fireEvent.click(button(records[0].title, action === 'remove'))
    const busy = screen.getByRole('button', { name: /Updating Favorite/ })
    expect(busy).toBeDisabled()
    fireEvent.click(busy)
    expect(mock.mock.calls.filter(([, options]) => options?.method)).toHaveLength(1)
    await act(async () => rejectWrite(new Error('Write failed')))
    expect(screen.getByRole('alert')).toHaveTextContent("Couldn't update this Favorite")
    expect(button(records[0].title, action === 'remove')).toBeEnabled()
  })

  it('refreshes backend data after a saved custom activity disappears', async () => {
    const mock = backend([records[1]])
    render(<FavoritesProvider><Favorites /></FavoritesProvider>)
    await screen.findByRole('link', { name: /Custom task/ })
    mock.mockResolvedValueOnce({ ok: true, json: async () => [] })
    fireEvent.click(screen.getByRole('button', { name: 'Refresh Favorites' }))
    expect(await screen.findByText(/No Favorites yet/)).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /Custom task/ })).not.toBeInTheDocument()
  })

  it('ignores an older list response after a newer load and confirmed mutation', async () => {
    let resolveOld!: (value: unknown) => void
    const mock = backend()
    mock.mockImplementationOnce(() => new Promise((resolve) => { resolveOld = resolve }))
    render(<FavoritesProvider><Favorites /><FavoriteButton activity={records[0]} /></FavoritesProvider>)
    await waitFor(() => expect(button(records[0].title)).toBeEnabled())
    fireEvent.click(button(records[0].title))
    await waitFor(() => expect(button(records[0].title, true)).toBeEnabled())
    await act(async () => resolveOld({ ok: true, json: async () => [] }))
    expect(button(records[0].title, true)).toHaveAttribute('aria-pressed', 'true')
  })
})
