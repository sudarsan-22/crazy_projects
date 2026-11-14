/* KC Customs "Design your dream bike": option catalogue.
   Every option lists the KC Customs video that shows it (`src`). To add an option or a model,
   add an entry here; the studio UI and the WhatsApp summary pick it up automatically.
   Options with no KC evidence (e.g. matte, metallic) are deliberately NOT listed. */

export const MODELS = [
  { id: 'rx100', name: 'Yamaha RX100', short: 'RX100', blurb: 'The two-stroke icon. Full custom paint is a KC staple.', hasCowl: false, src: ['HcIpbg8CbIs', 'D46gpxd8nA4'],
    sample: { color: '#7DC42B', finish: 'candy', graphic: 'splash', accent: '#C4161C' } },
  { id: 'rxz', name: 'Yamaha RXZ', short: 'RXZ', blurb: 'Where KC began. 6-speed builds and Malaysian-style rebuilds.', hasCowl: true, src: ['vRxt4pK-0wA', 'ZNegxLjxVZA', 'Glsa5eccRBI'],
    sample: { color: '#813D8A', finish: 'candy', graphic: 'angular', accent: '#C9A14A' } },
  { id: 'rx115', name: 'Yamaha RX115', short: 'RX115', blurb: 'Full custom builds with KC-style layered graphics.', hasCowl: true, src: ['X8-hUFeROlM', 'P08bwaDRwRc'],
    sample: { color: '#1E4FD8', finish: 'gloss', graphic: 'angular', accent: '#7DC42B' } },
];

/* Base colours drawn from real KC builds (custom paint can match any colour; a picker is offered too). */
export const COLORS = [
  { id: 'chromered', name: 'Chrome Red', hex: '#C4161C', seen: 'RX King chrome red (oWhoaVNHnH4)' },
  { id: 'candyred', name: 'Candy Red', hex: '#B3122E', seen: 'R15 V3 candy red (cq1YADod7Z8)' },
  { id: 'candyblue', name: 'Candy Blue', hex: '#1E4FD8', seen: 'R15 V3 candy blue (cq1YADod7Z8)' },
  { id: 'purple', name: 'KC Purple', hex: '#813D8A', seen: 'Malaysian-style RXZ (ZNegxLjxVZA)' },
  { id: 'lime', name: 'Lime Green', hex: '#7DC42B', seen: 'RX115 KC style (P08bwaDRwRc)' },
  { id: 'yellow', name: 'Racing Yellow', hex: '#F2C200', seen: 'RX King builds (Gg50_VpLoOk, jvk2rxSIMs0)' },
  { id: 'pearl', name: 'Pearl White', hex: '#EDEAE3', seen: 'Pearl white parts (cq1YADod7Z8), show RX King (kkQ9kdpLZDA)' },
  { id: 'pink', name: 'Hot Pink', hex: '#E5357F', seen: 'Show-quality RX King (kkQ9kdpLZDA)' },
  { id: 'gold', name: 'Gold', hex: '#C9A14A', seen: 'Gold parts (cq1YADod7Z8), Chetak (ht_Y0jp5r3g)' },
  { id: 'black', name: 'Gloss Black', hex: '#15161A', seen: 'Project Evergreen base (EQ3jW9j3Fb8)' },
];

export const FINISHES = [
  { id: 'gloss', name: 'Gloss', note: 'PU top coat + high-quality clear coat', src: 'tWAe6b1ONRU' },
  { id: 'candy', name: 'Candy', note: 'Deep transparent colour', src: 'cq1YADod7Z8' },
  { id: 'chrome', name: 'Chrome', note: 'Mirror base under colour', src: 'oWhoaVNHnH4' },
  { id: 'pearl', name: 'Pearl', note: 'Soft shimmer', src: 'cq1YADod7Z8' },
];

export const GRAPHICS = [
  { id: 'none', name: 'Clean', note: 'Paint only' },
  { id: 'stripes', name: 'Twin stripes', note: 'Decal-style stripes', src: 'R-jAihOHzc0' },
  { id: 'angular', name: 'KC layers', note: 'Angular layered graphics', src: 'X8-hUFeROlM' },
  { id: 'splash', name: 'Colour splash', note: 'Multi-colour airbrush', src: 'HcIpbg8CbIs' },
  { id: 'flames', name: 'Flames', note: 'Airbrushed flames', src: 'FJHeepFVawY' },
  { id: 'lettering', name: 'Lettering', note: 'Your name or text', src: 'q9GEdi3sdlY' },
];

