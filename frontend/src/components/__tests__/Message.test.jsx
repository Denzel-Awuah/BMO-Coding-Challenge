import React from 'react'
import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Message from '../Message'

describe('Message', ()=>{
  test('renders loading dots when loading', ()=>{
    const m = { role: 'assistant', loading: true }
    render(<Message m={m} />)
    expect(screen.getByText((content, node) => node.classList && node.classList.contains('loading-dots'))).toBeTruthy()
  })

  test('renders meta details when provided', ()=>{
    const m = { role:'assistant', text:'Result', meta: { tools:['CalculatorTool'], steps:['a','b'], timestamp: new Date().toISOString() } }
    render(<Message m={m} />)
    expect(screen.getByText(/Tools:/)).toBeTruthy()
    expect(screen.getByText(/CalculatorTool/)).toBeTruthy()
    // steps should be in the document (even if within details)
    expect(screen.getByText('a')).toBeTruthy()
    expect(screen.getByText('b')).toBeTruthy()
  })
})
