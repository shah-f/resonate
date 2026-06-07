import React, { useEffect, useRef, forwardRef, useImperativeHandle } from 'react'

const VideoPlayer = forwardRef(function VideoPlayer({ src, onTimeUpdate, duration }, ref) {
  const vref = useRef(null)

  useImperativeHandle(ref, () => ({
    seekTo: (t) => {
      const v = vref.current
      if (!v) return
      v.currentTime = Math.max(0, Math.min(t, duration || v.duration || 0))
      // ensure a small play then pause to update frame (optional)
      v.pause()
    },
  }))

  useEffect(() => {
    const v = vref.current
    if (!v) return
    const h = () => onTimeUpdate && onTimeUpdate(v.currentTime)
    v.addEventListener('timeupdate', h)
    return () => v.removeEventListener('timeupdate', h)
  }, [onTimeUpdate])

  return (
    <div className="video-wrap">
      <video ref={vref} controls src={src} className="video-player" />
      <div className="video-meta">Duration: {duration}s</div>
    </div>
  )
})

export default VideoPlayer
