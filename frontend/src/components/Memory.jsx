export default function Memory({ memory }) {
  const entries = memory ? Object.entries(memory) : []

  return (
    <div className="w-60 shrink-0 rounded border border-[#1a3050] bg-[#0c1829] overflow-hidden flex flex-col">
      <div className="px-3 py-1.5 border-b border-[#1a3050] shrink-0">
        <span className="text-[11px] font-mono text-[#506880]">memory</span>
      </div>

      <div className="overflow-y-auto flex-1 max-h-52">
        {entries.length === 0 ? (
          <div className="p-3 text-[#2a3c50] text-[11px] font-mono italic">empty</div>
        ) : (
          <table className="w-full text-[11px] mono border-collapse">
            <thead className="sticky top-0 bg-[#0c1829]">
              <tr style={{ color: '#2a3c50' }}>
                <th className="text-left px-3 py-1 border-b border-[#1a3050] font-medium">addr</th>
                <th className="text-right px-3 py-1 border-b border-[#1a3050] font-medium">hex</th>
                <th className="text-right px-3 py-1 border-b border-[#1a3050] font-medium">dec</th>
              </tr>
            </thead>
            <tbody>
              {entries.map(([addr, val]) => (
                <tr key={addr} className="border-b border-[#0e1d2e] hover:bg-[#101f36] transition-colors">
                  <td className="px-3 py-1" style={{ color: '#3a9de8' }}>{addr}</td>
                  <td className="px-3 py-1 text-right" style={{ color: '#e8a050' }}>
                    {`0x${(val >>> 0).toString(16).padStart(8, '0')}`}
                  </td>
                  <td className="px-3 py-1 text-right" style={{ color: '#506880' }}>{val}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
