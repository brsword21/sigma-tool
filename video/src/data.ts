export const prompt = 'Słuchawki podobne do AirPods Pro, z dobrym ANC, ale tańsze';

export const products = [
  {brand: 'Sony', model: 'WF-1000XM5', price: '520 zł', note: 'Najpełniejszy zamiennik AirPods Pro', accent: '#1769ff'},
  {brand: 'Samsung', model: 'Galaxy Buds2 Pro', price: '310 zł', note: 'Najlepsza wartość', accent: '#8c6cff'},
  {brand: 'Bose', model: 'QuietComfort Earbuds II', price: '460 zł', note: 'Referencyjne ANC', accent: '#2f8f70'},
  {brand: 'Nothing', model: 'Ear (2)', price: '250 zł', note: 'Najniższy próg wejścia', accent: '#f06f5b'},
] as const;

export const offers = [
  {rank: '01', title: 'Sony WF-1000XM5, czarne, komplet', price: '479 zł', score: 87, warranty: '3 miesiące', returns: '14 dni', seller: '4.8 / 5', recommended: true},
  {rank: '02', title: 'Sony WF-1000XM5 z etui', price: '419 zł', score: 81, warranty: 'brak danych', returns: 'brak danych', seller: 'brak danych', recommended: false},
  {rank: '03', title: 'Sony WF-1000XM5 odnowione', price: '549 zł', score: 76, warranty: '12 miesięcy', returns: '30 dni', seller: '4.9 / 5', recommended: false},
] as const;
