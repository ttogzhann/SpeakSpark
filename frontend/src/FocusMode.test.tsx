import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'

const activity = { id: 'custom-focus', title: 'Focus task', level: 'B1', topic: 'Work', type: 'Speaking Challenge', prompt: 'Speak clearly.\nKeep going.', is_builtin: false, instructions: ['Use examples'], follow_up_questions: ['What happens next?'] }
afterEach(() => { cleanup(); vi.unstubAllGlobals(); window.history.replaceState(null, '', '/') })

function api(record = activity) {
  const mock = vi.fn().mockImplementation(async (url: string) => ({ ok: true, json: async () => url === '/api/favorites' ? [record] : url.startsWith('/api/random-activities') ? { status: 'selected', activity: record } : record }))
  vi.stubGlobal('fetch', mock)
  return mock
}

describe('Focus Mode', () => {
  it.each([true, false])('presents a detail activity built-in=%s and restores source focus without requests', async (isBuiltin) => {
    const mock = api({ ...activity, is_builtin: isBuiltin })
    window.history.replaceState(null, '', '/#/library/custom-focus')
    render(<App />)
    const enter = await screen.findByRole('button', { name: 'Enter Focus Mode' })
    enter.focus()
    const calls = mock.mock.calls.length
    fireEvent.click(enter)
    const presentation = screen.getByRole('main', { name: 'Focus Mode' })
    expect(within(presentation).getByRole('heading', { name: activity.title })).toBeInTheDocument()
    expect(within(presentation).getByText(/Speak clearly/).textContent).toBe(activity.prompt)
    expect(within(presentation).getByRole('heading', { name: 'Supporting prompts' })).toBeInTheDocument()
    expect(within(presentation).getByText('Use examples')).toBeInTheDocument()
    expect(screen.queryByRole('navigation')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Remove from Favorites/ })).not.toBeInTheDocument()
    expect(screen.getAllByRole('button')).toHaveLength(1)
    expect(screen.getByRole('button', { name: 'Exit Focus Mode' })).toHaveFocus()
    fireEvent.click(screen.getByRole('button', { name: 'Exit Focus Mode' }))
    await waitFor(() => expect(enter).toHaveFocus())
    expect(screen.getByRole('navigation')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Remove from Favorites/ })).toBeInTheDocument()
    expect(mock).toHaveBeenCalledTimes(calls)
    expect(window.location.hash).toBe('#/library/custom-focus')
  })

  it('preserves Surprise Me filters and selection across Escape exit without drawing again', async () => {
    const mock = api()
    window.history.replaceState(null, '', '/#/surprise-me')
    render(<App />)
    fireEvent.change(screen.getByLabelText('Level (required)'), { target: { value: 'B1' } })
    fireEvent.change(screen.getByLabelText('Activity type (optional)'), { target: { value: 'Speaking Challenges' } })
    fireEvent.click(screen.getByRole('button', { name: 'Surprise Me' }))
    const enter = await screen.findByRole('button', { name: 'Enter Focus Mode' })
    enter.focus()
    const calls = mock.mock.calls.length
    fireEvent.click(enter)
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Next' })).not.toBeInTheDocument()
    fireEvent.keyDown(window, { key: 'Escape' })
    await waitFor(() => expect(enter).toHaveFocus())
    expect(screen.getByLabelText('Level (required)')).toHaveValue('B1')
    expect(screen.getByLabelText('Activity type (optional)')).toHaveValue('Speaking Challenges')
    expect(screen.getByRole('heading', { name: activity.title })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Next' })).toBeInTheDocument()
    expect(mock).toHaveBeenCalledTimes(calls)
  })
})
