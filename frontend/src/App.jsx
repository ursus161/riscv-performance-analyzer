import { useState, useRef, useEffect } from 'react'
import Editor from './components/Editor'
import Pipeline from './components/Pipeline'
import Registers from './components/Registers'
import Memory from './components/Memory'
import Stats from './components/Stats'
import Controls from './components/Controls'

const API = 'http://localhost:8000'

const DEFAULT_CODE = `.data
.text
.globl main
main:
  addi x1, x0, 10
  addi x2, x0, 3
  add  x3, x1, x2
  sub  x4, x1, x2
`

const EDITOR_MIN = 220
const EDITOR_MAX = 0.65

export default function App() {
  const [code, setCode] = useState(() =>
    localStorage.getItem('riscv-code') ?? DEFAULT_CODE
  )
  const [editorWidth, setEditorWidth] = useState(() =>
    parseInt(localStorage.getItem('editor-width') ?? '400')
  )
  const [config, setConfig] = useState({ use_cache: false, use_branch_predictor: false })
  const [pipelineState, setPipelineState] = useState(null)
  const [prevState, setPrevState] = useState(null)
  const [stats, setStats] = useState(null)
  const [compareStats, setCompareStats] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState(null)
  const sessionId = useRef(null)
  const isDragging = useRef(false)
  const widthRef = useRef(editorWidth)

  useEffect(() => { localStorage.setItem('riscv-code', code) }, [code])

  useEffect(() => {
    const onMove = (e) => {
      if (!isDragging.current) return
      const max = window.innerWidth * EDITOR_MAX
      const w = Math.round(Math.max(EDITOR_MIN, Math.min(max, e.clientX)))
      widthRef.current = w
      setEditorWidth(w)
    }
    const onUp = () => {
      if (!isDragging.current) return
      isDragging.current = false
      localStorage.setItem('editor-width', widthRef.current)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp) }
  }, [])

  const startDrag = (e) => {
    isDragging.current = true
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
    e.preventDefault()
  }

  const reset = async () => {
    if (sessionId.current) {
      await fetch(`${API}/session/${sessionId.current}`, { method: 'DELETE' }).catch(() => {})
      sessionId.current = null
    }
    setPipelineState(null)
    setPrevState(null)
    setStats(null)
    setCompareStats(null)
    setError(null)
    setMode(null)
  }

  const run = async () => {
    await reset()
    setLoading(true)
    try {
      const res = await fetch(`${API}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, ...config }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail)
      setPipelineState(data.state)
      setStats(data.stats)
      setMode('run')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const startStep = async () => {
    await reset()
    setLoading(true)
    try {
      const res = await fetch(`${API}/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, ...config }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail)
      sessionId.current = data.session_id
      setPipelineState(data.state)
      setMode('step')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const step = async () => {
    if (!sessionId.current) return
    setLoading(true)
    try {
      const res = await fetch(`${API}/session/${sessionId.current}/step`, { method: 'POST' })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail)
      setPrevState(pipelineState)
      setPipelineState(data.state ?? data)
      if (data.stats) setStats(data.stats)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const compare = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API}/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, ...config }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail)
      setCompareStats(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const inStep = mode === 'step'
  const isDone = pipelineState?.done && pipelineState?.cycle > 0
  const canStep = inStep && !isDone

  const activeStages = pipelineState
    ? Object.entries(pipelineState.stages)
        .filter(([, s]) => s.instruction)
        .map(([name, s]) => ({ stage: name, instr: s.instruction }))
    : []

  // Status bar text
  const statusMode = loading ? 'running…'
    : isDone ? 'done'
    : inStep ? `step · cycle ${pipelineState?.cycle ?? 0}`
    : mode === 'run' ? 'complete'
    : 'idle'

  const statusColor = loading ? '#e8a838'
    : isDone ? '#38d499'
    : inStep ? '#3a9de8'
    : mode === 'run' ? '#38d499'
    : '#3a5870'

  return (
    <div className="h-full flex flex-col" style={{ background: '#08111e', color: '#c8d8e8' }}>
      {/* Header */}
      <header className="h-10 shrink-0 flex items-center gap-4 px-4 border-b" style={{ borderColor: '#1a3050', background: '#0c1829' }}>
        <div className="flex items-center gap-2 shrink-0">
          <span className="font-mono font-semibold text-sm" style={{ color: '#3a9de8' }}>RISC-V</span>
          <span className="font-mono text-xs hidden sm:inline" style={{ color: '#2a3c50' }}>/ performance analyzer</span>
        </div>

        <div className="ml-auto flex items-center gap-2">
          <Controls
            config={config}
            onConfigChange={setConfig}
            onRun={run}
            onStep={canStep ? step : startStep}
            onReset={reset}
            onCompare={compare}
            stepLabel={inStep && pipelineState ? 'step →' : 'step mode'}
            loading={loading}
            done={isDone}
            inStep={inStep}
          />
        </div>
      </header>

      {/* Body */}
      <div className="flex-1 overflow-hidden flex min-h-0">

        {/* Left: Editor */}
        <div
          className="shrink-0 flex flex-col border-r min-w-0"
          style={{ width: editorWidth, borderColor: '#1a3050' }}
        >
          <div className="px-3 py-1.5 border-b shrink-0 flex items-center gap-2" style={{ borderColor: '#1a3050', background: '#0c1829' }}>
            <span className="text-[11px] font-mono" style={{ color: '#506880' }}>editor</span>
          </div>
          <Editor code={code} onChange={setCode} activeStages={activeStages} />

          {error && (
            <div className="shrink-0 border-t p-2.5" style={{ borderColor: 'rgba(232,80,64,0.3)', background: 'rgba(232,80,64,0.07)' }}>
              <pre className="text-[11px] font-mono whitespace-pre-wrap leading-relaxed" style={{ color: '#e85040' }}>{error}</pre>
            </div>
          )}
        </div>

        {/* Resize handle */}
        <div
          className="w-px shrink-0 cursor-col-resize transition-colors duration-150"
          style={{ background: '#1a3050' }}
          onMouseDown={startDrag}
          onMouseEnter={e => e.currentTarget.style.background = '#3a9de8'}
          onMouseLeave={e => e.currentTarget.style.background = '#1a3050'}
        />

        {/* Right: Dashboard */}
        <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-3 min-w-0">
          <Pipeline state={pipelineState} prevState={prevState} />

          <div className="flex gap-3 flex-wrap">
            <Registers registers={pipelineState?.registers} prevRegisters={prevState?.registers} />
            <Memory memory={pipelineState?.memory} />
          </div>

          {(stats || pipelineState) && (
            <Stats stats={stats} state={pipelineState} config={config} compareStats={compareStats} />
          )}
        </div>
      </div>

      {/* Status bar */}
      <div className="h-6 shrink-0 flex items-center px-3 gap-4 border-t text-[10px] font-mono" style={{ borderColor: '#1a3050', background: '#0a1522' }}>
        <span style={{ color: statusColor }}>{statusMode}</span>

        {pipelineState?.cycle > 0 && (
          <>
            <span style={{ color: '#1e3048' }}>·</span>
            <span style={{ color: '#3a5870' }}>
              cycle <span style={{ color: '#506880' }}>{pipelineState.cycle}</span>
            </span>
          </>
        )}
        {stats?.total_instructions && (
          <>
            <span style={{ color: '#1e3048' }}>·</span>
            <span style={{ color: '#3a5870' }}>
              {stats.total_instructions} instr
            </span>
          </>
        )}
        {stats?.ipc !== undefined && (
          <>
            <span style={{ color: '#1e3048' }}>·</span>
            <span style={{ color: '#3a5870' }}>
              IPC <span style={{ color: '#506880' }}>{stats.ipc.toFixed(2)}</span>
            </span>
          </>
        )}

        <div className="ml-auto flex items-center gap-3">
          {config.use_cache && <span style={{ color: '#2a4870' }}>cache</span>}
          {config.use_branch_predictor && <span style={{ color: '#2a4870' }}>bp</span>}
        </div>
      </div>
    </div>
  )
}
