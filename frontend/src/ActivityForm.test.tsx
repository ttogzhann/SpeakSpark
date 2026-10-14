import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import ActivityForm from './ActivityForm'
import MyActivities from './MyActivities'

const custom = { id: 'custom-new', title: 'My new task', level: 'A2', topic: 'Travel', type: 'Conversation Card', prompt: 'Discuss travel.', is_builtin: false }
const change = (label: string, value: string) => fireEvent.change(screen.getByLabelText(label), { target: { value } })
function fill(type = 'Conversation Card') {
  change('Title', ' My new task ')
  change('Level', 'A2')
  change('Topic', 'Travel')
  change('Activity type', type)
  change('Speaking prompt', ' Discuss travel. ')
}
function submit() { fireEvent.click(screen.getByRole('button', { name: 'Create activity' })) }
afterEach(() => { cleanup(); vi.unstubAllGlobals() })

describe('Custom activity creation', () => {
  it('lists only backend custom records and their metadata', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => [{ ...custom, id: 'builtin-one', title: 'Builtin hidden', is_builtin: true }, custom] }))
    render(<MyActivities />)
    const list = await screen.findByRole('list', { name: 'Your custom activities' })
    expect(within(list).getAllByRole('listitem')).toHaveLength(1)
    expect(within(list).getByRole('link', { name: /My new task/ })).toHaveTextContent('A2')
    expect(screen.queryByText('Builtin hidden')).not.toBeInTheDocument()
  })

  it.each(['Conversation Card', 'Role-play', 'Speaking Challenge'])('submits schema-aligned %s guidance and confirmed creation', async (type) => {
    const mock = vi.fn().mockResolvedValue({ status: 201, json: async () => ({ ...custom, type }) })
    const created = vi.fn()
    vi.stubGlobal('fetch', mock)
    render(<ActivityForm onCreated={created} />)
    fill(type)
    if (type === 'Role-play') {
      change('Participant 1', ' Passenger '); change('Objective 1', ' Find a flight ')
      change('Useful phrases (optional)', ' Please help \n\n Thank you ')
      change('Instructions (optional)', ' Take turns ')
    } else {
      change(type === 'Conversation Card' ? 'Follow-up questions (optional)' : 'Supporting prompts (optional)', ' Why? \n\n When? ')
      if (type === 'Speaking Challenge') change('Instructions (optional)', ' Speak for a minute ')
    }
    submit()
    expect(await screen.findByText(/Activity saved/)).toBeInTheDocument()
    const payload = JSON.parse(mock.mock.calls[0][1].body)
    expect(payload).toEqual({ title: 'My new task', level: 'A2', topic: 'Travel', type, prompt: 'Discuss travel.', follow_up_questions: type === 'Role-play' ? [] : ['Why?', 'When?'], useful_phrases: type === 'Role-play' ? ['Please help', 'Thank you'] : [], roles: type === 'Role-play' ? [{ participant: 'Passenger', objective: 'Find a flight' }] : [], instructions: type === 'Conversation Card' ? [] : [type === 'Role-play' ? 'Take turns' : 'Speak for a minute'] })
    expect(mock.mock.calls[0][0]).toBe('/api/activities')
    expect(mock.mock.calls[0][1].method).toBe('POST')
    expect(created).toHaveBeenCalledTimes(1)
    expect(screen.getByLabelText('Title')).toHaveValue('')
  })

  it('normalizes blank optional fields and omits guidance from a previously selected type', async () => {
    const mock = vi.fn().mockResolvedValue({ status: 201, json: async () => custom })
    vi.stubGlobal('fetch', mock)
    render(<ActivityForm onCreated={vi.fn()} />)
    fill('Role-play')
    change('Useful phrases (optional)', 'Hidden after switching')
    change('Activity type', 'Conversation Card')
    change('Follow-up questions (optional)', ' \n\n ')
    submit()
    await screen.findByText(/Activity saved/)
    expect(JSON.parse(mock.mock.calls[0][1].body)).toMatchObject({ follow_up_questions: [], useful_phrases: [], roles: [], instructions: [] })
  })

  it('validates required whitespace and incomplete roles without sending a request', async () => {
    const mock = vi.fn()
    vi.stubGlobal('fetch', mock)
    render(<ActivityForm onCreated={vi.fn()} />)
    submit()
    expect(screen.getByRole('alert')).toHaveTextContent('Enter a title')
    fill('Role-play')
    change('Title', '  ')
    submit()
    expect(mock).not.toHaveBeenCalled()
    change('Title', 'Valid title')
    change('Participant 1', 'Passenger')
    submit()
    expect(screen.getByRole('alert')).toHaveTextContent('Complete both participant and objective')
    expect(mock).not.toHaveBeenCalled()
  })

  it.each([422, 500, 'network'])('preserves entered data and reports %s without false success', async (failure) => {
    vi.stubGlobal('fetch', failure === 'network' ? vi.fn().mockRejectedValue(new Error('Offline')) : vi.fn().mockResolvedValue({ status: failure }))
    render(<ActivityForm onCreated={vi.fn()} />)
    fill()
    submit()
    expect(await screen.findByRole('alert')).toHaveTextContent(failure === 422 ? 'backend rejected' : failure === 'network' ? 'could not confirm' : 'could not save')
    expect(screen.getByLabelText('Title')).toHaveValue(' My new task ')
    expect(screen.queryByText(/Activity saved/)).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Create activity' })).toBeEnabled()
  })

  it('prevents duplicate pending submissions and inserts the confirmed record exactly once', async () => {
    let resolveSave!: (value: unknown) => void
    const mock = vi.fn().mockImplementation((_: string, options?: RequestInit) => options?.method === 'POST' ? new Promise((resolve) => { resolveSave = resolve }) : Promise.resolve({ ok: true, json: async () => [] }))
    vi.stubGlobal('fetch', mock)
    render(<MyActivities />)
    await screen.findByText(/No custom activities yet/)
    fill()
    submit()
    const pending = screen.getByRole('button', { name: 'Saving activity...' })
    expect(pending).toBeDisabled()
    fireEvent.click(pending)
    expect(mock.mock.calls.filter(([, options]) => options?.method === 'POST')).toHaveLength(1)
    await act(async () => resolveSave({ status: 201, json: async () => custom }))
    expect(await screen.findByRole('link', { name: /My new task/ })).toBeInTheDocument()
    expect(screen.getAllByRole('listitem')).toHaveLength(1)
    mock.mockResolvedValueOnce({ ok: false })
    fireEvent.click(screen.getByRole('button', { name: 'Refresh My Activities' }))
    await screen.findByRole('alert')
    expect(screen.getByText(/Activity saved/)).toBeInTheDocument()
    expect(screen.getByLabelText('Title')).toHaveValue('')
  })

  it('distinguishes list loading, empty and failure with retry', async () => {
    const mock = vi.fn().mockRejectedValue(new Error('Offline'))
    vi.stubGlobal('fetch', mock)
    render(<MyActivities />)
    expect(screen.getByRole('status')).toHaveTextContent('Loading your activities')
    expect(await screen.findByRole('alert')).toHaveTextContent("couldn't load your activities")
    mock.mockResolvedValueOnce({ ok: true, json: async () => [] })
    fireEvent.click(screen.getByRole('button', { name: 'Refresh My Activities' }))
    expect(await screen.findByText(/No custom activities yet/)).toBeInTheDocument()
  })
})
