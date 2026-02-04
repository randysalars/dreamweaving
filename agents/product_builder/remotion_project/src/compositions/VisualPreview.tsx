import React from 'react';
import { AbsoluteFill, Img, staticFile, useCurrentFrame, interpolate, Easing } from 'remotion';

interface VisualPreviewProps {
  icons: string[];
  theme?: {
    backgroundColor?: string;
    iconColor?: string;
  };
}

/**
 * Visual Preview Component (5-10 seconds)
 * 
 * Purpose: Prime comprehension before language
 * - Shows what will happen, not explanations
 * - Icons, images, or animations only
 * - No full sentences yet
 */
export const VisualPreview: React.FC<VisualPreviewProps> = ({
  icons = [],
  theme = {}
}) => {
  const frame = useCurrentFrame();
  const { backgroundColor = '#1a1a2e', iconColor = '#9F7AEA' } = theme;
  
  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 80,
      }}
    >
      {icons.map((icon, index) => {
        // Staggered entrance animation
        const delay = index * 10;
        const scale = interpolate(
          frame - delay,
          [0, 15],
          [0, 1],
          {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
            easing: Easing.out(Easing.back(1.5)),
          }
        );
        
        const opacity = interpolate(
          frame - delay,
          [0, 10],
          [0, 1],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
        );
        
        return (
          <div
            key={icon}
            style={{
              transform: `scale(${scale})`,
              opacity,
              fontSize: 120,
              filter: `drop-shadow(0 4px 20px ${iconColor}40)`,
            }}
          >
            {/* Use icon from library or emoji fallback */}
            {getIconEmoji(icon)}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// Simple icon mapping - can be expanded with proper icon library
function getIconEmoji(key: string): string {
  const iconMap: Record<string, string> = {
    menu: '📋',
    plate: '🍽️',
    cash: '💵',
    money: '💰',
    food: '🍔',
    order: '📝',
    pay: '💳',
    restaurant: '🏪',
    waiter: '🧑‍🍳',
    drink: '🥤',
    default: '✨',
  };
  return iconMap[key.toLowerCase()] || iconMap.default;
}

export default VisualPreview;
