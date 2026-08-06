import React from 'react'
import { describe, test, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import Sidebar from '../Sidebar'

describe('Sidebar interactions', ()=>{
  test('shows empty state when no history', ()=>{
    render(<Sidebar history={[]} selected={null} onSelect={()=>{}} />)
    expect(screen.getByText(/No history yet/i)).toBeTruthy()
  })

  test('clicking history calls onSelect with item', ()=>{
    const item = { id: '1', task: 'Task One', timestamp: new Date().toISOString(), tools:['TextProcessorTool'] }
    const onSelect = vi.fn()
    render(<Sidebar history={[item]} selected={null} onSelect={onSelect} />)
    const row = screen.getByText('Task One')
    fireEvent.click(row)
    expect(onSelect).toHaveBeenCalledWith(item)
  })

  test('applies active class when selected', ()=>{
    const item = { id: '1', task: 'Active Task', timestamp: new Date().toISOString(), tools:['TextProcessorTool'] }
    const { container } = render(<Sidebar history={[item]} selected={'1'} onSelect={()=>{}} />)
    const row = container.querySelector('.history-row')
    expect(row.classList.contains('active')).toBe(true)
  })
})