/* Airbrush artwork: references are crops of real KC pieces. A customer's artwork is painted fresh. */
export const ARTWORK = [
  { id: 'none', name: 'No artwork' },
  { id: 'deity-murugan', name: 'Deity panel (Murugan)', tex: 'art-murugan', src: 'ZNegxLjxVZA' },
  { id: 'deity-kali', name: 'Deity panel (Kali)', tex: 'art-kali', src: '66u_MtxUcVE' },
  { id: 'skull-flame', name: 'Skull & flames', tex: 'art-skullflame', src: 'FJHeepFVawY' },
  { id: 'cartoon', name: 'Cartoon badge', tex: 'art-cartoon', src: 'biiIjij08T4' },
  { id: 'caricature', name: 'Caricature', tex: 'art-caricature', src: 'DW4hmWpu3SM' },
  { id: 'script', name: 'Script lettering', tex: 'art-lettering', src: 'q9GEdi3sdlY' },
];
export const PLACEMENTS = [
  { id: 'side', name: 'Side panels' },
  { id: 'tank', name: 'Fuel tank' },
];

export const HYDRO = [
  { id: 'carbon', name: 'Carbon look', tex: null, src: 'cq1YADod7Z8' },
  { id: 'skulls', name: 'Skulls', tex: 'hydro-skulls', src: 'GnQmHIi4ZOE' },
  { id: 'roses', name: 'Roses & skulls', tex: 'hydro-roses', src: 'gFQ1GW-Y46s' },
  { id: 'sugarskull', name: 'Sugar skull', tex: 'hydro-sugarskull', src: 'J6uavvancpw' },
  { id: 'stickerbomb', name: 'Sticker bomb', tex: 'hydro-stickerbomb', src: 'J6uavvancpw' },
];

/* Paintable components. `cowl` only exists on models with a headlight cowl. */
export const PARTS = [
  { id: 'tank', name: 'Fuel tank' },
  { id: 'side', name: 'Side panels' },
  { id: 'frontGuard', name: 'Front mudguard' },
  { id: 'rearGuard', name: 'Rear mudguard / tail' },
  { id: 'cowl', name: 'Headlight cowl', needs: 'hasCowl' },
  { id: 'engine', name: 'Engine cover', src: 'Ac0JbaZAokQ' },
];
export const PART_SOURCES = [
  { id: 'main', name: 'Main colour' },
  { id: 'accent', name: 'Accent colour' },
  { id: 'hydro', name: 'Hydro dip' },
  { id: 'stock', name: 'Stock' },
];
export const RIMS = [
  { id: 'chrome', name: 'Stock chrome', hex: '#C9CDD3' },
  { id: 'gold', name: 'Gold', hex: '#C9A14A', src: 'X8-hUFeROlM' },
  { id: 'pink', name: 'Pink', hex: '#E5357F', src: 'kkQ9kdpLZDA' },
  { id: 'main', name: 'Match main colour', src: 'd4Amxf5w4BE' },
];

/* Enquiry-only modifications (not drawn). `models` limits where they are offered. */
export const MODS = [
  { id: 'restoration', name: 'Full restoration', models: ['rx100', 'rxz', 'rx115'], src: 'EOkal7lTLC0' },
  { id: 'imported', name: 'Imported performance / CNC parts', models: ['rx100', 'rxz', 'rx115'], src: 'MCiFikHUXT0' },
  { id: 'exhaust', name: 'Imported exhaust', models: ['rx100', 'rxz'], src: 'TTO78NUK2AU' },
  { id: 'sixspeed', name: '4 → 6-speed conversion', models: ['rxz'], src: 'Glsa5eccRBI' },
  { id: 'malaysian', name: 'Malaysian-style conversion', models: ['rxz'], src: 'ZNegxLjxVZA' },
  { id: 'rxking', name: 'RX King-style conversion', models: ['rx100'], src: 'EQ3jW9j3Fb8' },
];

export const DEFAULTS = (model) => {
  const m = MODELS.find((x) => x.id === model) || MODELS[0];
  return {
    v: 1, model: m.id,
    color: m.sample.color, finish: m.sample.finish, accent: m.sample.accent,
    graphic: m.sample.graphic, text: '', art: 'none', place: 'side', hydro: 'carbon',
    parts: { tank: 'main', side: 'main', frontGuard: 'stock', rearGuard: 'stock', cowl: 'main', engine: 'stock' },
    rims: 'chrome', mods: [], note: '',
  };
};

export const STOCK = (model) => ({
  ...DEFAULTS(model), color: '#15161A', finish: 'gloss', accent: '#C9CDD3', graphic: 'none', art: 'none',
  parts: { tank: 'main', side: 'main', frontGuard: 'stock', rearGuard: 'stock', cowl: 'main', engine: 'stock' }, rims: 'chrome', mods: [],
});

export const PHONE = '919677184462';
