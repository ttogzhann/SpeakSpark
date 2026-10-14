import '@testing-library/jest-dom/vitest'
import { afterEach, beforeEach, vi } from 'vitest'

const unmockedFetch = vi.fn(() => Promise.reject(new Error('Unexpected unmocked fetch in component test')))
beforeEach(() => {
  unmockedFetch.mockClear()
  vi.stubGlobal('fetch', unmockedFetch)
})
afterEach(() => {
  vi.unstubAllGlobals()
  if (unmockedFetch.mock.calls.length) throw new Error('Component tests must mock every backend request')
})
