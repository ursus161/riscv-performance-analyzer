// diagrama Gantt clasica din arhitectura calculatoarelor
// fiecare bara e proportionala cu numarul de cicluri petrecute in etapa respectiva
// latimea mare a unui bar = stall (instructiunea a asteptat in etapa aceea)

const STAGE_COLOR = {
  IF:  '#1e4060',
  ID:  '#1a3a5c',
  EX:  '#1a4d38',
  MEM: '#4d3a10',
  WB:  '#3a1a5c',
}
const STAGE_TEXT = {
  IF: '#4a80a8', ID: '#3a6080', EX: '#38d499', MEM: '#e8a838', WB: '#9d7bda',
}

const CELL = 20  // pixeli per ciclu

function abbrev(instr) {
  return instr.length > 22 ? instr.slice(0, 21) + '…' : instr
}

function GanttRow({ entry }) {
  const { IF: tIF, ID: tID, EX: tEX, MEM: tMEM, WB: tWB, instr } = entry

  const bars = [
    { name: 'IF',  from: tIF,  to: tID  },
    { name: 'ID',  from: tID,  to: tEX  },
    { name: 'EX',  from: tEX,  to: tMEM },
    { name: 'MEM', from: tMEM, to: tWB  },
    { name: 'WB',  from: tWB,  to: tWB + 1 },
  ]

  return (
    <div className="flex items-stretch" style={{ height: 18, marginBottom: 2 }}>
      <div
        className="shrink-0 font-mono overflow-hidden text-ellipsis whitespace-nowrap"
        style={{ width: 140, fontSize: 10, color: '#506880', lineHeight: '18px', paddingRight: 6 }}
        title={instr}
      >
        {abbrev(instr)}
      </div>
      <div style={{ position: 'relative', flex: 1 }}>
        {bars.map(({ name, from, to }) => {
          if (from == null || to == null) return null
          const w = (to - from) * CELL
          return (
            <div
              key={name}
              style={{
                position: 'absolute',
                left: from * CELL,
                width: w,
                height: '100%',
                background: STAGE_COLOR[name],
                border: '1px solid rgba(0,0,0,0.4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 9,
                color: STAGE_TEXT[name],
                fontFamily: 'monospace',
                overflow: 'hidden',
                boxSizing: 'border-box',
              }}
            >
              {w >= 18 ? name : ''}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default function Timeline({ stats }) {
  if (!stats?.timeline) return null

  const entries = Object.values(stats.timeline)
  if (!entries.length) return null

  // nu afisam pentru programe prea mari — diagrama devine ilizibila
  if (entries.length > 30) return (
    <div className="rounded border border-[#1a3050] bg-[#0c1829] px-3 py-2">
      <span className="text-[11px] font-mono text-[#506880]">
        pipeline timeline — disponibil pentru ≤30 instrucțiuni ({entries.length} găsite)
      </span>
    </div>
  )

  const maxCycle = stats.total_cycles ?? Math.max(...entries.map(e => (e.WB ?? 0) + 1))
  const totalW = (maxCycle + 1) * CELL

  // afisam headerul cu numerele ciclurilor — din 5 in 5 daca sunt prea multe
  const step = maxCycle > 40 ? 10 : maxCycle > 20 ? 5 : 1
  const ticks = Array.from({ length: maxCycle + 1 }, (_, i) => i).filter(i => i % step === 0)

  return (
    <div className="rounded border border-[#1a3050] bg-[#0c1829] overflow-hidden">
      <div className="px-3 py-1.5 border-b border-[#1a3050] flex items-center gap-3">
        <span className="text-[11px] font-mono text-[#506880]">pipeline timeline</span>
        <span className="text-[10px] font-mono text-[#2a3c50]">{maxCycle} cicluri · {entries.length} instrucțiuni</span>
      </div>

      <div className="p-3 overflow-x-auto">
        {/* header cicluri */}
        <div className="flex" style={{ marginBottom: 4, paddingLeft: 140 }}>
          <div style={{ position: 'relative', width: totalW, height: 14 }}>
            {ticks.map(c => (
              <div
                key={c}
                style={{
                  position: 'absolute',
                  left: c * CELL,
                  fontSize: 9,
                  fontFamily: 'monospace',
                  color: '#2a3c50',
                  transform: 'translateX(-50%)',
                }}
              >
                {c}
              </div>
            ))}
          </div>
        </div>

        {/* linii cu instructiunile */}
        {entries.map((entry, i) => <GanttRow key={i} entry={entry} />)}

        {/* legenda */}
        <div className="flex gap-3 mt-3 flex-wrap">
          {Object.entries(STAGE_COLOR).map(([name, bg]) => (
            <div key={name} className="flex items-center gap-1">
              <div style={{ width: 12, height: 10, background: bg, border: '1px solid rgba(0,0,0,0.4)' }} />
              <span style={{ fontSize: 9, fontFamily: 'monospace', color: STAGE_TEXT[name] }}>{name}</span>
            </div>
          ))}
          <span style={{ fontSize: 9, fontFamily: 'monospace', color: '#2a3c50' }}>· golul dintre bare = ciclu de stall</span>
        </div>
      </div>
    </div>
  )
}
