export function HeadphoneVisual({ variant = 0 }: { variant?: number }) {
  const themes = ['visual-blue', 'visual-graphite', 'visual-silver', 'visual-sand']
  return (
    <div className={`headphone-visual ${themes[variant % themes.length]}`} aria-hidden="true">
      <svg viewBox="0 0 520 390" role="presentation">
        <defs>
          <linearGradient id={`shell-${variant}`} x1="0" y1="0" x2="1" y2="1"><stop stopColor="currentColor" stopOpacity=".96"/><stop offset="1" stopColor="currentColor" stopOpacity=".62"/></linearGradient>
          <filter id={`shadow-${variant}`} x="-30%" y="-30%" width="160%" height="180%"><feDropShadow dx="0" dy="22" stdDeviation="20" floodColor="#101114" floodOpacity=".14"/></filter>
        </defs>
        <g filter={`url(#shadow-${variant})`}>
          <path d="M118 189c8-92 57-144 142-144s134 52 142 144" fill="none" stroke="currentColor" strokeWidth="34" strokeLinecap="round" opacity=".88"/>
          <path d="M121 190c5-60 32-112 75-132" fill="none" stroke="#fff" strokeWidth="6" strokeLinecap="round" opacity=".48"/>
          <g transform="rotate(6 110 249)"><rect x="67" y="177" width="103" height="150" rx="48" fill={`url(#shell-${variant})`}/><rect x="90" y="201" width="56" height="102" rx="28" fill="#0d1117" opacity=".86"/><path d="M87 207c17-24 42-29 61-13" fill="none" stroke="#fff" strokeWidth="5" opacity=".45"/></g>
          <g transform="rotate(-6 410 249)"><rect x="350" y="177" width="103" height="150" rx="48" fill={`url(#shell-${variant})`}/><rect x="374" y="201" width="56" height="102" rx="28" fill="#0d1117" opacity=".86"/><path d="M371 207c17-24 42-29 61-13" fill="none" stroke="#fff" strokeWidth="5" opacity=".45"/></g>
        </g>
      </svg>
      <span className="visual-orbit" />
      <span className="visual-dot visual-dot--one" />
      <span className="visual-dot visual-dot--two" />
    </div>
  )
}
