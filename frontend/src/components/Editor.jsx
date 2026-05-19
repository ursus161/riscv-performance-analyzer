import { useRef, useCallback } from 'react'
import { highlight } from '../utils/highlight'

const STAGE_CLASS = { IF: 'stage-if', ID: 'stage-id', EX: 'stage-ex', MEM: 'stage-mem', WB: 'stage-wb' }

function matchLine(code, instrStr) {
  if (!instrStr) return -1
  const lines = code.split('\n')
  // normalize: strip extra spaces
  const norm = s => s.replace(/\s+/g, ' ').trim().toLowerCase()
  const target = norm(instrStr)
  return lines.findIndex(l => norm(l) === target || norm(l).includes(target))
}

export default function Editor({ code, onChange, activeStages = [], stallData = null }) {
  const taRef = useRef()
  const preRef = useRef()
  const lineNumRef = useRef()
  const stallGutterRef = useRef()

  const syncScroll = useCallback(() => {
    const top = taRef.current?.scrollTop ?? 0
    const left = taRef.current?.scrollLeft ?? 0
    if (preRef.current)       { preRef.current.scrollTop = top; preRef.current.scrollLeft = left }
    if (lineNumRef.current)   lineNumRef.current.scrollTop = top
    if (stallGutterRef.current) stallGutterRef.current.scrollTop = top
  }, [])

  const lines = highlight(code)
  const codeLines = code.split('\n')

  const lineStage = {}
  for (const { stage, instr } of activeStages) {
    const idx = matchLine(code, instr)
    if (idx >= 0 && !(idx in lineStage)) lineStage[idx] = stage
  }

  const maxStalls = stallData ? Math.max(1, ...Object.values(stallData)) : 0

  return (
    <div className="flex-1 overflow-hidden flex" style={{ background: '#08111e' }}>
      {/* Line numbers */}
      <div
        ref={lineNumRef}
        className="shrink-0 w-10 overflow-hidden select-none border-r"
        style={{ borderColor: '#1a3050', paddingTop: 12, paddingBottom: 12 }}
      >
        {codeLines.map((_, i) => (
          <div
            key={i}
            className="text-right pr-2 mono leading-5 text-[13px]"
            style={{ color: '#1e3a58', height: 20, lineHeight: '20px' }}
          >
            {i + 1}
          </div>
        ))}
      </div>

      {/* Stall gutter — arata ciclurile de stall cauzate de fiecare linie */}
      {stallData && (
        <div
          ref={stallGutterRef}
          className="shrink-0 overflow-hidden select-none border-r"
          style={{ width: 36, borderColor: '#1a3050', paddingTop: 12, paddingBottom: 12 }}
        >
          {codeLines.map((_, i) => {
            const n = stallData[i] ?? 0
            const t = n / maxStalls
            const r = Math.round(232)
            const g = Math.round(80 + (1 - t) * 88)  // portocaliu -> rosu
            const a = n > 0 ? 0.5 + t * 0.5 : 0
            return (
              <div
                key={i}
                className="text-right pr-1.5 font-mono"
                style={{ height: 20, lineHeight: '20px', fontSize: 9, color: `rgba(${r},${g},64,${a})` }}
              >
                {n > 0 ? `+${n}` : ''}
              </div>
            )
          })}
        </div>
      )}

      {/* Highlighted pre + textarea */}
      <div className="editor-wrap">
        <pre ref={preRef} className="editor-pre">
          {lines.map((html, i) => {
            const n = stallData?.[i] ?? 0
            const t = n / maxStalls
            const bg = n > 0 && !lineStage[i]
              ? `rgba(232,${Math.round(80 + (1 - t) * 88)},64,${t * 0.12})`
              : undefined
            return (
              <span
                key={i}
                className={`editor-line ${lineStage[i] ? STAGE_CLASS[lineStage[i]] : ''}`}
                style={bg ? { background: bg } : undefined}
                dangerouslySetInnerHTML={{ __html: html || ' ' }}
              />
            )
          })}
        </pre>
        <textarea
          ref={taRef}
          className="editor-ta"
          value={code}
          onChange={e => onChange(e.target.value)}
          onScroll={syncScroll}
          spellCheck={false}
          autoCapitalize="off"
          autoCorrect="off"
        />
      </div>
    </div>
  )
}
