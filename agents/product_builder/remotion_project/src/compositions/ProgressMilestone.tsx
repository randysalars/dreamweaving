import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  spring,
  useVideoConfig,
} from "remotion";

interface ProgressMilestoneProps {
  milestones: Array<{
    name: string;
    description: string;
    completed: boolean;
  }>;
  currentMilestone: number;
  title?: string;
  theme?: {
    primaryColor: string;
    completedColor: string;
    backgroundColor: string;
    textColor: string;
  };
}

/**
 * Progress Milestone Animation
 * Shows journey progress through milestones.
 */
export const ProgressMilestone: React.FC<ProgressMilestoneProps> = ({
  milestones,
  currentMilestone,
  title = "Your Progress",
  theme = {
    primaryColor: "#9F7AEA",
    completedColor: "#48BB78",
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

  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.backgroundColor,
        padding: 80,
        justifyContent: "center",
      }}
    >
      {/* Title */}
      <h1
        style={{
          fontSize: 48,
          fontWeight: 700,
          color: theme.textColor,
          marginBottom: 60,
          textAlign: "center",
          opacity: titleSpring,
        }}
      >
        {title}
      </h1>

      {/* Progress track */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "center",
          gap: 0,
          position: "relative",
        }}
      >
        {milestones.map((milestone, index) => {
          const isCompleted = index < currentMilestone;
          const isCurrent = index === currentMilestone;
          const delay = 30 + index * 25;

          const nodeSpring = spring({
            frame: frame - delay,
            fps,
            config: { damping: 12, stiffness: 100 },
          });

          const pulseScale = isCurrent
            ? 1 + Math.sin(frame / 8) * 0.1
            : 1;

          return (
            <React.Fragment key={index}>
              {/* Milestone node */}
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  width: 180,
                  opacity: nodeSpring,
                  transform: `translateY(${interpolate(nodeSpring, [0, 1], [30, 0])}px)`,
                }}
              >
                {/* Circle */}
                <div
                  style={{
                    width: 60,
                    height: 60,
                    borderRadius: "50%",
                    backgroundColor: isCompleted
                      ? theme.completedColor
                      : isCurrent
                      ? theme.primaryColor
                      : "#4a5568",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    transform: `scale(${pulseScale * nodeSpring})`,
                    boxShadow: isCurrent
                      ? `0 0 30px ${theme.primaryColor}`
                      : "none",
                  }}
                >
                  {isCompleted ? (
                    <span style={{ fontSize: 28, color: "#fff" }}>✓</span>
                  ) : (
                    <span style={{ fontSize: 24, color: "#fff", fontWeight: 700 }}>
                      {index + 1}
                    </span>
                  )}
                </div>

                {/* Name */}
                <div
                  style={{
                    marginTop: 16,
                    fontSize: 18,
                    fontWeight: 600,
                    color: isCurrent ? theme.primaryColor : theme.textColor,
                    textAlign: "center",
                  }}
                >
                  {milestone.name}
                </div>

                {/* Description */}
                <div
                  style={{
                    marginTop: 8,
                    fontSize: 14,
                    color: theme.textColor,
                    opacity: 0.6,
                    textAlign: "center",
                    maxWidth: 150,
                  }}
                >
                  {milestone.description}
                </div>
              </div>

              {/* Connector line */}
              {index < milestones.length - 1 && (
                <div
                  style={{
                    width: 80,
                    height: 4,
                    backgroundColor: isCompleted ? theme.completedColor : "#4a5568",
                    marginTop: 28,
                    borderRadius: 2,
                    opacity: nodeSpring,
                  }}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
