import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';

interface GoalStatementProps {
  goal: string;
  theme?: {
    backgroundColor?: string;
    textColor?: string;
    accentColor?: string;
  };
}

/**
 * Goal Statement Component (8 seconds)
 * 
 * Purpose: Set expectations with one clear sentence
 * - One sentence
 * - Present tense
 * - Concrete outcome
 */
export const GoalStatement: React.FC<GoalStatementProps> = ({
  goal,
  theme = {}
}) => {
  const frame = useCurrentFrame();
  const {
    backgroundColor = '#1a1a2e',
    textColor = '#ffffff',
    accentColor = '#9F7AEA',
  } = theme;
  
  // Badge entrance
  const badgeScale = interpolate(
    frame,
    [0, 20],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.back(1.2)),
    }
  );
  
  // Goal text entrance
  const textOpacity = interpolate(
    frame,
    [15, 35],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  
  const textY = interpolate(
    frame,
    [15, 35],
    [30, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  
  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 80,
      }}
    >
      {/* Goal Badge */}
      <div
        style={{
          transform: `scale(${badgeScale})`,
          backgroundColor: accentColor,
          color: '#ffffff',
          padding: '16px 48px',
          borderRadius: 50,
          fontSize: 24,
          fontWeight: 600,
          letterSpacing: 2,
          textTransform: 'uppercase',
          marginBottom: 40,
        }}
      >
        🎯 Goal
      </div>
      
      {/* Goal Statement */}
      <div
        style={{
          opacity: textOpacity,
          transform: `translateY(${textY}px)`,
          color: textColor,
          fontSize: 48,
          fontWeight: 500,
          textAlign: 'center',
          maxWidth: 1200,
          lineHeight: 1.4,
        }}
      >
        {goal}
      </div>
    </AbsoluteFill>
  );
};

export default GoalStatement;
