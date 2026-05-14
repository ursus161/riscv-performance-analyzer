const ABI = [
  'zero','ra','sp','gp','tp','t0','t1','t2',
  's0','s1','a0','a1','a2','a3','a4','a5',
  'a6','a7','s2','s3','s4','s5','s6','s7',
  's8','s9','s10','s11','t3','t4','t5','t6',
]

export default function Registers({ registers, prevRegisters }) {
  if (!registers) return (
    <div className="flex-1 rounded border border-[#1a3050] bg-[#0c1829] p-6 flex items-center justify-center">
      <span className="text-[#2a3c50] text-xs font-mono">no data</span>
    </div>
  )

  return (
    <div className="flex-1 rounded border border-[#1a3050] bg-[#0c1829] overflow-hidden">
      <div className="px-3 py-1.5 border-b border-[#1a3050]">
        <span className="text-[11px] font-mono text-[#506880]">registers</span>
      </div>

      <div className="p-2 grid grid-cols-4 gap-0.5 overflow-y-auto max-h-52">
        {Array.from({ length: 32 }, (_, i) => {
          const val = registers[i] ?? 0
          const prev = prevRegisters?.[i] ?? 0
          const changed = prevRegisters !== undefined && val !== prev

          return (
            <div
              key={i}
              className="reg-cell rounded-sm px-1.5 py-1 flex items-center justify-between gap-1"
              style={{ background: changed ? 'rgba(56,212,153,0.10)' : '#08111e' }}
            >
              <div className="flex flex-col leading-none gap-0.5">
                <span className="text-[9px] mono" style={{ color: '#2a3c50' }}>x{i}</span>
                <span className="text-[9px] mono" style={{ color: changed ? '#38d499' : '#2a3c50' }}>{ABI[i]}</span>
              </div>
              <span
                className="text-[11px] mono font-medium tabular-nums"
                style={{ color: changed ? '#38d499' : val !== 0 ? '#c8d8e8' : '#2a3c50' }}
              >
                {val}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
