import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  spring,
  useVideoConfig,
  Sequence,
} from "remotion";

interface KeyInsightProps {
  insightText: string;
  context: string;
  chapterNumber: number;
  theme?: {
    primaryColor: string;
    backgroundColor: string;
    textColor: string;
  };
}

/**
 * Key Insight Animation
 * 8-second animation highlighting a key takeaway.
 */
export const KeyInsight: React.FC<KeyInsightProps> = ({
  insightText,
  context,
  chapterNumber,
  theme = {
    primaryColor: "#9F7AEA",
    backgroundColor: "#1a1a2e",
    textColor: "#ffffff",
  },
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Lightbulb animation
  const bulbSpring = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 100 },
  });

  const glowIntensity = interpolate(
    Math.sin(frame / 10),
    [-1, 1],
    [0.5, 1]
  );

  // Text animations
  const textSpring = spring({
    frame: frame - 30,
    fps,
    config: { damping: 15, stiffness: 60 },
  });

  const contextSpring = spring({
    frame: frame - 60,
    fps,
    config: { damping: 15, stiffness: 60 },
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.backgroundColor,
        justifyContent: "center",
        alignItems: "center",
        padding: 80,
      }}
    >
      {/* Glowing background */}
      <div
        style={{
          position: "absolute",
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${theme.primaryColor}40 0%, transparent 70%)`,
          opacity: glowIntensity,
          transform: `scale(${bulbSpring})`,
        }}
      />

      {/* Lightbulb icon */}
      <div
        style={{
          fontSize: 120,
          marginBottom: 40,
          transform: `scale(${bulbSpring})`,
          filter: `drop-shadow(0 0 ${20 * glowIntensity}px ${theme.primaryColor})`,
        }}
      >
        💡
      </div>

      {/* Key insight text */}
      <div
        style={{
          fontSize: 48,
          fontWeight: 700,
          color: theme.textColor,
          textAlign: "center",
          maxWidth: 1000,
          lineHeight: 1.4,
          opacity: textSpring,
          transform: `translateY(${interpolate(textSpring, [0, 1], [40, 0])}px)`,
        }}
      >
        "{insightText}"
      </div>

      {/* Context */}
      <div
        style={{
          marginTop: 30,
          fontSize: 24,
          color: theme.primaryColor,
          opacity: contextSpring,
          transform: `translateY(${interpolate(contextSpring, [0, 1], [20, 0])}px)`,
        }}
      >
        — Chapter {chapterNumber}: {context}
      </div>
    </AbsoluteFill>
  );
};
