// dependente RAW intre instructiuni
// causes_stall=true inseamna load-use la distanta 1 — singurul caz pe care forwarding-ul nu-l poate acoperi

const TYPE_COLOR = {
  stall:   { bg: 'rgba(232,80,64,0.08)',  border: 'rgba(232,80,64,0.35)',  text: '#e85040' },
  forward: { bg: 'rgba(232,168,56,0.06)', border: 'rgba(232,168,56,0.25)', text: '#e8a838' },
}

export default function HazardGraph({ hazards }) {
  if (!hazards?.length) return null

  const stalls   = hazards.filter(h => h.causes_stall)
  const forwards = hazards.filter(h => !h.causes_stall)

  const th = 'px-2.5 py-1.5 text-left text-[10px] font-mono font-medium whitespace-nowrap'
  const td = 'px-2.5 py-1.5 font-mono text-[11px]'

  function Row({ h }) {
    const c = h.causes_stall ? TYPE_COLOR.stall : TYPE_COLOR.forward
    return (
      <tr style={{ borderBottom: '1px solid #0e1d2e', background: c.bg }}>
        <td className={td} style={{ color: c.text, fontWeight: 600 }}>
          {h.causes_stall ? 'stall' : 'fwd'}
        </td>
        <td className={td} style={{ color: '#8ab0c8' }}>{h.from_instr}</td>
        <td className={td} style={{ color: '#506880' }}>→</td>
        <td className={td} style={{ color: '#8ab0c8' }}>{h.to_instr}</td>
        <td className={td} style={{ color: '#506880' }}>{h.reg_name}</td>
        <td className={td} style={{ color: '#506880', textAlign: 'right' }}>{h.distance}</td>
      </tr>
    )
  }

  return (
    <div className="rounded border border-[#1a3050] bg-[#0c1829] overflow-hidden">
      <div className="px-3 py-1.5 border-b border-[#1a3050] flex items-center gap-3">
        <span className="text-[11px] font-mono text-[#506880]">dependente RAW</span>
        {stalls.length > 0 && (
          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded"
            style={{ background: 'rgba(232,80,64,0.12)', color: '#e85040', border: '1px solid rgba(232,80,64,0.3)' }}>
            {stalls.length} stall{stalls.length > 1 ? 's' : ''}
          </span>
        )}
        {forwards.length > 0 && (
          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded"
            style={{ background: 'rgba(232,168,56,0.08)', color: '#e8a838', border: '1px solid rgba(232,168,56,0.25)' }}>
            {forwards.length} forwarded
          </span>
        )}
      </div>

      <div className="overflow-x-auto max-h-60 overflow-y-auto">
        <table className="w-full text-[11px] border-collapse">
          <thead className="sticky top-0 bg-[#0c1829] z-10">
            <tr style={{ borderBottom: '1px solid #1a3050', color: '#2a3c50' }}>
              <th className={th}>tip</th>
              <th className={th}>produce</th>
              <th className={th}></th>
              <th className={th}>consuma</th>
              <th className={th}>registru</th>
              <th className={th + ' text-right'}>distanta</th>
            </tr>
          </thead>
          <tbody>
            {/* stall-urile primele ca sunt mai importante */}
            {stalls.map((h, i) => <Row key={`s${i}`} h={h} />)}
            {forwards.map((h, i) => <Row key={`f${i}`} h={h} />)}
          </tbody>
        </table>
      </div>
    </div>
  )
}
