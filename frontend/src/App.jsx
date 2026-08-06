import React, { useEffect, useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'
import TestResultsModal from './components/TestResultsModal'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export default function App(){
  const [task, setTask] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState(null) // selected history id
  const [messages, setMessages] = useState([]) // current chat messages [{role, text}]
  const [showTestResults, setShowTestResults] = useState(false)

  useEffect(()=>{ fetchHistory() }, [])

  async function fetchHistory(){
    try{ const res = await fetch(`${API_BASE}/tasks`); const data = await res.json(); setHistory(data); if(data.length>0 && !selected){ setSelected(data[0].id); populateFromHistory(data[0]) } }catch(e){console.error(e)}
  }

  function populateFromHistory(item){
    setSelected(item.id)
    const msgs = [ {role:'user', text:item.task}, {role:'assistant', text: typeof item.output==='object'? JSON.stringify(item.output): String(item.output), meta:{tools:item.tools, steps:item.steps, timestamp:item.timestamp}} ]
    setMessages(msgs)
  }

  async function submit(e){
    e && e.preventDefault()
    if(!task.trim()) return
    setLoading(true)
    // clear current chat and show only the new user message (single request/response)
    const userMsg = {role:'user', text:task}
    // insert assistant placeholder with loading flag
    const placeholderAssistant = {role:'assistant', text:'', loading:true}
    setMessages([userMsg, placeholderAssistant])
    setSelected(null)
    try{
      // Stream endpoint returns Server-Sent-Events-like data over POST streaming
      const res = await fetch(`${API_BASE}/tasks/stream`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({task}) })
      if(!res.ok){ throw new Error(`Streaming request failed: ${res.status}`) }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      // local assistant message object we update progressively
      let assistantMsg = {role:'assistant', text:'', loading:true, meta:{steps:[]}}
      setMessages([userMsg, assistantMsg])

      while(true){
        const { done, value } = await reader.read()
        if(done) break
        buffer += decoder.decode(value, {stream:true})
        // SSE frames separated by double newlines
        const parts = buffer.split('\n\n')
        buffer = parts.pop() // remainder
        for(const part of parts){
          const lines = part.split('\n')
          for(const line of lines){
            if(line.startsWith('data:')){
              const jsonStr = line.replace(/^data:\s*/,'')
              try{
                const evt = JSON.parse(jsonStr)
                if(evt.type === 'step'){
                  assistantMsg.meta.steps = [...assistantMsg.meta.steps, evt.data]
                  // update assistant placeholder text to show latest step summary
                  assistantMsg.text = assistantMsg.meta.steps.join('\n')
                  setMessages([userMsg, {...assistantMsg}])
                } else if(evt.type === 'result'){
                  const result = evt.data
                  assistantMsg.loading = false
                  assistantMsg.text = typeof result.output === 'object' ? JSON.stringify(result.output) : String(result.output)
                  assistantMsg.meta.tools = result.tools
                  assistantMsg.meta.timestamp = result.timestamp
                  // merge accumulated steps (if backend didn't include them)
                  assistantMsg.meta.steps = assistantMsg.meta.steps

                  setMessages([userMsg, {...assistantMsg}])
                  // refresh history (stream endpoint persists result server-side)
                  await fetchHistory()
                  setTask('')
                  setSelected(result.id)
                }
              }catch(err){
                console.error('Failed to parse stream event', err)
              }
            }
          }
        }
      }

    }catch(err){ 
      console.error(err); 
      // replace placeholder with error message
      setMessages([userMsg, {role:'assistant', text:`Error: ${err.message || 'failed to get response from backend.'}`}])
      alert('Failed to submit task') 
    }
    finally{ setLoading(false) }
  }

  return (
    <div className="app-shell">
      <div className="app chat-app">
        <Sidebar history={history} selected={selected} onSelect={populateFromHistory} />
        <ChatWindow
          messages={messages}
          task={task}
          setTask={setTask}
          onSubmit={submit}
          loading={loading}
          onClear={()=>setTask('')}
          onShowTestResults={() => setShowTestResults(true)}
        />
      </div>
      <TestResultsModal isOpen={showTestResults} onClose={() => setShowTestResults(false)} />
    </div>
  )
}
