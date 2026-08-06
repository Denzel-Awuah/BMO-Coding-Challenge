import React, { useEffect, useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export default function App(){
  const [task, setTask] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState(null) // selected history id
  const [messages, setMessages] = useState([]) // current chat messages [{role, text}]

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
      const res = await fetch(`${API_BASE}/tasks`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({task}) })
      const data = await res.json()
      const assistantMsg = {role:'assistant', text: typeof data.output==='object'? JSON.stringify(data.output): String(data.output), meta:{tools:data.tools, steps:data.steps, timestamp:data.timestamp}}
      setMessages([userMsg, assistantMsg])
      await fetchHistory()
      setTask('')
      setSelected(data.id)
    }catch(err){ 
      console.error(err); 
      // replace placeholder with error message
      setMessages([userMsg, {role:'assistant', text:'Error: failed to get response from backend.'}])
      alert('Failed to submit task') 
    }
    finally{ setLoading(false) }
  }

  return (
    <div className="app chat-app">
      <Sidebar history={history} selected={selected} onSelect={populateFromHistory} />
      <ChatWindow messages={messages} task={task} setTask={setTask} onSubmit={submit} loading={loading} onClear={()=>setTask('')} />
    </div>
  )
}
