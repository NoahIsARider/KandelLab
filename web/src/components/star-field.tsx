'use client';

import { useEffect, useRef } from 'react';

/** Twinkling star field rendered as pure DOM elements (no canvas). */
export default function StarField({ count = 70 }: { count?: number }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    for (let i = 0; i < count; i++) {
      const s = document.createElement('i');
      s.style.left = `${Math.random() * 100}%`;
      s.style.top = `${Math.random() * 100}%`;
      s.style.setProperty('--s', `${(Math.random() * 1.6 + 0.8).toFixed(1)}px`);
      s.style.setProperty('--o', (Math.random() * 0.5 + 0.3).toFixed(2));
      s.style.setProperty('--t', `${(Math.random() * 4 + 2).toFixed(1)}s`);
      el.appendChild(s);
    }
  }, [count]);

  return <div ref={ref} className="hero-stars" aria-hidden="true" />;
}
