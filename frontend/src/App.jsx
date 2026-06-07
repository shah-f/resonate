import React, { useEffect, useRef, useState } from 'react'
import BrainVisualization from './components/BrainVisualization'
import VideoPlayer from './components/VideoPlayer'
import Timeline from './components/Timeline'

export default function App() {
  const [data, setData] = useState(null)
  const [currentTime, setCurrentTime] = useState(0)
  const videoRef = React.useRef(null)

  useEffect(() => {
    Promise.all([
      fetch('/src/mock/result.json').then((r) => r.json()),
      fetch('/src/mock/schaefer200_parcels.json').then((r) => r.json()).catch(() => null),
    ]).then(([d, parcelsJson]) => {
        // synthesize parcel-level mock data if missing
        if (!d.brain.parcels || d.brain.parcels.length === 0) {
          const timesteps = d.brain.modality.visual.length
          const parcels = Array.from({ length: timesteps }, () => {
            return Array.from({ length: 200 }, () => Math.random() * 0.6 + 0.2)
          })
          d.brain.parcels = parcels
          d.brain.parcelNames = Array.from({ length: 200 }, (_, i) => `Parcel_${i + 1}`)
          // simple modality indices: first 70 visual, next 60 audio, rest language
          d.brain.modalityIndices = {
            visual: Array.from({ length: 70 }, (_, i) => i),
            audio: Array.from({ length: 60 }, (_, i) => 70 + i),
            language: Array.from({ length: 70 }, (_, i) => 130 + i),
          }
        }
        // attach parcelPositions if exporter JSON exists
        if (parcelsJson && parcelsJson.parcels) {
          d.brain.parcelPositions = parcelsJson.parcels.map((p) => p.pos)
          // if brain.parcels empty, use mock_timeseries
          if ((!d.brain.parcels || d.brain.parcels.length === 0) && parcelsJson.mock_timeseries) {
            d.brain.parcels = parcelsJson.mock_timeseries
          }
        }
        setData(d)
      })
  }, [])

  if (!data) return <div className="loading">Loading demo data…</div>

  // compute overall series as mean of modalities
  const overall = data && data.brain && data.brain.modality
    ? data.brain.modality.visual.map((v, i) => {
        const a = data.brain.modality.audio[i] || 0
        const l = data.brain.modality.language[i] || 0
        return Math.max(0, Math.min(1, (v + a + l) / 3))
      })
    : []

  // simple dip detection: find indices where drop from previous > threshold
  const dips = []
  for (let i = 1; i < overall.length; i++) {
    const delta = overall[i] - overall[i - 1]
    if (delta < -0.06) {
      const time = (i / Math.max(1, overall.length - 1)) * data.duration
      dips.push({ time, index: i, label: `${(time).toFixed(1)}s` })
    }
  }

  return (
    <div className="app-root">
      <header className="topbar">
        <h1>Resonate — Demo</h1>
        <p className="subtitle">Find the moments your video loses the brain.</p>
      </header>

      <main className="results-grid">
        <section className="left">
          <VideoPlayer
            ref={videoRef}
            src={data.videoUrl}
            duration={data.duration}
            onTimeUpdate={(t) => setCurrentTime(t)}
          />

          <div className="timeline">
            <h3>Attention timeline (overall)</h3>
            <Timeline
              series={overall}
              duration={data.duration}
              currentTime={currentTime}
              dips={dips}
              onSeek={(t) => videoRef.current && videoRef.current.seekTo(t)}
            />
          </div>
        </section>

        <aside className="right">
          <div className="brain-card">
            <h3>Brain Activation</h3>
            <BrainVisualization
              currentTime={currentTime}
              duration={data.duration}
              segments={data.brain.segments}
              modality={data.brain.modality}
              parcels={data.brain.parcels}
              parcelNames={data.brain.parcelNames}
              modalityIndices={data.brain.modalityIndices}
              parcelPositions={data.brain.parcelPositions}
            />
          </div>

          <div className="readout">
            <h4>Now Playing</h4>
            <div>Time: {currentTime.toFixed(1)}s</div>
            <div className="modalities">
              <div>Visual: {Math.round(getModValue(data.brain.modality.visual, currentTime, data.duration) * 100)}%</div>
              <div>Audio: {Math.round(getModValue(data.brain.modality.audio, currentTime, data.duration) * 100)}%</div>
              <div>Language: {Math.round(getModValue(data.brain.modality.language, currentTime, data.duration) * 100)}%</div>
            </div>
          </div>
        </aside>
      </main>
    </div>
  )
}

function getModValue(series, time, duration) {
  if (!series || series.length === 0) return 0
  const idx = Math.round((time / duration) * (series.length - 1))
  const v = series[Math.max(0, Math.min(series.length - 1, idx))]
  return Math.max(0, Math.min(1, v))
}
