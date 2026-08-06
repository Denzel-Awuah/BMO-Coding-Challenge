import React from 'react'
import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { within } from '@testing-library/dom'
import ChatWindow from '../ChatWindow'

describe('ChatWindow', ()=>{
  test('renders messages and composer', ()=>{
    const messages = [ {role:'user', text:'Submit a task'}, {role:'assistant', text:'Connected'} ]
    const props = {
      task: '', setTask: ()=>{}, onSubmit: ()=>{}, loading: false, onClear: ()=>{}
    }
    const { container } = render(<ChatWindow messages={messages} {...props} />)
    expect(screen.getByText('Agent Chat')).toBeTruthy()
    const messagesDiv = container.querySelector('#messages')
    expect(messagesDiv).toBeTruthy()
    const messagesWithin = within(messagesDiv)
    expect(messagesWithin.getByText('Submit a task')).toBeTruthy()
    expect(messagesWithin.getByText('Connected')).toBeTruthy()
    // composer textarea placeholder
    expect(screen.getByPlaceholderText(/Ask the agent/i)).toBeTruthy()
  })
})
