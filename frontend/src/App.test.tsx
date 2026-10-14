import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'

const sections = [
  ['Library', '/library'],
  ['Surprise Me', '/surprise-me'],
  ['Favorites', '/favorites'],
  ['My Activities', '/my-activities'],
] as const

beforeEach(() => {
  window.history.replaceState(null, '', '/')
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => [] }))
})
afterEach(() => { cleanup(); vi.unstubAllGlobals() })

describe('App navigation', () => {
  it('opens Library at the base URL with exactly the four approved sections', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: 'Library', level: 1 })).toBeInTheDocument()
    const navigation = screen.getByRole('navigation', { name: 'Main navigation' })
    expect(within(navigation).getAllByRole('link')).toHaveLength(4)
    for (const [title, path] of sections) {
      expect(within(navigation).getByRole('link', { name: title })).toHaveAttribute('href', `#${path}`)
    }
    expect(screen.getByRole('link', { name: 'Library' })).toHaveAttribute('aria-current', 'page')
  })

  it.each(sections)('opens %s directly and after remounting at the same URL', (title, path) => {
    window.history.replaceState(null, '', `/#${path}`)
    const view = render(<App />)
    expect(screen.getByRole('heading', { name: title })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: title })).toHaveAttribute('aria-current', 'page')
    view.unmount()
    render(<App />)
    expect(screen.getByRole('heading', { name: title })).toBeInTheDocument()
  })

  it('follows native section links and moves the current-page indication', async () => {
    render(<App />)
    for (const [title, path] of sections.slice(1)) {
      fireEvent.click(screen.getByRole('link', { name: title }))
      expect(await screen.findByRole('heading', { name: title })).toBeInTheDocument()
      expect(window.location.hash).toBe(`#${path}`)
      expect(document.querySelectorAll('[aria-current="page"]')).toHaveLength(1)
      expect(screen.getByRole('link', { name: title })).toHaveAttribute('aria-current', 'page')
    }
  })

  it('updates the section when the browser restores a hash from history', () => {
    render(<App />)
    for (const [title, path] of [sections[2], sections[0], sections[2]]) {
      act(() => {
        window.history.replaceState(null, '', `/#${path}`)
        window.dispatchEvent(new HashChangeEvent('hashchange'))
      })
      expect(screen.getByRole('heading', { name: title })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: title })).toHaveAttribute('aria-current', 'page')
    }
  })
})
