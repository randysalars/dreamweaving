import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  spring,
  useVideoConfig,
} from "remotion";

interface StatisticProps {
  value: string;
  label: string;
  suffix?: string;
  description?: string;
  theme?: {
    primaryColor: string;
    backgroundColor: string;
    textColor: string;
  };
}

/**
 * Statistic Highlight
 * Animated number/stat reveal with context.
 */
export const Statistic: React.FC<StatisticProps> = ({
  value,
  label,
  suffix = "",
  description,
  theme = {
    primaryColor: "#9F7AEA",
    backgroundColor: "#1a1a2e",
    textColor: "#ffffff",
  },
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Count up animation
  const numericValue = parseFloat(value.replace(/[^0-9.]/g, ""));
  const countProgress = interpolate(frame, [30, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  
  const displayValue = isNaN(numericValue) 
    ? value 
    : Math.round(numericValue * countProgress).toLocaleString();

  const labelSpring = spring({
    frame: frame - 60,
    fps,
    config: { damping: 15, stiffness: 60 },
  });

  const descSpring = spring({
    frame: frame - 90,
    fps,
    config: { damping: 15, stiffness: 60 },
  });

  // Glow pulse
  const glowIntensity = interpolate(
    Math.sin(frame / 15),
    [-1, 1],
    [0.3, 0.6]
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.backgroundColor,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {/* Glow background */}
      <div
        style={{
          position: "absolute",
          width: 500,
          height: 500,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${theme.primaryColor} 0%, transparent 70%)`,
          opacity: glowIntensity,
        }}
      />

      {/* Main value */}
      <div
        style={{
          fontSize: 180,
          fontWeight: 800,
          color: theme.primaryColor,
          textShadow: `0 0 60px ${theme.primaryColor}`,
        }}
      >
        {displayValue}{suffix}
      </div>

      {/* Label */}
      <div
        style={{
          fontSize: 48,
          fontWeight: 600,
          color: theme.textColor,
          marginTop: 20,
          opacity: labelSpring,
          transform: `translateY(${interpolate(labelSpring, [0, 1], [20, 0])}px)`,
        }}
      >
        {label}
      </div>

      {/* Description */}
      {description && (
        <div
          style={{
            fontSize: 28,
            color: theme.textColor,
            opacity: descSpring * 0.7,
            marginTop: 16,
            maxWidth: 800,
            textAlign: "center",
            transform: `translateY(${interpolate(descSpring, [0, 1], [15, 0])}px)`,
          }}
        >
          {description}
        </div>
      )}
    </AbsoluteFill>
  );
};
