import { useEffect, useState } from 'react';

interface BloodCell {
  id: number;
  left: number;
  top: number;
  size: number;
  delay: number;
  duration: number;
}

export const BloodCells = () => {
  const [cells, setCells] = useState<BloodCell[]>([]);

  useEffect(() => {
    const newCells: BloodCell[] = Array.from({ length: 15 }, (_, i) => ({
      id: i,
      left: Math.random() * 100,
      top: Math.random() * 100,
      size: Math.random() * 30 + 20,
      delay: Math.random() * 5,
      duration: Math.random() * 4 + 6,
    }));
    setCells(newCells);
  }, []);

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {cells.map((cell) => (
        <div
          key={cell.id}
          className="absolute rounded-full bg-gradient-to-br from-primary/20 to-primary/5 blur-sm"
          style={{
            left: `${cell.left}%`,
            top: `${cell.top}%`,
            width: `${cell.size}px`,
            height: `${cell.size}px`,
            animation: `float ${cell.duration}s ease-in-out infinite`,
            animationDelay: `${cell.delay}s`,
          }}
        >
          <div className="w-full h-full rounded-full animate-pulse-glow" />
        </div>
      ))}
    </div>
  );
};
