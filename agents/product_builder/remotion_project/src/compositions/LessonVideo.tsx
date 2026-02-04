import React from 'react';
import { Composition, Sequence, AbsoluteFill, Audio, staticFile } from 'remotion';
import { VisualPreview } from './VisualPreview';
import { GoalStatement } from './GoalStatement';
import { CoreExplanation } from './CoreExplanation';
import { Reinforcement } from './Reinforcement';
import { GuidedPause } from './GuidedPause';
import { MiniCheck } from './MiniCheck';
import { NextLessonPreview } from './NextLessonPreview';

// Scene types matching the JSON schema
interface Scene {
  id: string;
  learning_role: string;
  template: string;
  duration_sec: number;
  narration?: {
    text: string;
    voice_text?: string;
    audio_path?: string;
    pace?: number;
  };
  visuals?: Array<{
    type: string;
    key?: string;
    headline?: string;
    subhead?: string;
    bullets?: string[];
    prompt?: string;
    choices?: string[];
    answer?: string;
  }>;
  captions?: {
    enabled: boolean;
    mode: string;
  };
}

interface LessonVideoProps {
  video: {
    id: string;
    title: string;
    fps?: number;
    theme?: string;
  };
  scenes: Scene[];
  style_tokens?: {
    primary_color?: string;
    background_color?: string;
    accent_color?: string;
  };
}

/**
 * LessonVideo Master Composition
 * 
 * Sequences the 7-part video anatomy from lesson JSON:
 * 1. Visual Preview (5-10 sec) - Prime comprehension
 * 2. Goal Statement (8 sec) - Set expectations
 * 3. Core Explanation (2-4 min) - Teach the concept
 * 4. Reinforcement (30 sec) - Lock meaning visually
 * 5. Guided Pause (5-10 sec) - Let brain catch up
 * 6. Mini Check (20 sec) - Active recall
 * 7. Next Preview (10 sec) - Maintain momentum
 */
export const LessonVideo: React.FC<LessonVideoProps> = ({
  video,
  scenes,
  style_tokens = {}
}) => {
  const fps = video.fps || 30;
  const theme = {
    backgroundColor: style_tokens.background_color || '#1a1a2e',
    textColor: '#ffffff',
    accentColor: style_tokens.accent_color || '#9F7AEA',
    highlightColor: style_tokens.primary_color || '#9F7AEA',
  };
  
  // Calculate frame positions for each scene
  let currentFrame = 0;
  const sceneFrames: Array<{ scene: Scene; startFrame: number; durationFrames: number }> = [];
  
  for (const scene of scenes) {
    const durationFrames = Math.round(scene.duration_sec * fps);
    sceneFrames.push({
      scene,
      startFrame: currentFrame,
      durationFrames,
    });
    currentFrame += durationFrames;
  }
  
  return (
    <AbsoluteFill style={{ backgroundColor: theme.backgroundColor }}>
      {sceneFrames.map(({ scene, startFrame, durationFrames }) => (
        <Sequence
          key={scene.id}
          from={startFrame}
          durationInFrames={durationFrames}
          name={scene.id}
        >
          {renderScene(scene, theme)}
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

/**
 * Render appropriate component based on scene template
 */
function renderScene(scene: Scene, theme: any): React.ReactNode {
  const { template, visuals = [], narration } = scene;
  
  // Extract common visual data
  const icons = visuals
    .filter(v => v.type === 'icon')
    .map(v => v.key || '');
  
  const keywords = visuals
    .filter(v => v.type === 'deck' || v.type === 'text')
    .flatMap(v => v.bullets || [v.headline].filter(Boolean));
  
  const quizVisual = visuals.find(v => v.type === 'quiz');
  const textVisual = visuals.find(v => v.type === 'text');
  
  switch (template) {
    case 'VisualPreview':
      return <VisualPreview icons={icons} theme={theme} />;
      
    case 'GoalStatement':
      return (
        <GoalStatement
          goal={textVisual?.subhead || narration?.text || ''}
          theme={theme}
        />
      );
      
    case 'CoreExplanation':
      return (
        <>
          {narration?.audio_path && (
            <Audio src={staticFile(narration.audio_path)} />
          )}
          <CoreExplanation
            keywords={keywords.length > 0 ? keywords : ['Step 1', 'Step 2', 'Step 3']}
            theme={theme}
          />
        </>
      );
      
    case 'Reinforcement':
      return (
        <Reinforcement
          keywords={keywords.length > 0 ? keywords : ['Practice', 'Remember']}
          theme={theme}
        />
      );
      
    case 'GuidedPause':
      return (
        <GuidedPause
          text={textVisual?.headline || 'Pause. Think. Repeat.'}
          theme={theme}
        />
      );
      
    case 'MiniCheck':
      return (
        <>
          {narration?.audio_path && (
            <Audio src={staticFile(narration.audio_path)} />
          )}
          <MiniCheck
            question={quizVisual?.prompt || narration?.text || 'Check your understanding'}
            choices={quizVisual?.choices || []}
            answer={quizVisual?.answer || ''}
            theme={theme}
          />
        </>
      );
      
    case 'NextLessonPreview':
      return (
        <>
          {narration?.audio_path && (
            <Audio src={staticFile(narration.audio_path)} />
          )}
          <NextLessonPreview
            title={narration?.text || textVisual?.subhead || 'Coming up next...'}
            theme={theme}
          />
        </>
      );
      
    default:
      // Fallback to text display
      return (
        <AbsoluteFill
          style={{
            backgroundColor: theme.backgroundColor,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <div style={{ color: '#fff', fontSize: 32 }}>
            {scene.id}: {template}
          </div>
        </AbsoluteFill>
      );
  }
}

/**
 * Calculate total duration from scenes
 */
export function calculateTotalDuration(scenes: Scene[], fps: number = 30): number {
  return scenes.reduce((total, scene) => {
    return total + Math.round(scene.duration_sec * fps);
  }, 0);
}

export default LessonVideo;
