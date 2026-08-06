import React from 'react'
import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Sidebar from '../Sidebar'

describe('Sidebar', ()=>{
  test('renders title and history items', ()=>{
    const history = [ {id:1, task:'Test task', timestamp: new Date().toISOString(), tools:['TextProcessorTool']} ]
    render(<Sidebar history={history} selected={1} onSelect={()=>{}} />)
    expect(screen.getByText('BMO Agent Simulator')).toBeTruthy()
    expect(screen.getByText('Tool Usage')).toBeTruthy()
    expect(screen.getByText('Test task')).toBeTruthy()
    expect(screen.getByText(/TextProcessorTool/)).toBeTruthy()
  })
})
