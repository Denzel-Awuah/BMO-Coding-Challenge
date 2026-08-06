import React from 'react'

export default function Composer({ task, setTask, onSubmit, loading, onClear }){
  return (
    <form className="composer" onSubmit={onSubmit}>
      <textarea value={task} onChange={(e)=>setTask(e.target.value)} placeholder='Ask the agent, e.g. "Weather in Toronto?"' />
      <div className="composer-actions">
        <button className="btn" type="submit" disabled={loading}>{loading? 'Thinking...':'Send'}</button>
        <button type="button" className="btn secondary" onClick={onClear}>Clear</button>
      </div>
    </form>
  )
}
