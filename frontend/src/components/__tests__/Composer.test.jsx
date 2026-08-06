import React from 'react'
import { describe, test, expect, vi } from 'vitest'
import { render, screen, fireEvent, within } from '@testing-library/react'
import Composer from '../Composer'

describe('Composer', ()=>{
  test('renders textarea and buttons', ()=>{
    const { container } = render(<Composer task="" setTask={()=>{}} onSubmit={()=>{}} loading={false} onClear={()=>{}} />)
    const c = within(container)
    expect(c.getByPlaceholderText(/Ask the agent/i)).toBeTruthy()
    expect(c.getByRole('button', { name: /Send/i })).toBeTruthy()
    expect(c.getByRole('button', { name: /Clear/i })).toBeTruthy()
  })

  test('calls setTask on textarea change', ()=>{
    const setTask = vi.fn()
    const { container } = render(<Composer task="" setTask={setTask} onSubmit={()=>{}} loading={false} onClear={()=>{}} />)
    const c = within(container)
    const ta = c.getByPlaceholderText(/Ask the agent/i)
    fireEvent.change(ta, { target: { value: 'Hello' } })
    expect(setTask).toHaveBeenCalled()
  })

  test('calls onSubmit when form submitted', ()=>{
    const onSubmit = vi.fn((e)=>e && e.preventDefault())
    const { container } = render(<Composer task="hi" setTask={()=>{}} onSubmit={onSubmit} loading={false} onClear={()=>{}} />)
    const c = within(container)
    const btn = c.getByRole('button', { name: /Send/i })
    fireEvent.click(btn)
    expect(onSubmit).toHaveBeenCalled()
  })

  test('calls onClear when clear clicked', ()=>{
    const onClear = vi.fn()
    const { container } = render(<Composer task="" setTask={()=>{}} onSubmit={()=>{}} loading={false} onClear={onClear} />)
    const c = within(container)
    const clear = c.getByRole('button', { name: /Clear/i })
    fireEvent.click(clear)
    expect(onClear).toHaveBeenCalled()
  })

  test('shows Thinking... when loading is true', ()=>{
    const { container } = render(<Composer task="" setTask={()=>{}} onSubmit={()=>{}} loading={true} onClear={()=>{}} />)
    const c = within(container)
    const btn = c.getByRole('button', { name: /Thinking.../i })
    expect(btn).toBeTruthy()
    expect(btn.disabled).toBe(true)
  })
})
