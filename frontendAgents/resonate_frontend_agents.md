# Resonate — Frontend Agent Instructions

**Stack:** Next.js (App Router), Tailwind CSS, shadcn/ui, Three.js, Recharts  
**Deploy:** Vercel (one command at the end)  
**Design vibe:** Dark background (#0a0a0f), deep navy/black, electric blue + purple accent colors, glowing brain visualization. Think neuroscience meets modern SaaS — not a data dashboard, not a toy app.

---

## How to use this doc

Each section below is a self-contained task for a single agent. Give the agent:
1. The section title
2. The full section contents
3. Any relevant context from earlier sections it depends on

Run agents roughly in order — later agents depend on earlier ones.

---

## Agent 1 — Project Setup

**Task:** Set up a new Next.js project with all dependencies installed and configured.

**Instructions:**
```
Create a new Next.js 14 app with App Router using:
  npx create-next-app@latest resonate --typescript --tailwind --app --src-dir

Then install these dependencies:
  npm install three @types/three @react-three/fiber @react-three/drei
  npm install recharts
  npm install lucide-react
  npm install clsx tailwind-merge
  npx shadcn@latest init

When shadcn asks for config: use Default style, Zinc base color, CSS variables yes.

Then install these shadcn components:
  npx shadcn@latest add button card progress badge separator tabs

Set up the global CSS in src/app/globals.css:
- Background color: #0a0a0f
- Default text: white
- Accent color (CSS variable): electric blue #3b82f6
- Font: Inter (import from Google Fonts in layout.tsx)

Update tailwind.config to extend colors:
  brand: { blue: '#3b82f6', purple: '#8b5cf6', glow: '#60a5fa' }
```

---

## Agent 2 — Upload Page

**Task:** Build the video upload landing page at `/` (src/app/page.tsx).

**Depends on:** Agent 1 (project setup complete)

**Instructions:**
```
Build the upload page at src/app/page.tsx. This is the first screen users see.

Layout (dark background, centered content):
- Top: "Resonate" wordmark in white, small tagline underneath: 
  "Know exactly where your video loses viewers — backed by neuroscience."
- Center: Large drag-and-drop upload zone
  - Dashed border, rounded corners, subtle glow on hover
  - Icon: brain or upload icon (lucide-react)
  - Text: "Drop your video here" + "or click to browse"
  - Accepted formats: .mp4, .mov, .webm (show this as small text)
  - Max file size note: "15 seconds works best for demo"
- Below upload zone: a "Analyze Video" button (disabled until file selected, 
  electric blue when active, full width)
- Bottom: three small feature pills showing what it analyzes:
  "Engagement Autopsy" · "Sound-Off Score" · "Modality Balance" · "CTA Timing"

State management:
- Use useState for: selectedFile, isDragging, isUploading
- On file drop or select: show filename + file size + a thumbnail preview if possible
- On "Analyze Video" click: POST to /api/analyze with the video file as FormData,
  then redirect to /results/[jobId] (the API will return a jobId)

Styling notes:
- Upload zone background: rgba(255,255,255,0.03), border: 1px dashed rgba(255,255,255,0.15)
- On drag over: border color switches to brand blue, background slightly brighter
- Button: bg-blue-600 hover:bg-blue-500, rounded-lg, py-3, text-white font-semibold
```

---

## Agent 3 — Loading / Processing Screen

**Task:** Build the loading screen shown while Tribe v2 is running inference (~30-40 seconds).

**Depends on:** Agent 1

**Instructions:**
```
Build a loading page at src/app/results/[jobId]/loading.tsx (or as a conditional 
render inside the results page based on job status).

Layout:
- Full screen dark background
- Center: animated pulsing brain icon (use a SVG brain outline, animate with 
  CSS pulse + a slow rotating glow ring around it using Tailwind animate-spin 
  at very slow speed)
- Below brain: status text that cycles through these messages every 4 seconds:
    "Running Tribe v2 brain encoding model..."
    "Mapping 20,000 cortical vertices..."  
    "Applying Schaefer-200 brain atlas..."
    "Comparing against top creator reference pack..."
    "Generating insights..."
- Below status: a thin progress bar (indeterminate/shimmer animation, blue)
- Bottom: small text "This takes about 30–40 seconds"

Poll /api/status/[jobId] every 3 seconds. When status returns "complete", 
redirect to /results/[jobId].

Styling: 
- Brain SVG glow: drop-shadow with blue color
- Status text: text-zinc-400, transitions smoothly between messages (fade)
- Progress bar: shimmer animation left-to-right, blue gradient
```

---

## Agent 4 — Results Page Shell

**Task:** Build the results page layout and shell at `/results/[jobId]`.

**Depends on:** Agent 1, Agent 2

**Instructions:**
```
Build the results page shell at src/app/results/[jobId]/page.tsx.

This page fetches results from /api/results/[jobId] and lays out the full 
results view. Build with placeholder/mock data for now — the API will be 
wired in later.

Mock data shape to use while building:
{
  videoUrl: "/demo.mp4",
  dips: [{ timestamp: 8, region: "visual cortex", severity: "high", reason: "..." }],
  soundOffGap: 0.34,
  modalityBalance: { visual: 28, language: 72 },
  ctaWindow: { optimal: 18, current: 34, dropped: true },
  suggestions: ["Shorten VO at 0:04–0:12", "Add b-roll at 0:08"],
  attentionCurve: [{ t: 0, score: 0.9 }, { t: 5, score: 0.85 }, ...]
}

Page layout (two-column on desktop, single column on mobile):
LEFT COLUMN (60% width):
  - Video player (standard HTML5 <video> tag, controls, rounded corners)
  - Below video: attention curve chart (placeholder for Agent 5)
  - Below chart: dip markers list (each dip as a card — timestamp, brain region, reason)

RIGHT COLUMN (40% width):
  - 3D Brain visualization (placeholder div with text "Brain viz here" for now — 
    Agent 6 will fill this in)
  - Sound-Off Score card (placeholder for Agent 7)
  - Modality Balance card (placeholder for Agent 8)
  - CTA Window card (placeholder for Agent 9)

Top of page:
  - "Resonate" wordmark (small, top left)
  - Video filename (top center)
  - "New Analysis" button (top right)

Styling:
  - Page background: #0a0a0f
  - Cards: bg-zinc-900 border border-zinc-800 rounded-xl p-5
  - Section headers: text-zinc-400 text-xs uppercase tracking-widest mb-3
```

---

## Agent 5 — Attention Curve Chart

**Task:** Build the attention curve chart component that sits below the video player.

**Depends on:** Agent 4 (results page shell)

**Instructions:**
```
Build src/components/AttentionCurveChart.tsx using Recharts.

Props:
  attentionCurve: Array<{ t: number, score: number }> // t = seconds, score = 0-1
  dips: Array<{ timestamp: number, severity: 'high' | 'medium' }>
  duration: number // total video length in seconds
  currentTime: number // current playhead position (synced to video)
  onSeek: (t: number) => void // called when user clicks chart to seek video

Chart spec:
- AreaChart (Recharts) with smooth curve (type="monotone")
- X axis: time in seconds (0 to duration)
- Y axis: hidden (0 to 1 range)
- Area fill: gradient from blue (top) to transparent (bottom)
- Line stroke: #3b82f6 (brand blue)
- Background: transparent (sits on dark page)
- No grid lines — just the curve

Overlays:
- Red vertical lines at each dip timestamp (severity "high" = bright red, 
  "medium" = orange)
- A vertical white line following currentTime (playhead indicator)
- On hover: tooltip showing "0:08 — Visual cortex drop" 

Interactions:
- Click anywhere on chart → call onSeek(t) to jump video to that time
- Dip markers are clickable → scroll to that dip's card in the left column

Styling:
- Chart height: 80px (compact strip under video)
- Chart background: rgba(255,255,255,0.02), rounded corners
- Dip labels: tiny text above each red line showing the timestamp
```

---

## Agent 6 — 3D Brain Visualization

**Task:** Build the 3D rotating brain component with color-coded region activation.

**Depends on:** Agent 1 (Three.js installed), Agent 4

**Instructions:**
```
Build src/components/BrainVisualization.tsx using @react-three/fiber and @react-three/drei.

This component renders a 3D brain cortical surface mesh with regions colored 
by activation intensity.

Props:
  regionScores: Record<string, number> // region name → activation 0-1
  highlightedRegion: string | null // region to highlight (from hovering a dip card)

Setup:
- Use @react-three/fiber <Canvas> with a dark background (#0a0a0f)
- Load a brain mesh — use a simplified GLTF/OBJ brain mesh. 
  Find a free one at sketchfab.com (search "brain cortex" filter by free license)
  or use the included example from @react-three/drei examples.
  Place the mesh file at public/brain.glb

Brain mesh rendering:
- MeshStandardMaterial, vertex coloring by region
- Base color: #1e1b4b (deep purple/dark)
- Activated regions: interpolate from #1e1b4b → #3b82f6 → #60a5fa based on score
- Highlighted region (from prop): pulse with a bright white/blue glow
- Ambient light: subtle, blue-tinted
- Point light: above the brain, white

Controls:
- OrbitControls from @react-three/drei (user can rotate/zoom)
- Auto-rotate slowly when idle (autoRotate, autoRotateSpeed=0.5)
- Stop auto-rotate on user interaction, resume after 3s

Below the canvas:
- Small legend: color scale from dark purple (low) → bright blue (high)
- Text label showing the currently highlighted region name (if any)

Canvas size: full width of the right column, height 280px
```

---

## Agent 7 — Sound-Off Score Card

**Task:** Build the Sound-Off Score feature card.

**Depends on:** Agent 4 (results page shell)

**Instructions:**
```
Build src/components/SoundOffCard.tsx.

Props:
  fullScore: number      // 0-1 overall brain engagement with sound
  mutedScore: number     // 0-1 overall brain engagement without sound  
  regionDeltas: Array<{ region: string, delta: number }> // which regions drop most

Layout (fits inside a card in the right column):
- Header: "Sound-Off Score" with a mute icon (lucide-react VolumeX)
- Big score: show the gap as a percentage — e.g. "-34% engagement without sound"
  Color: red if gap > 30%, orange if 15-30%, green if < 15%
- Verdict line: one sentence — e.g. "This video relies heavily on audio. 
  It won't hold attention on mute."
- Top affected regions: list the 2-3 regions with biggest delta
  e.g. "Language processing: -61%" / "Auditory cortex: -48%"
- Bottom: small bar showing full vs muted engagement side by side

Styling: same card style as Agent 4. Score number: text-4xl font-bold.
Red/orange/green color applied to the score number and border-left of the card.
```

---

## Agent 8 — Modality Balance Card

**Task:** Build the Modality Balance feature card.

**Depends on:** Agent 4

**Instructions:**
```
Build src/components/ModalityBalanceCard.tsx.

Props:
  visual: number    // 0-100 visual brain region activation %
  language: number  // 0-100 language brain region activation %
  categoryAvg: { visual: number, language: number } // reference pack average
  suggestion: string // GPT-4o fix suggestion

Layout:
- Header: "Modality Balance" with a brain icon
- Balance bar: full-width horizontal bar
  Left side labeled "Visual" (blue), right side labeled "Language" (purple)
  Fill proportionally — e.g. 28% blue | 72% purple
  Below bar: "28% Visual · 72% Language"
- Verdict: one-line e.g. "VO-heavy — language processing dominates"
- Category comparison: small text + thin bar showing category average
  e.g. "Your niche avg: 52% Visual — you're 24% more language-heavy"
- Suggestion box: slightly different background, italic text, 
  lightbulb icon, shows GPT-4o suggestion

Styling: balance bar height 12px, rounded-full. 
Visual fill: bg-blue-500, Language fill: bg-violet-500.
Category avg shown as a small tick mark on the balance bar.
```

---

## Agent 9 — CTA Window Card

**Task:** Build the CTA Window Finder card.

**Depends on:** Agent 4

**Instructions:**
```
Build src/components/CTAWindowCard.tsx.

Props:
  optimalTimestamp: number  // seconds — best moment for CTA
  currentTimestamp: number | null  // where their current CTA is (if detected)
  attentionAtOptimal: number  // 0-1 brain engagement at optimal moment
  attentionAtCurrent: number | null
  onSeek: (t: number) => void  // seek video to timestamp on click

Layout:
- Header: "CTA Window" with a target/cursor icon
- If currentTimestamp exists and is suboptimal:
    Warning banner (red/orange): "Your CTA lands at 0:34 — attention already dropped"
- Big recommendation: "Best CTA window: 0:18"
  Clickable — calls onSeek(optimalTimestamp), scrubs video to that moment
  Shows attention level: "Brain engagement: 84% at this moment"
- If currentTimestamp:
    Comparison: "Current placement: 0:34 (41% engagement) vs optimal: 0:18 (84%)"
- Small timeline strip: miniature version showing the full attention curve 
  with a green marker at optimal, red marker at current CTA

Styling: optimal timestamp shown in large blue text, clickable with underline 
on hover. Warning banner: bg-red-950 border-red-800 text-red-300.
```

---

## Agent 10 — Dip Cards (Engagement Autopsy)

**Task:** Build the individual dip cards that appear below the attention chart.

**Depends on:** Agent 4, Agent 5

**Instructions:**
```
Build src/components/DipCard.tsx and src/components/DipList.tsx.

DipCard Props:
  timestamp: number
  region: string       // e.g. "Visual cortex"
  severity: 'high' | 'medium'
  reason: string       // GPT-4o explanation
  suggestion: string   // GPT-4o fix
  onSeek: (t: number) => void

DipCard layout:
- Left: timestamp badge (e.g. "0:08") in monospace font, colored by severity
  high = red bg, medium = orange bg
- Right of badge: region name in white, severity badge (HIGH/MED)
- Below: reason text in zinc-400
- Below: suggestion in a slightly lighter box with arrow icon "→ Fix: ..."
- Clicking anywhere on the card → onSeek(timestamp)
- Hover state: card border brightens, subtle blue glow

DipList:
- Renders a list of DipCards
- Header: "Engagement Autopsy" with a stethoscope or activity icon
- Hook zone callout at top if there's a dip in first 8 seconds:
  special "⚠ Hook Zone" banner above that dip card

Styling: DipCard bg-zinc-900 border-zinc-800, on hover border-zinc-600.
High severity: left border 3px solid red. Medium: 3px solid orange.
```

---

## Agent 11 — Video Player Sync

**Task:** Wire the video player to the attention chart and dip cards so they all stay in sync.

**Depends on:** Agent 4, Agent 5, Agent 10

**Instructions:**
```
In src/app/results/[jobId]/page.tsx, add video playback synchronization:

1. Add a videoRef (useRef<HTMLVideoElement>) and currentTime state (useState<number>)

2. On video timeupdate event: update currentTime state → passes to AttentionCurveChart 
   as currentTime prop (moves the playhead line on the chart)

3. onSeek function: videoRef.current.currentTime = t → seeks the video
   Pass this to AttentionCurveChart, CTAWindowCard, and DipCards

4. Active dip highlighting: as video plays, check which dip is "current" 
   (within ±1s of currentTime) → highlight that DipCard with a glowing border
   and pass its region name to BrainVisualization as highlightedRegion

5. Auto-scroll: when a dip becomes active during playback, smoothly scroll 
   its DipCard into view (scrollIntoView({ behavior: 'smooth', block: 'center' }))

This creates the main demo magic: play the video → attention curve playhead moves → 
brain regions light up → dip card highlights — all in sync.
```

---

## Agent 12 — Polish Pass

**Task:** Final polish — animations, transitions, and making it look non-vibe-coded.

**Depends on:** All previous agents

**Instructions:**
```
Do a full polish pass across the app. Specific things to fix:

1. Page transitions: add fade-in on page load (opacity-0 → opacity-100 over 300ms)

2. Card entrance animations: stagger the right column cards fading in 
   (first card at 100ms delay, second at 200ms, etc.) using CSS animation-delay

3. Number animations: wherever a score or percentage is shown (Sound-Off gap, 
   Modality Balance %), animate it counting up from 0 on page load using 
   a simple useEffect + requestAnimationFrame counter

4. Glow effects: 
   - The brain viz canvas: add a subtle blue radial glow behind it 
     (box-shadow or a blurred div underneath)
   - High-severity dip cards: pulsing red left border (CSS @keyframes pulse)

5. Typography cleanup:
   - All timestamps: font-mono
   - All section headers: text-xs uppercase tracking-widest text-zinc-500
   - All "verdict" one-liners: text-lg font-medium text-white
   - All supporting text: text-sm text-zinc-400

6. Mobile responsiveness: on screens < 768px, stack both columns vertically,
   brain viz comes after the attention chart

7. Empty/loading states: every card should have a skeleton loader state 
   (use shadcn Skeleton component) for while data is fetching

8. Favicon: set a brain emoji as favicon in layout.tsx metadata
```

---

## Agent 13 — Vercel Deploy

**Task:** Deploy to Vercel and confirm everything works on a live URL.

**Depends on:** All previous agents, API routes wired in

**Instructions:**
```
Deploy the Next.js app to Vercel:

1. Make sure .env.local has all required keys:
   OPENAI_API_KEY=...
   MODAL_TOKEN_ID=...
   MODAL_TOKEN_SECRET=...
   YOUTUBE_API_KEY=...

2. Run: npx vercel
   - Follow prompts, link to your Vercel account
   - Add all env vars in Vercel dashboard under Settings → Environment Variables

3. After deploy, test:
   - Upload a short video (< 15s)
   - Confirm loading screen appears and polls correctly
   - Confirm results page renders with all 4 feature cards
   - Confirm video + chart sync works
   - Confirm brain viz rotates and responds to highlighted regions
   - Check on mobile (resize browser)

4. Get the production URL — this is what you show judges.
   Also run: npx vercel --prod to promote to production domain.
```
