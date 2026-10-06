import { useState, useRef, useEffect } from 'react';
import { Play, Pause } from 'lucide-react';

interface AudioPlayerProps {
  src: string;
}

export function AudioPlayer({ src }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);

  // Auto-play the voice response when it arrives
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.play().catch(e => console.log('Autoplay prevented:', e));
    }
  }, [src]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
  };

  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    const current = audioRef.current.currentTime;
    const total = audioRef.current.duration;
    setCurrentTime(current);
    if (total) {
      setProgress((current / total) * 100);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
    setProgress(0);
    setCurrentTime(0);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!audioRef.current) return;
    const newTime = (Number(e.target.value) / 100) * duration;
    audioRef.current.currentTime = newTime;
    setProgress(Number(e.target.value));
  };

  const formatTime = (time: number) => {
    if (isNaN(time)) return '0:00';
    const mins = Math.floor(time / 60);
    const secs = Math.floor(time % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-2xl px-4 py-2 w-full mt-2 hover:bg-white/10 transition-colors shadow-sm">
      <audio
        ref={audioRef}
        src={src}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
        className="hidden"
      />
      
      <button 
        onClick={togglePlay}
        className="shrink-0 w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-colors text-white"
      >
        {isPlaying ? (
          <Pause size={14} fill="currentColor" />
        ) : (
          <Play size={14} fill="currentColor" className="ml-0.5" />
        )}
      </button>

      {/* Waveform / Progress bar (Simulated waveform using playing state) */}
      <div className="flex-1 flex items-center gap-2 relative">
        <div className="relative w-full h-1.5 bg-white/10 rounded-full overflow-hidden flex items-center group cursor-pointer">
          <div 
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-[#7c3aed] to-[#f97316] rounded-full"
            style={{ width: `${progress}%` }}
          />
          <input 
            type="range"
            min="0"
            max="100"
            value={progress || 0}
            onChange={handleSeek}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
        </div>
        
        {/* Animated Voice Equalizer when playing */}
        {isPlaying && (
          <div className="flex gap-0.5 h-3 items-end ml-2 shrink-0">
            <div className="w-[3px] bg-[#f97316] rounded-full animate-[pulse_0.8s_infinite_100ms] h-full" />
            <div className="w-[3px] bg-[#f97316] rounded-full animate-[pulse_0.8s_infinite_300ms] h-2/3" />
            <div className="w-[3px] bg-[#f97316] rounded-full animate-[pulse_0.8s_infinite_200ms] h-full" />
            <div className="w-[3px] bg-[#f97316] rounded-full animate-[pulse_0.8s_infinite_400ms] h-1/2" />
          </div>
        )}
      </div>

      <div className="shrink-0 text-[10px] text-white/50 font-mono w-16 text-right">
        {formatTime(currentTime)} / {formatTime(duration)}
      </div>
    </div>
  );
}
