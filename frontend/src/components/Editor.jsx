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

export default function Editor({ code, onChange, activeStages = [] }) {
  const taRef = useRef()
  const preRef = useRef()

  const syncScroll = useCallback(() => {
    if (preRef.current && taRef.current) {
      preRef.current.scrollTop = taRef.current.scrollTop
      preRef.current.scrollLeft = taRef.current.scrollLeft
    }
  }, [])

  const lines = highlight(code)
  const codeLines = code.split('\n')

  // build a map: lineIndex -> stage name (first match wins)
  const lineStage = {}
  for (const { stage, instr } of activeStages) {
    const idx = matchLine(code, instr)
    if (idx >= 0 && !(idx in lineStage)) lineStage[idx] = stage
  }

  const lineCount = codeLines.length

  return (
    <div className="flex-1 overflow-hidden flex" style={{ background: '#08111e' }}>
      {/* Line numbers */}
      <div
        className="shrink-0 w-10 overflow-hidden select-none border-r"
        style={{ borderColor: '#1a3050' }}
        style={{ paddingTop: 12, paddingBottom: 12 }}
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

      {/* Highlighted pre + textarea */}
      <div className="editor-wrap">
        <pre ref={preRef} className="editor-pre">
          {lines.map((html, i) => (
            <span
              key={i}
              className={`editor-line ${lineStage[i] ? STAGE_CLASS[lineStage[i]] : ''}`}
              dangerouslySetInnerHTML={{ __html: html || ' ' }}
            />
          ))}
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
