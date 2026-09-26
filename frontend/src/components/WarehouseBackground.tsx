import './WarehouseBackground.css'

/* ─────────────────────────────────────────────────────────────────
   WarehouseBackground
   Pure visual component – renders behind the login card.
   NO auth logic. NO state. NO side-effects.
───────────────────────────────────────────────────────────────── */
export default function WarehouseBackground() {
  return (
    <div className="wh-root" aria-hidden="true">

      {/* ── FLOOR ── */}
      <div className="wh-floor" />

      {/* ── FLOOR SAFETY LINES ── */}
      <svg className="wh-safety-lines" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        {/* centre aisle */}
        <line x1="580" y1="560" x2="580" y2="900" stroke="#f59e0b" strokeWidth="3" strokeDasharray="40 18" opacity="0.55" />
        <line x1="860" y1="560" x2="860" y2="900" stroke="#f59e0b" strokeWidth="3" strokeDasharray="40 18" opacity="0.55" />
        {/* cross line */}
        <line x1="0" y1="640" x2="1440" y2="640" stroke="#f59e0b" strokeWidth="2" strokeDasharray="60 24" opacity="0.35" />
        {/* pedestrian strips */}
        {[0,1,2,3,4,5,6,7].map(i => (
          <rect key={i} x={580} y={660 + i*30} width={280} height={14} fill="#f59e0b" opacity="0.18" />
        ))}
      </svg>

      {/* ── LEFT RACK BLOCK ── */}
      <svg className="wh-rack wh-rack-left" viewBox="0 0 420 620" preserveAspectRatio="xMidYMid meet">
        <RackUnit x={0} y={0} label="RACK A" cols={4} rows={5} seed={1} />
      </svg>

      {/* ── RIGHT RACK BLOCK ── */}
      <svg className="wh-rack wh-rack-right" viewBox="0 0 420 620" preserveAspectRatio="xMidYMid meet">
        <RackUnit x={0} y={0} label="RACK B" cols={4} rows={5} seed={7} />
      </svg>

      {/* ── BACK WALL RACKS (depth) ── */}
      <svg className="wh-rack wh-rack-back-left" viewBox="0 0 320 380" preserveAspectRatio="xMidYMid meet">
        <RackUnit x={0} y={0} label="RACK C" cols={5} rows={3} seed={13} small />
      </svg>
      <svg className="wh-rack wh-rack-back-right" viewBox="0 0 320 380" preserveAspectRatio="xMidYMid meet">
        <RackUnit x={0} y={0} label="RACK D" cols={5} rows={3} seed={19} small />
      </svg>

      {/* ── CEILING STRUCTURE ── */}
      <svg className="wh-ceiling" viewBox="0 0 1440 260" preserveAspectRatio="xMidYMid slice">
        {/* trusses */}
        {[180,460,740,1020,1300].map((x,i)=>(
          <g key={i}>
            <line x1={x} y1={0} x2={x-60} y2={260} stroke="#374151" strokeWidth="3" opacity="0.6"/>
            <line x1={x} y1={0} x2={x+60} y2={260} stroke="#374151" strokeWidth="3" opacity="0.6"/>
            <line x1={x-60} y1={260} x2={x+60} y2={260} stroke="#374151" strokeWidth="2" opacity="0.5"/>
          </g>
        ))}
        {/* horizontal beams */}
        <line x1="0" y1="40" x2="1440" y2="40" stroke="#4b5563" strokeWidth="4" opacity="0.5"/>
        <line x1="0" y1="120" x2="1440" y2="120" stroke="#4b5563" strokeWidth="2" opacity="0.3"/>
        {/* ceiling lights */}
        {[200,480,720,960,1240].map((x,i)=>(
          <g key={i} className="wh-ceiling-light">
            <rect x={x-30} y={35} width={60} height={10} rx={3} fill="#d1d5db" opacity="0.9"/>
            <ellipse cx={x} cy={42} rx={120} ry={60} fill="url(#lightCone)" opacity="0.13"/>
          </g>
        ))}
        <defs>
          <radialGradient id="lightCone" cx="50%" cy="0%" r="100%">
            <stop offset="0%" stopColor="#bfdbfe" stopOpacity="1"/>
            <stop offset="100%" stopColor="#bfdbfe" stopOpacity="0"/>
          </radialGradient>
        </defs>
      </svg>

      {/* ── AMBIENT LIGHT POOLS ON FLOOR ── */}
      <div className="wh-light-pool wh-lp1" />
      <div className="wh-light-pool wh-lp2" />
      <div className="wh-light-pool wh-lp3" />

      {/* ── FORKLIFT (CSS animated) ── */}
      <div className="wh-forklift-wrap">
        <svg className="wh-forklift" viewBox="0 0 120 80" fill="none">
          {/* body */}
          <rect x="30" y="30" width="70" height="38" rx="4" fill="#1e40af" opacity="0.85"/>
          {/* cab */}
          <rect x="75" y="14" width="25" height="32" rx="3" fill="#1d4ed8" opacity="0.9"/>
          <rect x="78" y="17" width="19" height="16" rx="2" fill="#93c5fd" opacity="0.6"/>
          {/* mast */}
          <rect x="18" y="10" width="6" height="58" rx="2" fill="#374151"/>
          <rect x="24" y="10" width="6" height="58" rx="2" fill="#4b5563"/>
          {/* forks */}
          <rect x="4" y="55" width="20" height="4" rx="1" fill="#6b7280"/>
          <rect x="4" y="62" width="20" height="4" rx="1" fill="#6b7280"/>
          {/* pallet on forks */}
          <rect x="2" y="46" width="26" height="9" rx="1" fill="#92400e" opacity="0.8"/>
          <rect x="4" y="38" width="22} " height="8" rx="1" fill="#b45309" opacity="0.7"/>
          <rect x="5" y="30" width="20" height="8" rx="1" fill="#d97706" opacity="0.6"/>
          {/* box on pallet */}
          <rect x="6" y="22" width="18" height="10" rx="1" fill="#6b7280" opacity="0.7"/>
          {/* wheels */}
          <circle cx="45" cy="70" r="9" fill="#111827"/>
          <circle cx="45" cy="70" r="5" fill="#374151"/>
          <circle cx="85" cy="70" r="9" fill="#111827"/>
          <circle cx="85" cy="70" r="5" fill="#374151"/>
          <circle cx="100" cy="70" r="7" fill="#111827"/>
          <circle cx="100" cy="70" r="4" fill="#374151"/>
          {/* warning stripe */}
          <rect x="30" y="62" width="70" height="6" rx="1" fill="#f59e0b" opacity="0.5"/>
          {/* headlight */}
          <circle cx="100" cy="40" r="4" fill="#fde68a" opacity="0.8"/>
        </svg>
      </div>

      {/* ── PALLETS ON FLOOR ── */}
      <svg className="wh-pallets" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        <Pallet x={90} y={720} label="A1" />
        <Pallet x={200} y={750} label="A2" />
        <Pallet x={1150} y={710} label="B1" />
        <Pallet x={1270} y={745} label="B2" />
        {/* stacked boxes far back */}
        <BoxStack x={440} y={580} opacity={0.45}/>
        <BoxStack x={960} y={575} opacity={0.45}/>
      </svg>

      {/* ── INVENTORY FLOW LINES (SVG animated) ── */}
      <svg className="wh-flow-lines" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        {/* Receiving → Storage → Pick → Pack → Dispatch */}
        <path
          d="M 200 820 Q 280 700 360 620 Q 440 540 580 500 Q 700 460 720 400 Q 740 340 860 400 Q 980 460 1060 540 Q 1160 620 1240 820"
          stroke="#38bdf8" strokeWidth="1.5" fill="none" opacity="0.35"
          strokeDasharray="8 6"
          className="wh-flow-path"
        />
        {/* vertical drop lines at nodes */}
        <line x1="200" y1="820" x2="200" y2="760" stroke="#38bdf8" strokeWidth="1" opacity="0.3" strokeDasharray="4 4"/>
        <line x1="720" y1="400" x2="720" y2="340" stroke="#38bdf8" strokeWidth="1" opacity="0.3" strokeDasharray="4 4"/>
        <line x1="1240" y1="820" x2="1240" y2="760" stroke="#38bdf8" strokeWidth="1" opacity="0.3" strokeDasharray="4 4"/>
        {/* travelling dots */}
        <circle r="3.5" fill="#7dd3fc" opacity="0.9">
          <animateMotion dur="7s" repeatCount="indefinite" keySplines="0.42 0 0.58 1" calcMode="spline">
            <mpath href="#flowPath"/>
          </animateMotion>
        </circle>
        <circle r="2.5" fill="#bae6fd" opacity="0.7">
          <animateMotion dur="7s" begin="2.3s" repeatCount="indefinite" keySplines="0.42 0 0.58 1" calcMode="spline">
            <mpath href="#flowPath"/>
          </animateMotion>
        </circle>
        <defs>
          <path id="flowPath" d="M 200 820 Q 280 700 360 620 Q 440 540 580 500 Q 700 460 720 400 Q 740 340 860 400 Q 980 460 1060 540 Q 1160 620 1240 820"/>
        </defs>
      </svg>

      {/* ── HUD PANELS ── */}
      <div className="wh-hud wh-hud-tl">
        <HudPanel icon="📦" label="INCOMING STOCK" value="Receiving Bay A" sub="RACK A1 · A2" pulse />
      </div>
      <div className="wh-hud wh-hud-tr">
        <HudPanel icon="🚚" label="OUTGOING STOCK" value="Dispatch Lane B" sub="RACK B1 · B2" />
      </div>
      <div className="wh-hud wh-hud-bl">
        <HudPanel icon="🏭" label="WAREHOUSE A" value="Stock Available" sub="Locations: 24 active" pulse />
      </div>
      <div className="wh-hud wh-hud-br">
        <HudPanel icon="📍" label="INVENTORY LOCATIONS" value="Rack A · Rack B" sub="12 pallets tracked" />
      </div>

      {/* ── LOCATION MARKERS ── */}
      <svg className="wh-location-markers" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        <LocationPin x={145} y={680} label="A1" />
        <LocationPin x={255} y={710} label="A2" />
        <LocationPin x={1155} y={670} label="B1" />
        <LocationPin x={1275} y={705} label="B2" />
      </svg>

      {/* ── CENTER DARK VIGNETTE (protects login card) ── */}
      <div className="wh-center-vignette" />
    </div>
  )
}

