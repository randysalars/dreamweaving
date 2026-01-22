import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  spring,
  useVideoConfig,
} from "remotion";

interface ChecklistProps {
  title: string;
  items: string[];
  theme?: {
    primaryColor: string;
    backgroundColor: string;
    textColor: string;
  };
}

/**
 * Animated Checklist
 * Items appear one by one with checkmark animations.
 */
export const Checklist: React.FC<ChecklistProps> = ({
  title,
  items,
  theme = {
    primaryColor: "#48BB78",
    backgroundColor: "#ffffff",
    textColor: "#1a202c",
  },
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 80 },
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.backgroundColor,
        padding: 80,
      }}
    >
      {/* Title */}
      <h1
        style={{
          fontSize: 56,
          fontWeight: 700,
          color: theme.textColor,
          marginBottom: 50,
          opacity: titleSpring,
          transform: `translateY(${interpolate(titleSpring, [0, 1], [30, 0])}px)`,
        }}
      >
        {title}
      </h1>

      {/* Checklist items */}
      <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        {items.map((item, index) => {
          const itemDelay = 30 + index * 20;
          const itemSpring = spring({
            frame: frame - itemDelay,
            fps,
            config: { damping: 12, stiffness: 100 },
          });

          const checkSpring = spring({
            frame: frame - itemDelay - 10,
            fps,
            config: { damping: 8, stiffness: 150 },
          });

          return (
            <div
              key={index}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 20,
                opacity: itemSpring,
                transform: `translateX(${interpolate(itemSpring, [0, 1], [-50, 0])}px)`,
              }}
            >
              {/* Checkmark */}
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 8,
                  backgroundColor: theme.primaryColor,
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  transform: `scale(${checkSpring})`,
                }}
              >
                <span style={{ fontSize: 24, color: "#fff" }}>✓</span>
              </div>

              {/* Item text */}
              <span
                style={{
                  fontSize: 32,
                  color: theme.textColor,
                  fontWeight: 500,
                }}
              >
                {item}
              </span>
            </div>
          );
        })}
      </div>

      {/* Branding */}
      <div
        style={{
          position: "absolute",
          bottom: 40,
          right: 60,
          fontSize: 18,
          color: theme.primaryColor,
          opacity: 0.7,
        }}
      >
        SalarsNet • Dreamweaving
      </div>
    </AbsoluteFill>
  );
};
