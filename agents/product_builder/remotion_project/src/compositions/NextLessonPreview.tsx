import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';

interface NextLessonPreviewProps {
  title: string;
  description?: string;
  theme?: {
    backgroundColor?: string;
    textColor?: string;
    accentColor?: string;
  };
}

/**
 * Next Lesson Preview Component (10 seconds)
 * 
 * Purpose: Maintain momentum
 * - Gentle preview of what's next
 * - Creates anticipation
 * - Keeps binge momentum high
 */
export const NextLessonPreview: React.FC<NextLessonPreviewProps> = ({
  title,
  description,
  theme = {}
}) => {
  const frame = useCurrentFrame();
  const {
    backgroundColor = '#1a1a2e',
    textColor = '#ffffff',
    accentColor = '#9F7AEA',
  } = theme;
  
  // Entrance animations
  const badgeOpacity = interpolate(
    frame,
    [0, 20],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  
  const titleOpacity = interpolate(
    frame,
    [15, 35],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  
  const titleY = interpolate(
    frame,
    [15, 35],
    [30, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    }
  );
  
  const arrowBounce = Math.sin(frame / 10) * 5;
  
  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 80,
        gap: 32,
      }}
    >
      {/* Up Next Badge */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          opacity: badgeOpacity,
        }}
      >
        <span
          style={{
            fontSize: 40,
            transform: `translateX(${arrowBounce}px)`,
          }}
        >
          ➡️
        </span>
        <span
          style={{
            color: accentColor,
            fontSize: 24,
            fontWeight: 600,
            letterSpacing: 3,
            textTransform: 'uppercase',
          }}
        >
          Up Next
        </span>
      </div>
      
      {/* Title */}
      <div
        style={{
          color: textColor,
          fontSize: 44,
          fontWeight: 600,
          textAlign: 'center',
          maxWidth: 900,
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
        }}
      >
        {title}
      </div>
      
      {/* Description (optional) */}
      {description && (
        <div
          style={{
            color: '#888',
            fontSize: 24,
            textAlign: 'center',
            maxWidth: 700,
            opacity: titleOpacity,
            marginTop: 16,
          }}
        >
          {description}
        </div>
      )}
    </AbsoluteFill>
  );
};

export default NextLessonPreview;
