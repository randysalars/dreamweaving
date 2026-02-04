import React from 'react';
import { AbsoluteFill, Audio, staticFile, useCurrentFrame, interpolate } from 'remotion';

interface CoreExplanationProps {
  keywords: string[];
  audioPath?: string;
  theme?: {
    backgroundColor?: string;
    textColor?: string;
    highlightColor?: string;
  };
}

/**
 * Core Explanation Component (2-4 minutes)
 * 
 * Purpose: Teach the concept
 * - Short sentences, one idea per sentence
 * - Slow pace (~0.75x normal speech)
 * - Keyword highlighting synced to narration
 */
export const CoreExplanation: React.FC<CoreExplanationProps> = ({
  keywords = [],
  audioPath,
  theme = {}
}) => {
  const frame = useCurrentFrame();
  const {
    backgroundColor = '#1a1a2e',
    textColor = '#ffffff',
    highlightColor = '#9F7AEA',
  } = theme;
  
  // Calculate which keyword is "active" based on frame
  // This is a simple version - production would use audio timestamps
  const keywordDuration = 90; // ~3 seconds per keyword at 30fps
  const activeKeywordIndex = Math.floor(frame / keywordDuration) % keywords.length;
  
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
      {/* Audio track */}
      {audioPath && (
        <Audio src={staticFile(audioPath)} />
      )}
      
      {/* Keyword cards */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 32,
          width: '100%',
          maxWidth: 900,
        }}
      >
        {keywords.map((keyword, index) => {
          const isActive = index === activeKeywordIndex;
          const isPast = index < activeKeywordIndex;
          
          const scale = isActive ? 1.05 : 1;
          const opacity = isPast ? 0.5 : 1;
          
          return (
            <div
              key={keyword}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 24,
                padding: 24,
                backgroundColor: isActive ? `${highlightColor}20` : 'transparent',
                borderRadius: 16,
                border: isActive ? `3px solid ${highlightColor}` : '3px solid transparent',
                transform: `scale(${scale})`,
                opacity,
                transition: 'all 0.3s ease',
              }}
            >
              {/* Number */}
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: '50%',
                  backgroundColor: isActive ? highlightColor : '#333',
                  color: '#fff',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  fontSize: 20,
                  fontWeight: 700,
                }}
              >
                {index + 1}
              </div>
              
              {/* Keyword */}
              <span
                style={{
                  color: isActive ? highlightColor : textColor,
                  fontSize: 40,
                  fontWeight: isActive ? 700 : 500,
                  textTransform: 'capitalize',
                }}
              >
                {keyword}
              </span>
              
              {/* Active indicator */}
              {isActive && (
                <div
                  style={{
                    marginLeft: 'auto',
                    fontSize: 32,
                  }}
                >
                  👈
                </div>
              )}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export default CoreExplanation;
