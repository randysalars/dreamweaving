import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';

interface GuidedPauseProps {
  text?: string;
  theme?: {
    backgroundColor?: string;
    textColor?: string;
  };
}

/**
 * Guided Pause Component (5-10 seconds)
 * 
 * Purpose: Let the brain catch up
 * - On-screen text: "Pause. Think. Repeat."
 * - No audio or very soft ambient sound
 * - Dramatically improves retention
 */
export const GuidedPause: React.FC<GuidedPauseProps> = ({
  text = 'Pause. Think. Repeat.',
  theme = {}
}) => {
  const frame = useCurrentFrame();
  const {
    backgroundColor = '#0d0d1a',
    textColor = '#ffffff',
  } = theme;
  
  // Gentle breathing animation
  const breathe = Math.sin(frame / 30) * 0.05 + 1;
  const opacity = interpolate(
    frame,
    [0, 30],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  
  // Parse text into words for staggered reveal
  const words = text.split(' ');
  
  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 40,
      }}
    >
      {/* Meditation icon */}
      <div
        style={{
          fontSize: 80,
          transform: `scale(${breathe})`,
          opacity,
        }}
      >
        🧘
      </div>
      
      {/* Text */}
      <div
        style={{
          display: 'flex',
          gap: 24,
          opacity,
        }}
      >
        {words.map((word, index) => {
          const wordOpacity = interpolate(
            frame,
            [30 + index * 20, 50 + index * 20],
            [0, 1],
            { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
          );
          
          return (
            <span
              key={index}
              style={{
                color: textColor,
                fontSize: 48,
                fontWeight: 300,
                letterSpacing: 4,
                opacity: wordOpacity,
              }}
            >
              {word}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export default GuidedPause;
