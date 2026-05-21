import { highlight } from '../utils/highlight'

const STAGE_CLASS = { IF: 'stage-if', ID: 'stage-id', EX: 'stage-ex', MEM: 'stage-mem', WB: 'stage-wb' }

function matchLine(code, instrStr) {
  if (!instrStr) return -1
  const norm = s => s.replace(/\s+/g, ' ').trim().toLowerCase()
  const target = norm(instrStr)
  return code.split('\n').findIndex(l => norm(l) === target || norm(l).includes(target))
}

export default function Editor({ code, onChange, activeStages = [], stallData = null }) {
  const lines = highlight(code)
  const codeLines = code.split('\n')

  const lineStage = {}
  for (const { stage, instr } of activeStages) {
    const idx = matchLine(code, instr)
    if (idx >= 0 && !(idx in lineStage)) lineStage[idx] = stage
  }

  const maxStalls = stallData ? Math.max(1, ...Object.values(stallData)) : 0

  return (
    <div className="flex-1 overflow-hidden" style={{ background: '#08111e' }}>
    <div style={{ height: '100%', overflow: 'auto' }}>
    <div style={{ display: 'flex', minHeight: '100%' }}>
      {/* Line numbers */}
      <div
        className="shrink-0 w-10 select-none border-r"
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

      {/* Stall gutter */}
      {stallData && (
        <div
          className="shrink-0 select-none border-r"
          style={{ width: 36, borderColor: '#1a3050', paddingTop: 12, paddingBottom: 12 }}
        >
          {codeLines.map((_, i) => {
            const n = stallData[i] ?? 0
            const t = n / maxStalls
            const r = Math.round(232)
            const g = Math.round(80 + (1 - t) * 88)
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
        <pre className="editor-pre">
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
          className="editor-ta"
          value={code}
          onChange={e => onChange(e.target.value)}
          spellCheck={false}
          autoCapitalize="off"
          autoCorrect="off"
        />
      </div>
    </div>
    </div>
    </div>
  )
}
