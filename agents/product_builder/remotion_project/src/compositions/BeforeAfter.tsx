import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  spring,
  useVideoConfig,
} from "remotion";

interface BeforeAfterProps {
  before: {
    title: string;
    points: string[];
  };
  after: {
    title: string;
    points: string[];
  };
  theme?: {
    beforeColor: string;
    afterColor: string;
    backgroundColor: string;
    textColor: string;
  };
}

/**
 * Before/After Transformation
 * Shows the journey from current state to transformed state.
 */
export const BeforeAfter: React.FC<BeforeAfterProps> = ({
  before,
  after,
  theme = {
    beforeColor: "#E53E3E",
    afterColor: "#48BB78",
    backgroundColor: "#1a1a2e",
    textColor: "#ffffff",
  },
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 80 },
  });

  const beforeSpring = spring({
    frame: frame - 30,
    fps,
    config: { damping: 15, stiffness: 60 },
  });

  const arrowSpring = spring({
    frame: frame - 120,
    fps,
    config: { damping: 12, stiffness: 100 },
  });

  const afterSpring = spring({
    frame: frame - 150,
    fps,
    config: { damping: 15, stiffness: 60 },
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.backgroundColor,
        padding: 80,
        justifyContent: "center",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 60,
        }}
      >
        {/* Before */}
        <div
          style={{
            flex: 1,
            backgroundColor: `${theme.beforeColor}20`,
            borderRadius: 24,
            padding: 50,
            borderLeft: `6px solid ${theme.beforeColor}`,
            opacity: beforeSpring,
            transform: `translateX(${interpolate(beforeSpring, [0, 1], [-50, 0])}px)`,
          }}
        >
          <h2
            style={{
              fontSize: 36,
              fontWeight: 700,
              color: theme.beforeColor,
              marginBottom: 30,
            }}
          >
            {before.title}
          </h2>
          {before.points.map((point, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                marginBottom: 16,
                fontSize: 24,
                color: theme.textColor,
              }}
            >
              <span style={{ color: theme.beforeColor }}>✗</span>
              {point}
            </div>
          ))}
        </div>

        {/* Arrow */}
        <div
          style={{
            fontSize: 80,
            color: theme.afterColor,
            opacity: arrowSpring,
            transform: `scale(${arrowSpring})`,
          }}
        >
          →
        </div>

        {/* After */}
        <div
          style={{
            flex: 1,
            backgroundColor: `${theme.afterColor}20`,
            borderRadius: 24,
            padding: 50,
            borderLeft: `6px solid ${theme.afterColor}`,
            opacity: afterSpring,
            transform: `translateX(${interpolate(afterSpring, [0, 1], [50, 0])}px)`,
          }}
        >
          <h2
            style={{
              fontSize: 36,
              fontWeight: 700,
              color: theme.afterColor,
              marginBottom: 30,
            }}
          >
            {after.title}
          </h2>
          {after.points.map((point, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                marginBottom: 16,
                fontSize: 24,
                color: theme.textColor,
              }}
            >
              <span style={{ color: theme.afterColor }}>✓</span>
              {point}
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};
