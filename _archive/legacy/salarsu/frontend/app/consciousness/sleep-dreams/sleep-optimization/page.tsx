import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Sleep Optimization & Hygiene | Sleep & Dreams",
  description: "Improving sleep quality and establishing healthy habits",
  openGraph: {
    title: "Sleep Optimization & Hygiene",
    description: "Improving sleep quality and establishing healthy habits",
    type: "article",
  },
};

const questions = [
  { text: "What is sleep hygiene?", slug: "what-is-sleep-hygiene" },
  { text: "How does light exposure affect sleep?", slug: "how-does-light-exposure-affect-sleep" },
  { text: "What is the best sleeping position?", slug: "what-is-the-best-sleeping-position" },
  { text: "Do sleep trackers actually work?", slug: "do-sleep-trackers-actually-work" },
  { text: "What is the ideal bedroom temperature for sleep?", slug: "what-is-the-ideal-bedroom-temperature-for-sleep" },
  { text: "How does exercise affect sleep?", slug: "how-does-exercise-affect-sleep" },
  { text: "What foods help or hurt sleep?", slug: "what-foods-help-or-hurt-sleep" },
  { text: "Should you avoid screens before bed?", slug: "should-you-avoid-screens-before-bed" },
  { text: "What is the best bedtime routine?", slug: "what-is-the-best-bedtime-routine" },
  { text: "How does caffeine affect sleep?", slug: "how-does-caffeine-affect-sleep" },
  { text: "Does alcohol help or hurt sleep?", slug: "does-alcohol-help-or-hurt-sleep" },
  { text: "What role does the mattress and pillow play in sleep quality?", slug: "what-role-does-the-mattress-and-pillow-play-in-sleep-quality" },
  { text: "Should you nap during the day?", slug: "should-you-nap-during-the-day" },
  { text: "What is the best time to go to bed?", slug: "what-is-the-best-time-to-go-to-bed" },
  { text: "How can noise affect sleep quality?", slug: "how-can-noise-affect-sleep-quality" },
];

export default function SleepOptimizationPage() {
  return (
    <div className='min-h-screen bg-background'>
      <main className='container mx-auto px-4 py-12 max-w-4xl'>
        <Link
          href='/consciousness/sleep-dreams'
          className='text-primary hover:underline mb-6 inline-flex items-center gap-2'
        >
          <ArrowLeft className='h-4 w-4' />
          Back to Sleep & Dreams
        </Link>

        <h1 className='text-4xl md:text-5xl font-bold mb-4 text-foreground'>
          Sleep Optimization & Hygiene
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          Improving sleep quality and establishing healthy habits
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/sleep-dreams/sleep-optimization/${q.slug}`}
              className='block group'
            >
              <div className='p-6 rounded-xl border border-border bg-card/40 hover:bg-card/60 transition-all hover:scale-[1.02] hover:shadow-md'>
                <div className='flex items-start gap-4'>
                  <div className='p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors'>
                    <HelpCircle className='h-5 w-5 text-primary' />
                  </div>
                  <h2 className='text-lg font-semibold text-foreground group-hover:text-primary transition-colors flex-1'>
                    {q.text}
                  </h2>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
