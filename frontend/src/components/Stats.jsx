function Bar({ value, color }) {
  return (
    <div className="h-px mt-1" style={{ background: '#1a3050' }}>
      <div
        className="h-full transition-all duration-500"
        style={{ width: `${Math.min(100, value * 100)}%`, background: color }}
      />
    </div>
  )
}

function MetricCard({ label, value, sub, bar, barColor }) {
  return (
    <div className="flex flex-col gap-1 pl-2.5 py-2" style={{ borderLeft: '2px solid #1a3050' }}>
      <span className="text-[10px] font-mono" style={{ color: '#3a5870' }}>{label}</span>
      <span className="text-base font-mono font-semibold leading-none" style={{ color: '#c8d8e8' }}>{value}</span>
      {sub && <span className="text-[10px] font-mono" style={{ color: '#3a5870' }}>{sub}</span>}
      {bar !== undefined && <Bar value={bar} color={barColor} />}
    </div>
  )
}

function ipcColor(ipc) {
  if (ipc >= 0.8) return '#38d499'
  if (ipc >= 0.5) return '#e8a838'
  return '#e85040'
}

function hitColor(rate) {
  if (rate >= 0.9) return '#38d499'
  if (rate >= 0.6) return '#e8a838'
  return '#e85040'
}

function findOptimalIdx(variants, baseIpc) {
  if (!variants?.length) return -1
  const bestIpc = Math.max(...variants.map(v => v.stats.ipc))
  if (bestIpc <= baseIpc * 1.01) return -1
  return variants.findIndex(v => v.stats.ipc >= bestIpc * 0.99)
}

