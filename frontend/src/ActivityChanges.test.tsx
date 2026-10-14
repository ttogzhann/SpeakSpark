import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import ActivityForm from './ActivityForm'
import MyActivities from './MyActivities'
import type { Activity } from './activity'

const record: Activity = { id: 'custom-edit', title: 'Original task', level: 'B1', topic: 'Work', type: 'Role-play', prompt: 'Original prompt', is_builtin: false, roles: [{ participant: 'Tutor', objective: 'Ask for help' }], instructions: ['Take turns'], useful_phrases: ['Please help'] }
afterEach(() => { cleanup(); vi.unstubAllGlobals() })

describe('Custom activity changes', () => {
  it('prefills required and optional content, cancels without mutation and rejects built-in forms', async () => {
    const mock = vi.fn().mockResolvedValue({ ok: true, json: async () => [record, { ...record, id: 'builtin-one', title: 'Built-in', is_builtin: true }] })
    vi.stubGlobal('fetch', mock)
    const view = render(<MyActivities />)
    fireEvent.click(await screen.findByRole('button', { name: 'Edit Original task' }))
    expect(screen.getByLabelText('Title')).toHaveValue(record.title)
    expect(screen.getByLabelText('Speaking prompt')).toHaveValue(record.prompt)
    expect(screen.getByLabelText('Participant 1')).toHaveValue('Tutor')
    expect(screen.getByLabelText('Objective 1')).toHaveValue('Ask for help')
    expect(screen.getByLabelText('Instructions (optional)')).toHaveValue('Take turns')
    expect(screen.getByLabelText('Useful phrases (optional)')).toHaveValue('Please help')
    fireEvent.click(screen.getByRole('button', { name: 'Cancel editing' }))
    expect(screen.getByLabelText('Title')).toHaveValue('')
    expect(screen.queryByRole('button', { name: 'Edit Built-in' })).not.toBeInTheDocument()
    expect(mock.mock.calls.filter(([, options]) => options?.method)).toHaveLength(0)
    view.unmount()
    render(<ActivityForm initialActivity={{ ...record, is_builtin: true }} onCreated={vi.fn()} />)
    expect(screen.getByRole('alert')).toHaveTextContent('read-only')
    expect(screen.queryByRole('button', { name: 'Save changes' })).not.toBeInTheDocument()
  })

  it('validates edits, preserves rejected input, then sends a PUT and updates the list', async () => {
    const mock = vi.fn().mockResolvedValue({ ok: true, json: async () => [record] })
    vi.stubGlobal('fetch', mock)
    render(<MyActivities />)
    fireEvent.click(await screen.findByRole('button', { name: 'Edit Original task' }))
    fireEvent.change(screen.getByLabelText('Title'), { target: { value: ' ' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }))
    expect(screen.getByRole('alert')).toHaveTextContent('Enter a title')
    expect(mock).toHaveBeenCalledTimes(1)
    fireEvent.change(screen.getByLabelText('Title'), { target: { value: 'Updated task' } })
    mock.mockResolvedValueOnce({ status: 422 })
    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('backend rejected')
    expect(screen.getByLabelText('Title')).toHaveValue('Updated task')
    expect(screen.getByRole('link', { name: /Original task/ })).toBeInTheDocument()
    mock.mockResolvedValueOnce({ status: 200, json: async () => ({ ...record, title: 'Updated task' }) })
    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }))
    expect(await screen.findByRole('link', { name: /Updated task/ })).toBeInTheDocument()
    expect(mock).toHaveBeenLastCalledWith('/api/activities/custom-edit', expect.objectContaining({ method: 'PUT' }))
  })

  it('requires named deletion confirmation, cancels without DELETE and preserves failed deletions', async () => {
    const mock = vi.fn().mockResolvedValue({ ok: true, json: async () => [record] })
    vi.stubGlobal('fetch', mock)
    render(<MyActivities />)
    fireEvent.click(await screen.findByRole('button', { name: 'Delete Original task' }))
    expect(screen.getByRole('region', { name: 'Delete confirmation' })).toHaveTextContent('Original task')
    fireEvent.click(screen.getByRole('button', { name: 'Cancel deletion' }))
    expect(mock.mock.calls.filter(([, options]) => options?.method === 'DELETE')).toHaveLength(0)
    fireEvent.click(screen.getByRole('button', { name: 'Delete Original task' }))
    mock.mockRejectedValueOnce(new Error('Offline'))
    fireEvent.click(screen.getByRole('button', { name: 'Confirm delete' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Could not confirm deletion')
    expect(screen.getByRole('link', { name: /Original task/ })).toBeInTheDocument()
    let resolveDelete!: (value: unknown) => void
    mock.mockImplementationOnce(() => new Promise((resolve) => { resolveDelete = resolve }))
    fireEvent.click(screen.getByRole('button', { name: 'Confirm delete' }))
    const pending = screen.getByRole('button', { name: 'Deleting activity...' })
    expect(pending).toBeDisabled()
    fireEvent.click(pending)
    expect(mock.mock.calls.filter(([, options]) => options?.method === 'DELETE')).toHaveLength(2)
    await act(async () => resolveDelete({ status: 204 }))
    expect(await screen.findByText(/No custom activities yet/)).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /Original task/ })).not.toBeInTheDocument()
  })
})
