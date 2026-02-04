import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';

interface MiniCheckProps {
  question: string;
  choices?: string[];
  answer: string;
  pauseDurationFrames?: number;
  theme?: {
    backgroundColor?: string;
    textColor?: string;
    correctColor?: string;
    accentColor?: string;
  };
}

/**
 * Mini Check Component (20 seconds)
 * 
 * Purpose: Active recall (not testing)
 * - Question display
 * - Pause for thinking
 * - Answer reveal
 */
export const MiniCheck: React.FC<MiniCheckProps> = ({
  question,
  choices = [],
  answer,
  pauseDurationFrames = 300, // 10 seconds at 30fps
  theme = {}
}) => {
  const frame = useCurrentFrame();
  const {
    backgroundColor = '#1a1a2e',
    textColor = '#ffffff',
    correctColor = '#48BB78',
    accentColor = '#9F7AEA',
  } = theme;
  
  // Animation phases
  const questionEntrance = 30;
  const choicesStart = 60;
  const answerReveal = pauseDurationFrames;
  
  // Question opacity
  const questionOpacity = interpolate(
    frame,
    [0, questionEntrance],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  
  // Answer revealed?
  const showAnswer = frame >= answerReveal;
  
  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 80,
        gap: 48,
      }}
    >
      {/* Mini Check Badge */}
      <div
        style={{
          backgroundColor: accentColor,
          color: '#fff',
          padding: '12px 32px',
          borderRadius: 50,
          fontSize: 20,
          fontWeight: 600,
          opacity: questionOpacity,
        }}
      >
        ✓ Mini Check
      </div>
      
      {/* Question */}
      <div
        style={{
          color: textColor,
          fontSize: 44,
          fontWeight: 600,
          textAlign: 'center',
          maxWidth: 1000,
          opacity: questionOpacity,
        }}
      >
        {question}
      </div>
      
      {/* Choices */}
      {choices.length > 0 && (
        <div
          style={{
            display: 'flex',
            gap: 24,
            marginTop: 32,
          }}
        >
          {choices.map((choice, index) => {
            const choiceOpacity = interpolate(
              frame,
              [choicesStart + index * 10, choicesStart + index * 10 + 15],
              [0, 1],
              { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
            );
            
            const isCorrect = choice.toLowerCase() === answer.toLowerCase();
            const bgColor = showAnswer
              ? isCorrect
                ? correctColor
                : '#555'
              : '#333';
            
            return (
              <div
                key={choice}
                style={{
                  backgroundColor: bgColor,
                  color: '#fff',
                  padding: '20px 40px',
                  borderRadius: 12,
                  fontSize: 28,
                  fontWeight: 500,
                  opacity: choiceOpacity,
                  border: showAnswer && isCorrect ? `3px solid ${correctColor}` : 'none',
                  boxShadow: showAnswer && isCorrect ? `0 0 30px ${correctColor}50` : 'none',
                }}
              >
                {choice}
              </div>
            );
          })}
        </div>
      )}
      
      {/* Thinking timer (before answer reveal) */}
      {!showAnswer && frame >= choicesStart + (choices.length * 10) && (
        <div
          style={{
            color: '#666',
            fontSize: 24,
            marginTop: 48,
          }}
        >
          Think about your answer...
        </div>
      )}
      
      {/* Answer reveal (if no choices) */}
      {showAnswer && choices.length === 0 && (
        <div
          style={{
            backgroundColor: correctColor,
            color: '#fff',
            padding: '24px 48px',
            borderRadius: 16,
            fontSize: 36,
            fontWeight: 700,
            marginTop: 32,
            boxShadow: `0 0 40px ${correctColor}50`,
          }}
        >
          ✓ {answer}
        </div>
      )}
    </AbsoluteFill>
  );
};

export default MiniCheck;
