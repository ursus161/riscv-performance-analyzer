const OPCODES = new Set([
  'add','sub','and','or','xor','sll','srl','sra',
  'addi','andi','ori','xori','slti','sltiu','slli','srli','srai',
  'lw','lb','lh','lbu','lhu','sw','sb','sh',
  'beq','bne','blt','bge','bltu','bgeu',
  'lui','auipc','jal','jalr',
  'slt','sltu','mul','div','rem',
  'la','li','mv','nop','ret','call',
])

const REGS = new Set([
  'zero','ra','sp','gp','tp',
  't0','t1','t2','t3','t4','t5','t6',
  's0','fp','s1','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11',
  'a0','a1','a2','a3','a4','a5','a6','a7',
])

const isReg = w => REGS.has(w) || /^x([0-9]|[12][0-9]|3[01])$/.test(w)

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

const TOKEN = /(\.[a-z]+\b)|([a-zA-Z_]\w*\s*:)|(0x[0-9a-fA-F]+)|(-?\d+)|([a-zA-Z_]\w*)|([(),+\-])|(\s+)/g

function highlightLine(line) {
  const ci = line.indexOf('#')
  const code = ci >= 0 ? line.slice(0, ci) : line
  const comment = ci >= 0 ? line.slice(ci) : ''

  TOKEN.lastIndex = 0
  let html = ''
  let match

  while ((match = TOKEN.exec(code)) !== null) {
    const [full, dir, label, hex, num, word, punct] = match
    if (dir) {
      html += `<span class="hl-dir">${esc(full)}</span>`
    } else if (label) {
      html += `<span class="hl-label">${esc(full)}</span>`
    } else if (hex || num) {
      html += `<span class="hl-num">${esc(full)}</span>`
    } else if (word) {
      const w = word.toLowerCase()
      if (OPCODES.has(w)) html += `<span class="hl-op">${esc(word)}</span>`
      else if (isReg(w))  html += `<span class="hl-reg">${esc(word)}</span>`
      else html += esc(word)
    } else if (punct) {
      html += `<span class="hl-punct">${esc(full)}</span>`
    } else {
      html += esc(full)
    }
  }

  if (comment) html += `<span class="hl-comment">${esc(comment)}</span>`
  return html
}

export function highlight(code) {
  return code.split('\n').map(highlightLine)
}