function CompareTable({ compareStats }) {
  const { baseline, variants } = compareStats
  const baseIpc = baseline?.ipc ?? 1

  const optimalIdx = findOptimalIdx(variants, baseIpc)
  const bestIpc = variants?.length ? Math.max(...variants.map(v => v.stats.ipc)) : baseIpc
  const allSame = bestIpc <= baseIpc * 1.01

  const delta = (ipc) => {
    const d = baseIpc > 0 ? ((ipc - baseIpc) / baseIpc) * 100 : 0
    return {
      str: d >= 0 ? `+${d.toFixed(1)}%` : `${d.toFixed(1)}%`,
      color: d > 1 ? '#38d499' : d < -1 ? '#e85040' : '#506880',
    }
  }

  const optimalV = optimalIdx >= 0 ? variants[optimalIdx] : null
  const banner = allSame
    ? 'cache nu aduce beneficiu — nicio instrucțiune de memorie semnificativă'
    : optimalV
      ? `optim: ${optimalV.size}B / ${optimalV.associativity}-way / ${optimalV.write_policy === 'write-back' ? 'WB' : 'WT'} — cel mai mic cache care atinge performanța maximă`
      : null

  const th = 'text-right px-2.5 py-1.5 text-[10px] font-mono font-medium whitespace-nowrap'
  const td = 'text-right px-2.5 py-1.5 font-mono text-[11px] tabular-nums'

  return (
    <div className="rounded border border-[#1a3050] bg-[#0c1829] overflow-hidden">
      <div className="px-3 py-1.5 border-b border-[#1a3050]">
        <span className="text-[11px] font-mono text-[#506880]">cache comparison</span>
      </div>

      {banner && (
        <div className="px-3 py-2 text-[11px] font-mono border-b border-[#1a3050] flex items-center gap-2"
          style={{ background: allSame ? 'rgba(232,168,56,0.06)' : 'rgba(58,157,232,0.06)', color: allSame ? '#e8a838' : '#3a9de8' }}>
          {allSame ? '⚠' : '✓'} {banner}
        </div>
      )}

      <div className="overflow-x-auto max-h-80 overflow-y-auto">
        <table className="w-full text-[11px] border-collapse">
          <thead className="sticky top-0 bg-[#0c1829] z-10">
            <tr style={{ borderBottom: '1px solid #1a3050', color: '#2a3c50' }}>
              <th className="text-left px-2.5 py-1.5 text-[10px] font-mono font-medium">size</th>
              <th className={th}>assoc</th>
              <th className={th}>policy</th>
              <th className={th}>cycles</th>
              <th className={th}>ipc</th>
              <th className={th}>cpi</th>
              <th className={th}>hit%</th>
              <th className={th}>amat</th>
              <th className={th}>Δ ipc</th>
            </tr>
          </thead>
          <tbody>
            {baseline && (
              <tr style={{ borderBottom: '1px solid #1a3050', background: '#08111e' }}>
                <td className="px-2.5 py-1.5 font-mono text-[11px] italic" style={{ color: '#3a5870' }} colSpan={3}>no cache</td>
                <td className={td} style={{ color: '#506880' }}>{baseline.total_cycles}</td>
                <td className={td + ' font-semibold'} style={{ color: ipcColor(baseline.ipc) }}>{baseline.ipc.toFixed(3)}</td>
                <td className={td} style={{ color: '#506880' }}>{baseline.cpi.toFixed(2)}</td>
                <td className={td} style={{ color: '#2a3c50' }}>—</td>
                <td className={td} style={{ color: '#2a3c50' }}>—</td>
                <td className={td} style={{ color: '#2a3c50' }}>—</td>
              </tr>
            )}

            {variants?.map((v, i) => {
              const s = v.stats
              const cs = s.cache
              const d = delta(s.ipc)
              const isOptimal = i === optimalIdx
              return (
                <tr
                  key={i}
                  style={{
                    borderBottom: '1px solid #0e1d2e',
                    background: isOptimal ? 'rgba(58,157,232,0.06)' : 'transparent',
                  }}
                  className="hover:bg-[#101f36] transition-colors"
                >
                  <td className="px-2.5 py-1.5 font-mono text-[11px] font-medium flex items-center gap-1.5"
                    style={{ color: isOptimal ? '#3a9de8' : '#c8d8e8' }}>
                    {v.size}B
                    {isOptimal && (
                      <span className="text-[9px] font-mono px-1 py-0.5 rounded-sm"
                        style={{ background: 'rgba(58,157,232,0.15)', color: '#3a9de8', border: '1px solid rgba(58,157,232,0.3)' }}>
                        optim
                      </span>
                    )}
                  </td>
                  <td className={td} style={{ color: '#506880' }}>{v.associativity}-way</td>
                  <td className={td} style={{ color: '#506880' }}>{v.write_policy === 'write-back' ? 'WB' : 'WT'}</td>
                  <td className={td} style={{ color: '#506880' }}>{s.total_cycles}</td>
                  <td className={td + ' font-semibold'} style={{ color: ipcColor(s.ipc) }}>{s.ipc.toFixed(3)}</td>
                  <td className={td} style={{ color: '#506880' }}>{s.cpi.toFixed(2)}</td>
                  <td className={td + ' font-semibold'} style={{ color: cs ? hitColor(cs.hit_rate) : '#2a3c50' }}>
                    {cs ? `${(cs.hit_rate * 100).toFixed(1)}%` : '—'}
                  </td>
                  <td className={td} style={{ color: '#506880' }}>{cs ? cs.amat.toFixed(2) : '—'}</td>
                  <td className={td + ' font-semibold'} style={{ color: d.color }}>{d.str}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function Stats({ stats, state, config, compareStats }) {
  const bp  = stats?.branch_predictor
  const btb = stats?.btb

  const cycles = stats?.total_cycles ?? state?.cycle
  const instrs = stats?.total_instructions
  const cpi    = stats?.cpi
  const ipc    = stats?.ipc

  if (!cycles && !compareStats) return null

  return (
    <>
      {cycles && (
        <div className="rounded border border-[#1a3050] bg-[#0c1829] overflow-hidden">
          <div className="px-3 py-1.5 border-b border-[#1a3050]">
            <span className="text-[11px] font-mono text-[#506880]">performance</span>
          </div>
          <div className="p-3 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-x-6 gap-y-3">
            <MetricCard label="cycles" value={cycles} />
            {instrs !== undefined && <MetricCard label="instructions" value={instrs} />}
            {cpi !== undefined && (
              <MetricCard label="cpi" value={cpi.toFixed(2)} sub="cycles / instr"
                bar={Math.min(1, 1 / cpi)}
                barColor={cpi <= 1.5 ? '#38d499' : cpi <= 2.5 ? '#e8a838' : '#e85040'} />
            )}
            {ipc !== undefined && (
              <MetricCard label="ipc" value={ipc.toFixed(2)} sub="instrs / cycle"
                bar={Math.min(1, ipc)} barColor="#3a9de8" />
            )}
            {bp && (
              <MetricCard label="bp accuracy"
                value={`${(bp.accuracy * 100).toFixed(1)}%`}
                sub={`${bp.mispredictions} miss`}
                bar={bp.accuracy}
                barColor={bp.accuracy >= 0.9 ? '#38d499' : bp.accuracy >= 0.7 ? '#e8a838' : '#e85040'} />
            )}
            {btb && (
              <MetricCard label="btb hit rate"
                value={`${(btb.hit_rate * 100).toFixed(1)}%`}
                sub={`${btb.hits} / ${btb.hits + btb.misses}`}
                bar={btb.hit_rate} barColor="#9d7bda" />
            )}
          </div>
        </div>
      )}

      {compareStats && <CompareTable compareStats={compareStats} />}
    </>
  )
}
