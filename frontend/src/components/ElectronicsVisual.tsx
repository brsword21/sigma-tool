export function ElectronicsVisual({ variant = 0 }: { variant?: number }) {
  const themes = ['visual-blue', 'visual-graphite', 'visual-silver', 'visual-sand']
  return (
    <div className={`electronics-visual ${themes[variant % themes.length]}`} aria-hidden="true">
      <svg viewBox="0 0 520 390" role="presentation">
        <defs>
          <linearGradient id={`device-${variant}`} x1="0" y1="0" x2="1" y2="1">
            <stop stopColor="currentColor" stopOpacity=".96" />
            <stop offset="1" stopColor="currentColor" stopOpacity=".62" />
          </linearGradient>
          <filter id={`shadow-${variant}`} x="-30%" y="-30%" width="160%" height="180%">
            <feDropShadow dx="0" dy="22" stdDeviation="20" floodColor="#101114" floodOpacity=".14" />
          </filter>
        </defs>
        <g filter={`url(#shadow-${variant})`}>
          <rect x="80" y="72" width="174" height="246" rx="30" fill={`url(#device-${variant})`} />
          <rect x="98" y="96" width="138" height="184" rx="12" fill="#f8fafc" opacity=".92" />
          <path d="M158 298h20" stroke="#fff" strokeWidth="7" strokeLinecap="round" opacity=".7" />
          <path d="M278 142h111a24 24 0 0 1 24 24v113H278z" fill="#f8fafc" stroke="currentColor" strokeWidth="14" />
          <path d="M254 308h184l-17 24H271z" fill={`url(#device-${variant})`} />
          <circle cx="385" cy="89" r="34" fill={`url(#device-${variant})`} />
          <circle cx="385" cy="89" r="13" fill="#f8fafc" opacity=".9" />
        </g>
      </svg>
      <span className="visual-orbit" />
      <span className="visual-dot visual-dot--one" />
      <span className="visual-dot visual-dot--two" />
    </div>
  )
}