/* ─── SUB-COMPONENTS ─── */

function RackUnit({ x, y, label, cols, rows, seed, small }: {
  x: number; y: number; label: string
  cols: number; rows: number; seed: number; small?: boolean
}) {
  const cw = small ? 52 : 72
  const ch = small ? 48 : 68
  const pad = small ? 6 : 10
  const W = cols * cw + pad * 2
  const H = rows * ch + 80

  const boxColors = ['#92400e','#b45309','#78350f','#6b7280','#374151','#1e3a5f','#1e40af']
  function rng(n: number) { return ((seed * 1103515245 + n * 12345) >>> 0) % 100 }

  return (
    <g transform={`translate(${x},${y})`}>
      {/* label board */}
      <rect x={0} y={0} width={W} height={28} rx={3} fill="#1e3a5f" opacity={0.9}/>
      <text x={W/2} y={19} textAnchor="middle" fontSize={small?11:13} fill="#93c5fd" fontFamily="monospace" fontWeight="bold">{label}</text>

      {/* frame */}
      <rect x={0} y={28} width={W} height={H-28} rx={2} fill="#1f2937" stroke="#374151" strokeWidth="1.5" opacity={0.85}/>

      {/* uprights */}
      {Array.from({length: cols+1},(_,i)=>(
        <rect key={i} x={pad + i*cw - 3} y={28} width={6} height={H-28} fill="#374151" opacity={0.9}/>
      ))}

      {/* shelves + boxes */}
      {Array.from({length: rows},(_,r)=>
        Array.from({length: cols},(_,c)=>{
          const idx = r*cols+c
          const bh = small ? 22 : 32
          const bw = cw - 10
          const filled = rng(idx*3+1) > 18
          const color = boxColors[rng(idx*7+3) % boxColors.length]
          const sy = 28 + 10 + r * ch
          return (
            <g key={`${r}-${c}`}>
              {/* shelf plank */}
              <rect x={pad + c*cw} y={sy + ch - 6} width={cw} height={5} fill="#4b5563" opacity={0.8}/>
              {/* box */}
              {filled && (
                <>
                  <rect x={pad + c*cw + 5} y={sy + ch - bh - 6} width={bw} height={bh} rx={2} fill={color} opacity={0.85}/>
                  {/* box label tape */}
                  <rect x={pad + c*cw + 5} y={sy + ch - bh - 6 + 6} width={bw} height={4} fill="#e5e7eb" opacity={0.3}/>
                  {/* location tag */}
                  <rect x={pad + c*cw + bw - 12} y={sy + ch - bh - 6} width={12} height={8} rx={1} fill="#1d4ed8" opacity={0.7}/>
                </>
              )}
            </g>
          )
        })
      )}
    </g>
  )
}

