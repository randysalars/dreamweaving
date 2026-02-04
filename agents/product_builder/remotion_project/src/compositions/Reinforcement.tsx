import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';

interface ReinforcementProps {
  keywords: string[];
  theme?: {
    backgroundColor?: string;
    textColor?: string;
    highlightColor?: string;
  };
}

/**
 * Reinforcement Component (30 seconds)
 * 
 * Purpose: Lock meaning without more words
 * - Highlight text
 * - Zoom on objects
 * - Animate arrows or circles
 * - Repeat key phrase visually
 */
export const Reinforcement: React.FC<ReinforcementProps> = ({
  keywords = [],
  theme = {}
}) => {
  const frame = useCurrentFrame();
  const {
    backgroundColor = '#1a1a2e',
    textColor = '#ffffff',
    highlightColor = '#9F7AEA',
  } = theme;
  
  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: 40,
          padding: 80,
        }}
      >
        {keywords.map((keyword, index) => {
          // Staggered pulsing animation
          const cycleOffset = index * 15;
          const pulse = Math.sin((frame + cycleOffset) / 15) * 0.1 + 1;
          
          const opacity = interpolate(
            frame,
            [index * 10, index * 10 + 20],
            [0, 1],
            { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
          );
          
          const glow = `drop-shadow(0 0 ${20 + Math.sin((frame + cycleOffset) / 10) * 10}px ${highlightColor}80)`;
          
          return (
            <div
              key={keyword}
              style={{
                transform: `scale(${pulse})`,
                opacity,
                fontSize: 56,
                fontWeight: 700,
                color: highlightColor,
                filter: glow,
                textTransform: 'uppercase',
                letterSpacing: 4,
              }}
            >
              {keyword}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export default Reinforcement;
