import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import TestResultsModal from '../TestResultsModal'

describe('TestResultsModal', () => {
  beforeEach(() => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          tests: [
            { tool: 'TextProcessorTool', category: 'uppercase', query: 'uppercase "hello"', result: 'HELLO' },
            { tool: 'CalculatorTool', category: 'arithmetic', query: 'calculate 2+2', result: '4' }
          ]
        })
      })
    )
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  test('renders sample tool results from the JSON data source', async () => {
    render(<TestResultsModal isOpen={true} onClose={() => {}} />)

    expect(screen.getByText('Test Results')).toBeTruthy()
    await waitFor(() => {
      expect(screen.getByText('TextProcessorTool')).toBeTruthy()
    })

    expect(screen.getByText('uppercase')).toBeTruthy()
    expect(screen.getByText('uppercase "hello"')).toBeTruthy()
    expect(screen.getByText('HELLO')).toBeTruthy()
    expect(screen.getByText('CalculatorTool')).toBeTruthy()
  })
})
