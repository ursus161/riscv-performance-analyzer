const STAGES = ['IF', 'ID', 'EX', 'MEM', 'WB']

const CFG = {
  IF:  { label: 'fetch',     color: '#9d7bda', border: '#4a3080', bg: 'rgba(157,123,218,0.07)' },
  ID:  { label: 'decode',    color: '#3a9de8', border: '#1a4a80', bg: 'rgba(58,157,232,0.07)'  },
  EX:  { label: 'execute',   color: '#e8a838', border: '#704e0a', bg: 'rgba(232,168,56,0.08)'  },
  MEM: { label: 'memory',    color: '#e87838', border: '#703008', bg: 'rgba(232,120,56,0.08)'  },
  WB:  { label: 'writeback', color: '#38d499', border: '#157840', bg: 'rgba(56,212,153,0.07)'  },
}

function getStatus(stage, curr, prev) {
  const c = curr?.stages[stage]?.instruction ?? null
  const p = prev?.stages[stage]?.instruction ?? null
  if (!c) return 'idle'
  if (prev && c === p) return 'stall'
  return 'active'
}

function StageCard({ name, state, prevState }) {
  const cfg = CFG[name]
  const instr = state?.stages[name]?.instruction ?? null
  const status = getStatus(name, state, prevState)
  const idle = !instr

  return (
    <div
      className="stage-card flex flex-col rounded overflow-hidden"
      style={{
        border: `1px solid ${idle ? '#1a3050' : cfg.border}`,
        background: idle ? '#0c1829' : cfg.bg,
        opacity: idle ? 0.45 : 1,
      }}
    >
      <div
        className="px-2.5 py-1 flex items-center justify-between"
        style={{ borderBottom: `1px solid ${idle ? '#1a3050' : cfg.border}20` }}
      >
        <span className="text-[11px] font-mono font-semibold" style={{ color: idle ? '#2a3c50' : cfg.color }}>{name}</span>
        <span className="text-[10px] font-mono" style={{ color: idle ? '#1e3048' : cfg.color + '88' }}>{cfg.label}</span>
      </div>

      <div className="px-2.5 py-2 flex-1 flex flex-col gap-1.5 min-h-[64px]">
        {instr ? (
          <span className="text-[11px] mono text-[#c8d8e8] leading-snug break-all">{instr}</span>
        ) : (
          <span className="text-[11px] mono text-[#1e3048] italic">—</span>
        )}
        <div className="mt-auto">
          {status === 'stall' && (
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded-sm font-bold"
              style={{ background: 'rgba(232,168,56,0.15)', color: '#e8a838', border: '1px solid rgba(232,168,56,0.3)' }}>
              stall
            </span>
          )}
          {status === 'active' && (
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded-sm font-bold"
              style={{ background: 'rgba(56,212,153,0.12)', color: '#38d499', border: '1px solid rgba(56,212,153,0.25)' }}>
              active
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

function Arrow() {
  return (
    <div className="flex items-center justify-center shrink-0 mt-4 text-[#1e3048] select-none text-sm">›</div>
  )
}

export default function Pipeline({ state, prevState }) {
  if (!state) return (
    <div className="rounded border border-[#1a3050] bg-[#0c1829] p-8 flex items-center justify-center">
      <span className="text-[#2a3c50] text-xs font-mono">run or step to see pipeline activity</span>
    </div>
  )

  return (
    <div className="rounded border border-[#1a3050] bg-[#0c1829] overflow-hidden">
      <div className="px-3 py-1.5 border-b border-[#1a3050] flex items-center gap-3">
        <span className="text-[11px] font-mono text-[#506880]">pipeline</span>
        <span className="mono text-[11px] text-[#506880]">
          cycle <span className="text-[#c8d8e8]">{state.cycle}</span>
        </span>
        {state.done && (
          <span className="ml-auto text-[10px] font-mono px-2 py-0.5 rounded-sm"
            style={{ background: 'rgba(56,212,153,0.12)', color: '#38d499', border: '1px solid rgba(56,212,153,0.25)' }}>
            done
          </span>
        )}
      </div>

      <div className="p-3 flex items-stretch gap-1">
        {STAGES.map((name, i) => (
          <div key={name} className="flex items-center gap-1 flex-1">
            <div className="flex-1">
              <StageCard name={name} state={state} prevState={prevState} />
            </div>
            {i < STAGES.length - 1 && <Arrow />}
          </div>
        ))}
      </div>
    </div>
  )
}
