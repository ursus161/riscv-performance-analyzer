function Btn({ onClick, disabled, variant = 'default', children }) {
  const base = 'px-3 py-1 rounded-sm text-[11px] font-mono font-medium border transition-all disabled:opacity-30 disabled:cursor-not-allowed'
  const variants = {
    primary: 'bg-[#0e2a4a] hover:bg-[#122e56] text-[#3a9de8] border-[#1a3a6a]',
    success: 'bg-[#0a2a1c] hover:bg-[#0d3022] text-[#38d499] border-[#124830]',
    ghost:   'bg-transparent hover:bg-[#101f36] text-[#506880] hover:text-[#c8d8e8] border-[#1a3050]',
  }
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${variants[variant] ?? variants.ghost}`}
    >
      {children}
    </button>
  )
}

function Toggle({ label, checked, onChange }) {
  return (
    <label className="flex items-center gap-1.5 cursor-pointer select-none">
      <div
        onClick={onChange}
        className="w-6 h-3.5 rounded-sm relative transition-colors cursor-pointer"
        style={{ background: checked ? '#1a3a6a' : '#101f36', border: '1px solid ' + (checked ? '#2a5aa0' : '#1a3050') }}
      >
        <div
          className="absolute top-0.5 w-2.5 h-2.5 rounded-sm bg-white transition-all"
          style={{ left: checked ? 'calc(100% - 11px)' : '1px', opacity: checked ? 1 : 0.35 }}
        />
      </div>
      <span className="text-[11px] font-mono" style={{ color: checked ? '#3a9de8' : '#506880' }}>{label}</span>
    </label>
  )
}

export default function Controls({ config, onConfigChange, onRun, onStep, onReset, onCompare, stepLabel, loading, done, inStep }) {
  const toggle = key => onConfigChange(c => ({ ...c, [key]: !c[key] }))

  return (
    <div className="flex items-center gap-2">
      <Btn onClick={onRun} disabled={loading || inStep} variant="primary">▶ run</Btn>
      <Btn onClick={onStep} disabled={loading || done} variant="success">{stepLabel}</Btn>
      <Btn onClick={onReset} disabled={loading} variant="ghost">↺ reset</Btn>
      <Btn onClick={onCompare} disabled={loading || inStep} variant="ghost">⇌ compare</Btn>

      <div className="w-px h-4 bg-[#1a3050] mx-1" />

      <Toggle label="cache" checked={config.use_cache} onChange={() => toggle('use_cache')} />
      <Toggle label="branch pred" checked={config.use_branch_predictor} onChange={() => toggle('use_branch_predictor')} />
    </div>
  )
}
