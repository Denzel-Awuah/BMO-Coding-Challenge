import React from 'react'
import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Sidebar from '../Sidebar'

describe('Sidebar', ()=>{
  test('renders title, section headings and history task labels', ()=>{
    const history = [
      {id:1, task:'Test task', timestamp: new Date().toISOString(), tools:['TextProcessorTool']},
      {id:2, task:'Another task', timestamp: new Date().toISOString(), tools:['CalculatorTool']},
    ]
    render(<Sidebar history={history} selected={1} onSelect={()=>{}} />)

    // Header branding
    expect(screen.getByText('BMO Agent Simulator')).toBeTruthy()
    expect(screen.getByText('Tool Usage')).toBeTruthy()
    expect(screen.getByText('Chats')).toBeTruthy()

    // History task text is visible; tool tags are intentionally NOT shown in the sidebar
    expect(screen.getByText('Test task')).toBeTruthy()
    expect(screen.getByText('Another task')).toBeTruthy()

    // Tool names must NOT appear in the sidebar (they are shown only in the ChatWindow)
    expect(screen.queryByText(/TextProcessorTool/)).toBeNull()
    expect(screen.queryByText(/CalculatorTool/)).toBeNull()
  })
})
