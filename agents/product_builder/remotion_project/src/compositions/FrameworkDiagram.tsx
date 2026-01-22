import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  spring,
  useVideoConfig,
} from "remotion";

interface FrameworkDiagramProps {
  title: string;
  centerLabel: string;
  elements: Array<{
    label: string;
    description?: string;
  }>;
  theme?: {
    primaryColor: string;
    backgroundColor: string;
    textColor: string;
  };
}

/**
 * Framework Diagram
 * Circular diagram showing connected concepts.
 */
export const FrameworkDiagram: React.FC<FrameworkDiagramProps> = ({
  title,
  centerLabel,
  elements,
  theme = {
    primaryColor: "#9F7AEA",
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

  const centerSpring = spring({
    frame: frame - 30,
    fps,
    config: { damping: 12, stiffness: 100 },
  });

  const radius = 280;
  const angleStep = (2 * Math.PI) / elements.length;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.backgroundColor,
        padding: 60,
      }}
    >
      {/* Title */}
      <h1
        style={{
          fontSize: 48,
          fontWeight: 700,
          color: theme.textColor,
          textAlign: "center",
          marginBottom: 40,
          opacity: titleSpring,
        }}
      >
        {title}
      </h1>

      {/* Diagram container */}
      <div
        style={{
          position: "relative",
          width: 800,
          height: 800,
          margin: "0 auto",
        }}
      >
        {/* Connection lines */}
        <svg
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
          }}
        >
          {elements.map((_, index) => {
            const angle = angleStep * index - Math.PI / 2;
            const x = 400 + radius * Math.cos(angle);
            const y = 400 + radius * Math.sin(angle);
            
            const lineSpring = spring({
              frame: frame - 60 - index * 10,
              fps,
              config: { damping: 15, stiffness: 60 },
            });

            return (
              <line
                key={index}
                x1={400}
                y1={400}
                x2={x}
                y2={y}
                stroke={theme.primaryColor}
                strokeWidth={3}
                strokeDasharray="10,5"
                opacity={lineSpring * 0.5}
              />
            );
          })}
        </svg>

        {/* Center circle */}
        <div
          style={{
            position: "absolute",
            left: 400 - 100,
            top: 400 - 100,
            width: 200,
            height: 200,
            borderRadius: "50%",
            backgroundColor: theme.primaryColor,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            transform: `scale(${centerSpring})`,
            boxShadow: `0 10px 40px ${theme.primaryColor}40`,
          }}
        >
          <span
            style={{
              fontSize: 24,
              fontWeight: 700,
              color: "#ffffff",
              textAlign: "center",
              padding: 20,
            }}
          >
            {centerLabel}
          </span>
        </div>

        {/* Outer elements */}
        {elements.map((element, index) => {
          const angle = angleStep * index - Math.PI / 2;
          const x = 400 + radius * Math.cos(angle);
          const y = 400 + radius * Math.sin(angle);

          const elementSpring = spring({
            frame: frame - 60 - index * 15,
            fps,
            config: { damping: 12, stiffness: 80 },
          });

          return (
            <div
              key={index}
              style={{
                position: "absolute",
                left: x - 80,
                top: y - 50,
                width: 160,
                textAlign: "center",
                opacity: elementSpring,
                transform: `scale(${elementSpring})`,
              }}
            >
              <div
                style={{
                  width: 100,
                  height: 100,
                  borderRadius: "50%",
                  backgroundColor: "#ffffff",
                  border: `4px solid ${theme.primaryColor}`,
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  margin: "0 auto",
                  fontSize: 14,
                  fontWeight: 600,
                  color: theme.textColor,
                  padding: 10,
                  boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
                }}
              >
                {element.label}
              </div>
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
