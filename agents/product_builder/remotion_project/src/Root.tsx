import { Composition } from "remotion";
import { ChapterVideo } from "./compositions/ChapterVideo";
import { AudioNarration } from "./compositions/AudioNarration";
import { CourseIntro } from "./compositions/CourseIntro";
import { ChapterCard } from "./compositions/ChapterCard";
import { KeyInsight } from "./compositions/KeyInsight";
import { Checklist } from "./compositions/Checklist";
import { QuoteCard } from "./compositions/QuoteCard";
import { ProgressMilestone } from "./compositions/ProgressMilestone";
import { BeforeAfter } from "./compositions/BeforeAfter";
import { Statistic } from "./compositions/Statistic";
import { FrameworkDiagram } from "./compositions/FrameworkDiagram";
// Video Framework components (7-part anatomy)
import { LessonVideo, calculateTotalDuration } from "./compositions/LessonVideo";

/**
 * Root component that registers all video/audio compositions.
 * These compositions are rendered via the Remotion CLI.
 */
export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Main chapter video with slides and narration */}
      <Composition
        id="ChapterVideo"
        component={ChapterVideo}
        durationInFrames={900}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          title: "Chapter Title",
          content: "Chapter content goes here",
          slides: [],
          style: {},
          theme: {
            primaryColor: "#9F7AEA",
            backgroundColor: "#FAF5FF",
            textColor: "#2D3748",
            fontFamily: "Inter, system-ui, sans-serif",
          },
        }}
      />

      {/* Audio-only narration */}
      <Composition
        id="AudioNarration"
        component={AudioNarration}
        durationInFrames={1800}
        fps={30}
        width={1}
        height={1}
        defaultProps={{
          title: "Audio Title",
          audioScript: "Narration script goes here",
          voiceId: "default",
        }}
      />

      {/* Course intro animation */}
      <Composition
        id="CourseIntro"
        component={CourseIntro}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          courseTitle: "Course Title",
          subtitle: "Transform your understanding",
          authorName: "SalarsNet",
        }}
      />

      {/* Chapter card for social sharing */}
      <Composition
        id="ChapterCard"
        component={ChapterCard}
        durationInFrames={150}
        fps={30}
        width={1200}
        height={630}
        defaultProps={{
          chapterNumber: 1,
          chapterTitle: "Getting Started",
          keyTakeaway: "The most important insight...",
        }}
      />

      {/* Key Insight highlight */}
      <Composition
        id="KeyInsight"
        component={KeyInsight}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          insightText: "The key insight goes here",
          context: "Context name",
          chapterNumber: 1,
        }}
      />

      {/* Animated Checklist */}
      <Composition
        id="Checklist"
        component={Checklist}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          title: "Action Steps",
          items: ["Step one", "Step two", "Step three"],
        }}
      />

      {/* Quote Card */}
      <Composition
        id="QuoteCard"
        component={QuoteCard}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          quote: "The quote goes here",
          author: "Author Name",
          context: "Book Title",
        }}
      />

      {/* Progress Milestone */}
      <Composition
        id="ProgressMilestone"
        component={ProgressMilestone}
        durationInFrames={360}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          milestones: [
            { name: "Foundation", description: "Core concepts", completed: true },
            { name: "Application", description: "First practice", completed: true },
            { name: "Mastery", description: "Full implementation", completed: false },
          ],
          currentMilestone: 2,
        }}
      />

      {/* Before/After Transformation */}
      <Composition
        id="BeforeAfter"
        component={BeforeAfter}
        durationInFrames={360}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          before: {
            title: "Before",
            points: ["Confused about next steps", "No clear system", "Overwhelmed"],
          },
          after: {
            title: "After",
            points: ["Clear roadmap", "Working system", "Confident execution"],
          },
        }}
      />

      {/* Statistic Highlight */}
      <Composition
        id="Statistic"
        component={Statistic}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          value: "10000",
          label: "Students Transformed",
          suffix: "+",
          description: "And counting...",
        }}
      />

      {/* Framework Diagram */}
      <Composition
        id="FrameworkDiagram"
        component={FrameworkDiagram}
        durationInFrames={420}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          title: "The Core Framework",
          centerLabel: "Your Goal",
          elements: [
            { label: "Foundation" },
            { label: "Strategy" },
            { label: "Execution" },
            { label: "Optimization" },
          ],
        }}
      />

      {/* Educational Lesson Video - 7-part anatomy */}
      <Composition
        id="LessonVideo"
        component={LessonVideo}
        durationInFrames={3600}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          video: {
            id: "sample-lesson-01",
            title: "Sample Lesson",
            fps: 30,
            theme: "salars_clean_01",
          },
          scenes: [
            {
              id: "s01_preview",
              learning_role: "visual_preview",
              template: "VisualPreview",
              duration_sec: 6,
              visuals: [
                { type: "icon", key: "menu" },
                { type: "icon", key: "plate" },
                { type: "icon", key: "cash" },
              ],
            },
            {
              id: "s02_goal",
              learning_role: "goal_statement",
              template: "GoalStatement",
              duration_sec: 8,
              narration: { text: "In this lesson, you will learn three key words." },
              visuals: [{ type: "text", headline: "Goal", subhead: "Learn 3 key words" }],
            },
            {
              id: "s03_explain",
              learning_role: "core_explanation",
              template: "CoreExplanation",
              duration_sec: 60,
              visuals: [{ type: "deck", bullets: ["Menu", "Order", "Pay"] }],
            },
            {
              id: "s04_pause",
              learning_role: "guided_pause",
              template: "GuidedPause",
              duration_sec: 8,
              visuals: [{ type: "text", headline: "Pause. Think. Repeat." }],
            },
            {
              id: "s05_check",
              learning_role: "check_understanding",
              template: "MiniCheck",
              duration_sec: 20,
              visuals: [{ type: "quiz", prompt: "Which word means the list of food?", answer: "menu" }],
            },
          ],
          style_tokens: {
            primary_color: "#9F7AEA",
            background_color: "#1a1a2e",
            accent_color: "#9F7AEA",
          },
        }}
      />
    </>
  );
};

