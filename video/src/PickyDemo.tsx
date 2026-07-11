import {AbsoluteFill, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {offers, products, prompt} from './data';

const clamp = (value: number, start: number, end: number) => Math.max(start, Math.min(end, value));
const reveal = (frame: number, from: number, duration = 18) => interpolate(frame, [from, from + duration], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

const Fade = ({children, from = 0, y = 24, className = ''}: {children: React.ReactNode; from?: number; y?: number; className?: string}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const progress = spring({frame: Math.max(0, frame - from), fps, config: {damping: 16, stiffness: 120}});
  return <div className={className} style={{opacity: progress, transform: `translateY(${(1 - progress) * y}px)`}}>{children}</div>;
};

const AppShell = ({children, camera = 'wide', working = false}: {children: React.ReactNode; camera?: 'wide' | 'composer' | 'cards' | 'offers' | 'detail'; working?: boolean}) => (
  <AbsoluteFill className="scene-bg">
    <div className={`camera camera--${camera}`}>
      <div className="app-window">
        <header className="topbar"><div className="brand"><b>P</b><span>Picky</span></div><div className={`agent-status ${working ? 'is-working' : ''}`}><i />{working ? 'agent działa' : 'agent gotowy'}</div></header>
        <div className="demo-strip"><strong>Tryb demonstracyjny</strong><span>Przygotowane dane przykładowe</span></div>
        {children}
      </div>
    </div>
  </AbsoluteFill>
);

const Intro = () => <section className="left-panel intro"><p className="eyebrow">Agent do używanej elektroniki</p><h1>Znajdź elektronikę,<br/><em>którą warto kupić.</em></h1><p>Jedna potrzeba. Kilka sprawdzonych kierunków. Jedna decyzja.</p></section>;

const Composer = ({text, sent = false}: {text: string; sent?: boolean}) => <div className={`composer ${sent ? 'composer--sent' : ''}`}><button>＋</button><div className="composer-text">{text}<span className="caret" /></div><button className="send">↑</button></div>;

const PromptScene = () => {
  const frame = useCurrentFrame();
  const typed = prompt.slice(0, Math.floor(interpolate(frame, [32, 168], [0, prompt.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})));
  const sent = frame > 165;
  return <AppShell camera={frame < 165 ? 'composer' : 'wide'}><div className="workspace"><div className="conversation"><Intro/><Fade from={18} className="example-pills"><span>Samsung S25 do 2200 zł</span><span>Laptop z baterią powyżej 80%</span></Fade><div className="composer-wrap"><Composer text={typed} sent={sent}/></div></div><div className="empty-state"><div className="orb">⌁</div><p>Powiedz, czego potrzebujesz.<br/><b>Picky znajdzie sensowne kierunki.</b></p></div></div></AppShell>;
};

const Headphones = ({accent}: {accent: string}) => <div className="headphones" style={{'--accent': accent} as React.CSSProperties}><div /><div /></div>;

const ProductSelectionScene = () => {
  const frame = useCurrentFrame();
  return <AppShell camera={frame > 175 ? 'cards' : 'wide'}><div className="workspace"><div className="conversation selection-conversation"><div className="messages"><Fade from={0}><div className="message user"><label>Ty</label><p>{prompt}</p></div></Fade><Fade from={26}><div className="message"><label>Picky</label><p>Znalazłem modele, które mają sens. Wybierzmy kierunek.</p></div></Fade></div><div className="composer-wrap"><Composer text=""/></div></div><section className="results-panel"><Fade from={12}><p className="eyebrow">Etap 1 · wybierz kierunek</p><div className="result-heading"><h2>4 modele, które<br/>mają sens</h2><span>To nie jest jeszcze ranking ofert</span></div><div className="directions"><b>Najlepsza wartość</b><span>Najbardziej podobne</span><span>Najlepsza jakość</span></div></Fade><div className="product-grid">{products.map((product, index) => <Fade from={42 + index * 25} key={product.model} className={`product-card ${index === 0 ? 'product-card--focus' : ''}`}><div className="product-visual"><small>{product.brand}</small><Headphones accent={product.accent}/></div><div className="product-copy"><strong>{product.model}</strong><b>{product.price}</b><p>{product.note}</p>{index === 0 && <button>Sprawdź konkretne oferty <i>↗</i></button>}</div></Fade>)}</div></section></div></AppShell>;
};

const VerificationScene = () => {
  const frame = useCurrentFrame();
  const stages = ['Rozpoznanie wybranego modelu', 'Połączenie ze źródłami ofert', 'Odrzucanie obcych modeli i akcesoriów'];
  return <AppShell camera="wide" working><div className="workspace"><div className="conversation verification-copy"><div className="message user"><label>Ty</label><p>{prompt}</p></div><div className="message"><label>Picky</label><p>Wybrałeś Sony WF-1000XM5.</p></div><div className="composer-wrap"><Composer text=""/></div></div><section className="verification"><div className="scan-orb"><div className="scan-icon">⌁</div></div><Fade from={10}><p className="eyebrow">Etap 2 · konkretne oferty</p><h2>Weryfikuję oferty,<br/>ceny i dokładny model.</h2></Fade><ul>{stages.map((stage, index) => {const state = frame > 64 + index * 90 ? 'done' : frame > 26 + index * 88 ? 'active' : ''; return <li className={state} key={stage}><i>{state === 'done' ? '✓' : ''}</i>{stage}</li>;})}</ul></section></div></AppShell>;
};

const Score = ({label, value, delay = 0}: {label: string; value: number; delay?: number}) => {
  const frame = useCurrentFrame();
  const width = Math.round(value * reveal(frame, delay, 28));
  return <div className="score"><span>{label}</span><i><b style={{width: `${width}%`}} /></i><strong>{value}/100</strong></div>;
};

const Offer = ({offer, index, focused = false, final = false}: {offer: typeof offers[number]; index: number; focused?: boolean; final?: boolean}) => {
  const frame = useCurrentFrame();
  const enter = spring({frame: Math.max(0, frame - index * 34), fps: 30, config: {damping: 17, stiffness: 110}});
  const finalBoost = final && offer.warranty === '12 miesięcy' ? spring({frame: Math.max(0, frame - 135), fps: 30, config: {damping: 14, stiffness: 90}}) : 0;
  return <article className={`offer ${focused ? 'offer--focus' : ''} ${final && offer.warranty === '12 miesięcy' ? 'offer--new-best' : ''}`} style={{opacity: enter, transform: `translateY(${(1 - enter) * 42 - finalBoost * 3}px) scale(${1 + finalBoost * .012})`}}><aside>{String(index + 1).padStart(2, '0')}</aside><div className="offer-body"><div className="offer-top"><div>{(offer.recommended || (final && offer.warranty === '12 miesięcy')) && <small className="best-badge">Najlepszy wybór</small>}<h3>{offer.title}</h3><p>WF-1000XM5 · stan: bardzo dobry</p></div><div className="price"><strong>{offer.price}</strong><span>Warszawa</span></div></div><div className="evidence"><div><Score label="Dopasowanie produktu" value={91} delay={index * 34 + 16}/><Score label="Jakość oferty" value={offer.score === 87 ? 88 : offer.score === 81 ? 80 : 72} delay={index * 34 + 28}/><Score label="Sprzedawca" value={offer.seller === '4.9 / 5' ? 94 : offer.seller === '4.8 / 5' ? 82 : 72} delay={index * 34 + 40}/></div><p><small>Dlaczego ta oferta</small>{offer.warranty === '12 miesięcy' ? 'Najbezpieczniejszy sprzedawca i roczna gwarancja.' : 'Właściwy wariant, dobry stan i atrakcyjna cena.'}</p></div><div className="trust"><div><span>Gwarancja</span><b>{offer.warranty}</b></div><div><span>Zwrot</span><b>{offer.returns}</b></div><div><span>Sprzedawca</span><b>{offer.seller}</b></div><div><span>Pewność</span><b>{offer.score}%</b></div></div></div></article>;
};

const ResultsHeader = () => <div className="offers-header"><div><p className="eyebrow">Etap 2 · ranking ofert</p><h2>Sony WF-1000XM5</h2></div><div><span>Nowe od</span><b>799 zł</b></div></div>;

const OfferRankingScene = () => <AppShell camera="offers"><div className="workspace"><div className="conversation results-conversation"><div className="message user"><label>Ty</label><p>{prompt}</p></div><div className="message"><label>Picky</label><p>Sprawdziłem konkretne ogłoszenia i porównałem ich jakość.</p></div><div className="composer-wrap"><Composer text=""/></div></div><section className="offers-panel"><ResultsHeader/>{offers.map((offer, index) => <Offer offer={offer} index={index} focused={index === 0} key={offer.rank}/>)}</section></div></AppShell>;

const PriorityUpdateScene = () => {
  const frame = useCurrentFrame();
  const update = 'Ważniejsza jest gwarancja niż najniższa cena';
  const text = update.slice(0, Math.floor(interpolate(frame, [8, 115], [0, update.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})));
  const reordered = [offers[2], offers[0], offers[1]];
  return <AppShell camera={frame < 180 ? 'detail' : 'offers'}><div className="workspace"><div className="conversation results-conversation"><div className="message user"><label>Ty</label><p>{prompt}</p></div><div className="message"><label>Picky</label><p>Sprawdziłem konkretne ogłoszenia i porównałem ich jakość.</p></div><div className="composer-wrap"><Composer text={text} sent={frame > 125}/></div></div><section className="offers-panel"><ResultsHeader/><div className="priority-note" style={{opacity: clamp((frame - 132) / 22, 0, 1)}}>Priorytet: gwarancja <i>✓</i></div>{reordered.map((offer, index) => <Offer offer={offer} index={index} final key={offer.rank}/>)}</section></div></AppShell>;
};

export const PickyDemo = () => <AbsoluteFill><Sequence from={0} durationInFrames={180}><PromptScene/></Sequence><Sequence from={180} durationInFrames={240}><ProductSelectionScene/></Sequence><Sequence from={420} durationInFrames={360}><VerificationScene/></Sequence><Sequence from={780} durationInFrames={660}><OfferRankingScene/></Sequence><Sequence from={1440} durationInFrames={360}><PriorityUpdateScene/></Sequence></AbsoluteFill>;