function Pallet({ x, y, label }: { x: number; y: number; label: string }) {
  return (
    <g>
      {/* pallet base */}
      <rect x={x} y={y+20} width={80} height={12} rx={2} fill="#92400e" opacity={0.7}/>
      <rect x={x+5} y={y+12} width={70} height={8} rx={1} fill="#78350f" opacity={0.6}/>
      {/* boxes on pallet */}
      <rect x={x+2} y={y-6} width={34} height={20} rx={2} fill="#374151" opacity={0.75}/>
      <rect x={x+38} y={y-6} width={34} height={20} rx={2} fill="#4b5563" opacity={0.75}/>
      <rect x={x+12} y={y-24} width={50} height={20} rx={2} fill="#1e3a5f" opacity={0.7}/>
      {/* label */}
      <rect x={x+26} y={y-28} width={28} height={12} rx={2} fill="#1d4ed8" opacity={0.85}/>
      <text x={x+40} y={y-19} textAnchor="middle" fontSize={9} fill="#bfdbfe" fontFamily="monospace" fontWeight="bold">{label}</text>
    </g>
  )
}

function BoxStack({ x, y, opacity }: { x: number; y: number; opacity: number }) {
  return (
    <g opacity={opacity}>
      <rect x={x} y={y+20} width={60} height={12} rx={1} fill="#92400e"/>
      <rect x={x+2} y={y+4} width={56} height={18} rx={2} fill="#374151"/>
      <rect x={x+2} y={y-12} width={56} height={18} rx={2} fill="#4b5563"/>
      <rect x={x+8} y={y-28} width={44} height={18} rx={2} fill="#1e3a5f"/>
    </g>
  )
}

