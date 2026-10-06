import { useState } from 'react';
import { Navbar } from '../components/Navbar';
import { Hero } from '../components/Hero';
import { WaveBackground } from '../components/WaveBackground';
import { LogoIntro } from '../components/LogoIntro';

export function Landing() {
  const [introDone, setIntroDone] = useState(false);
  const [, setTriggerReplay] = useState<{ fn: () => void } | null>(null);

  return (
    <div className="min-h-screen w-full relative selection:bg-[#8b5cf6]/30 selection:text-white flex flex-col font-sans bg-[#141414] text-white overflow-x-hidden">
      <WaveBackground />

      {!introDone && (
        <div className="fixed inset-0 z-50">
          <LogoIntro
            onComplete={() => setIntroDone(true)}
            onReplayReady={(fn) => setTriggerReplay({ fn })}
          />
        </div>
      )}

      <div
        className="flex-1 flex flex-col relative transition-opacity duration-1000 z-10 w-full"
        style={{ opacity: introDone ? 1 : 0, pointerEvents: introDone ? 'auto' : 'none' }}
      >
        <Navbar />
        <main className="flex-1 flex flex-col items-center">
          <Hero />
        </main>
      </div>
    </div>
  );
}
