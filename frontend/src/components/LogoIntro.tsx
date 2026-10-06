import { useState, useEffect } from 'react';
import { DatlyLogo } from './DatlyLogo';

export function LogoIntro({ onComplete, onReplayReady }: { onComplete: () => void, onReplayReady?: (replayFn: () => void) => void }) {
  const [key, setKey] = useState(0);
  const [reducedMotion, setReducedMotion] = useState(() => window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const [introFinished, setIntroFinished] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const listener = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
    mediaQuery.addEventListener('change', listener);
    return () => mediaQuery.removeEventListener('change', listener);
  }, []);

  useEffect(() => {
    if (onReplayReady) {
      onReplayReady(() => {
        setIntroFinished(false);
        setKey(k => k + 1);
      });
    }
  }, [onReplayReady]);

  // Master fallback timer
  useEffect(() => {
    const timer = setTimeout(() => {
      setIntroFinished(true);
      setTimeout(() => {
        onComplete();
      }, 800);
    }, 2800);
    
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run exactly once per mount


  return (
    <div className={`fixed inset-0 w-screen h-screen flex flex-col items-center justify-center transition-opacity duration-1000 ${introFinished ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
      <div className="flex items-center justify-center">
        <DatlyLogo key={key} animate={!introFinished} reducedMotion={reducedMotion} />
      </div>
    </div>
  );
}
