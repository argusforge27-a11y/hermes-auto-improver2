// Themes = palette + font mood. Pick one in script.json "theme". Every scene reads colours from the theme (lib.js TH),
// so a video can be re-themed by changing one word.
export const THEMES = {
  // dark, modern documentary (default for tech, business, mystery, science)
  midnight: {
    name: 'midnight', bg: '#0B1220', bg2: '#15243C', text: '#F2F5FA', muted: '#9AA8BD', accent: '#35D0BA', accent2: '#FFB547', accent3: '#6C8CFF',
    danger: '#FF5C6C', good: '#4ADE80', card: '#16233A', cardEdge: '#2A3C5C', ink: '#05080F', grid: 'rgba(255,255,255,0.055)',
    land: '#1B2B45', landEdge: '#2F4670', sea: '#0B1220', shadow: 'rgba(0,0,0,0.45)', onAccent: '#05080F', backdrop: 'drift', serif: false,
    capBox: 'rgba(5,8,15,0.74)', capText: '#FFFFFF', capHi: '#FFB547',
  },
  // bright, clean explainer (finance, productivity, health, how-it-works)
  daylight: {
    name: 'daylight', bg: '#F7F8FB', bg2: '#E4EAF6', text: '#14182B', muted: '#586178', accent: '#4F46E5', accent2: '#F97316', accent3: '#0EA5A4',
    danger: '#E11D48', good: '#16A34A', card: '#FFFFFF', cardEdge: '#D3DAE8', ink: '#14182B', grid: 'rgba(20,24,43,0.06)',
    land: '#D9E1F0', landEdge: '#B3BFD6', sea: '#F2F5FB', shadow: 'rgba(30,40,80,0.18)', onAccent: '#FFFFFF', backdrop: 'dots', serif: false,
    capBox: 'rgba(20,24,43,0.84)', capText: '#FFFFFF', capHi: '#FFC24B',
  },
  // warm paper and serif headings (history, culture, biography, true stories)
  parchment: {
    name: 'parchment', bg: '#F1E6CF', bg2: '#E3D2AB', text: '#2A1D12', muted: '#76634A', accent: '#A4262C', accent2: '#B8860B', accent3: '#2F5D62',
    danger: '#8F1D21', good: '#3F6B3A', card: '#F8F0DD', cardEdge: '#C9B58A', ink: '#2A1D12', grid: 'rgba(42,29,18,0.07)',
    land: '#D6C391', landEdge: '#A88F57', sea: '#EADCB9', shadow: 'rgba(60,40,10,0.28)', onAccent: '#F8F0DD', backdrop: 'paper', serif: true,
    capBox: 'rgba(42,29,18,0.84)', capText: '#FBF4E3', capHi: '#E9B949',
  },
};
