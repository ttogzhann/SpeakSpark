import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import type { Activity } from './activity'

afterEach(() => { cleanup(); vi.unstubAllGlobals(); window.history.replaceState(null, '', '/') })

describe('Saved custom activity changes across views', () => {
  it('keeps confirmed Favorite content in sync after editing, cancellation and deletion', async () => {
    let record: Activity | undefined = { id: 'custom-saved-flow', title: 'Saved original', level: 'A2', topic: 'Travel', type: 'Conversation Card', prompt: 'Discuss a trip.', is_builtin: false }
    const mock = vi.fn().mockImplementation(async (url: string, options?: RequestInit) => {
      if (options?.method === 'PUT') {
        record = { ...record!, ...JSON.parse(options.body as string) }
        return { status: 200, json: async () => record }
      }
      if (options?.method === 'DELETE') { record = undefined; return { status: 204 } }
      return { ok: true, json: async () => url.startsWith('/api/activities/') ? record : record ? [{ ...record }] : [] }
    })
    vi.stubGlobal('fetch', mock)
    window.history.replaceState(null, '', '/#/my-activities')
    render(<App />)
    fireEvent.click(await screen.findByRole('button', { name: 'Edit Saved original' }))
    fireEvent.change(screen.getByLabelText('Title'), { target: { value: 'Saved updated' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }))
    await screen.findByRole('link', { name: /Saved updated/ })
    fireEvent.click(screen.getByRole('link', { name: 'Favorites' }))
    await screen.findByRole('heading', { name: 'Favorites', level: 1 })
    expect(await screen.findByRole('link', { name: /Saved updated/ })).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /Saved original/ })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('link', { name: 'My Activities' }))
    await screen.findByRole('heading', { name: 'My Activities', level: 1 })
    fireEvent.click(await screen.findByRole('button', { name: 'Delete Saved updated' }))
    fireEvent.click(screen.getByRole('button', { name: 'Cancel deletion' }))
    expect(mock.mock.calls.filter(([, options]) => options?.method === 'DELETE')).toHaveLength(0)
    expect(screen.getByRole('button', { name: 'Remove from Favorites: Saved updated' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Delete Saved updated' }))
    fireEvent.click(screen.getByRole('button', { name: 'Confirm delete' }))
    await screen.findByText(/No custom activities yet/)
    fireEvent.click(screen.getByRole('link', { name: 'Favorites' }))
    await screen.findByRole('heading', { name: 'Favorites', level: 1 })
    expect(await screen.findByText(/No Favorites yet/)).toBeInTheDocument()
    await waitFor(() => expect(mock.mock.calls.filter(([, options]) => options?.method === 'DELETE')).toHaveLength(1))
  })
})