function HudPanel({ icon, label, value, sub, pulse }: {
  icon: string; label: string; value: string; sub: string; pulse?: boolean
}) {
  return (
    <div className={`wh-hud-panel ${pulse ? 'wh-hud-pulse' : ''}`}>
      <div className="wh-hud-header">
        <span className="wh-hud-icon">{icon}</span>
        <span className="wh-hud-label">{label}</span>
      </div>
      <div className="wh-hud-value">{value}</div>
      <div className="wh-hud-sub">{sub}</div>
    </div>
  )
}

function LocationPin({ x, y, label }: { x: number; y: number; label: string }) {
  return (
    <g className="wh-location-pin">
      {/* pulsing ring */}
      <circle cx={x} cy={y} r={14} fill="none" stroke="#38bdf8" strokeWidth="1.5" opacity="0.5">
        <animate attributeName="r" values="10;18;10" dur="3s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.6;0.1;0.6" dur="3s" repeatCount="indefinite"/>
      </circle>
      {/* pin body */}
      <circle cx={x} cy={y} r={8} fill="#1d4ed8" opacity="0.85"/>
      <text x={x} y={y+4} textAnchor="middle" fontSize={7} fill="#bfdbfe" fontFamily="monospace" fontWeight="bold">{label}</text>
    </g>
  )
}
