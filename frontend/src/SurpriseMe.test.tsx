import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import SurpriseMe from './SurpriseMe'

const activity = { id: 'custom-random', title: 'Random task', level: 'A2', topic: 'Travel', type: 'Role-play', prompt: 'Ask for help', is_builtin: false, roles: [{ participant: 'Passenger', objective: 'Find the gate' }] }
const level = (value: string) => fireEvent.change(screen.getByLabelText('Level (required)'), { target: { value } })
afterEach(() => { cleanup(); vi.unstubAllGlobals() })

describe('Surprise Me', () => {
  it('requires a level, sends approved filters, shows returned guidance, and explicitly restarts exhaustion', async () => {
    const mock = vi.fn().mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'selected', activity }) }).mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'exhausted', activity: null }) }).mockResolvedValue({ ok: true, json: async () => ({ status: 'selected', activity }) })
    vi.stubGlobal('fetch', mock)
    render(<SurpriseMe />)
    const start = screen.getByRole('button', { name: 'Surprise Me' })
    expect(start).toBeDisabled()
    fireEvent.click(start)
    expect(mock).not.toHaveBeenCalled()
    level('A2')
    fireEvent.change(screen.getByLabelText('Activity type (optional)'), { target: { value: 'Role-play Scenarios' } })
    fireEvent.click(start)
    expect(await screen.findByRole('heading', { name: activity.title })).toBeInTheDocument()
    expect(screen.getByText('Find the gate')).toBeInTheDocument()
    expect(mock).toHaveBeenLastCalledWith('/api/random-activities/next?level=A2&type=Role-play+Scenarios', { method: 'POST' })
    fireEvent.click(screen.getByRole('button', { name: 'Next' }))
    expect(await screen.findByText(/seen every matching activity/)).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: activity.title })).not.toBeInTheDocument()
    expect(mock).toHaveBeenCalledTimes(2)
    fireEvent.click(screen.getByRole('button', { name: 'Restart cycle' }))
    await screen.findByRole('heading', { name: activity.title })
    expect(mock).toHaveBeenCalledTimes(3)
  })

  it.each(['success', 'error'])('prevents concurrent requests and ignores stale %s after changing filters', async (outcome) => {
    let resolveOld!: (value: unknown) => void
    let rejectOld!: (error: unknown) => void
    const mock = vi.fn().mockImplementationOnce(() => new Promise((resolve, reject) => { resolveOld = resolve; rejectOld = reject })).mockResolvedValue({ ok: true, json: async () => ({ status: 'no_matches', activity: null }) })
    vi.stubGlobal('fetch', mock)
    render(<SurpriseMe />)
    level('A2')
    fireEvent.click(screen.getByRole('button', { name: 'Surprise Me' }))
    fireEvent.click(screen.getByRole('button', { name: 'Selecting activity...' }))
    level('B2')
    expect(mock).toHaveBeenCalledTimes(1)
    expect(screen.getByRole('button', { name: 'Selecting activity...' })).toBeDisabled()
    await act(async () => outcome === 'success' ? resolveOld({ ok: true, json: async () => ({ status: 'selected', activity }) }) : rejectOld(new Error('Old failure')))
    expect(screen.queryByRole('heading', { name: activity.title })).not.toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Surprise Me' }))
    expect(await screen.findByText(/No activities match these filters/)).toBeInTheDocument()
    expect(mock).toHaveBeenLastCalledWith('/api/random-activities/next?level=B2', { method: 'POST' })
  })

  it.each(['http', 'network'])('shows %s failure with manual retry and no stale activity', async (failure) => {
    const mock = vi.fn().mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'selected', activity }) })
    if (failure === 'http') mock.mockResolvedValueOnce({ ok: false })
    else mock.mockRejectedValueOnce(new Error('Offline'))
    vi.stubGlobal('fetch', mock)
    render(<SurpriseMe />)
    level('A2')
    fireEvent.click(screen.getByRole('button', { name: 'Surprise Me' }))
    await screen.findByRole('heading', { name: activity.title })
    fireEvent.click(screen.getByRole('button', { name: 'Next' }))
    expect(await screen.findByRole('alert')).toHaveTextContent("couldn't confirm the selection")
    expect(screen.queryByRole('heading', { name: activity.title })).not.toBeInTheDocument()
    expect(mock).toHaveBeenCalledTimes(2)
    expect(screen.getByRole('button', { name: 'Surprise Me' })).toBeEnabled()
  })
})
