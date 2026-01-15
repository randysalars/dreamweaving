import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Sleep Disorders & Solutions | Sleep & Dreams",
  description: "Common problems and evidence-based solutions",
  openGraph: {
    title: "Sleep Disorders & Solutions",
    description: "Common problems and evidence-based solutions",
    type: "article",
  },
};

const questions = [
  { text: "What is insomnia and how is it treated?", slug: "what-is-insomnia-and-how-is-it-treated" },
  { text: "What causes sleep apnea?", slug: "what-causes-sleep-apnea" },
  { text: "What are parasomnias (sleepwalking, night terrors)?", slug: "what-are-parasomnias-sleepwalking-night-terrors" },
  { text: "How does shift work affect sleep?", slug: "how-does-shift-work-affect-sleep" },
  { text: "What is restless leg syndrome?", slug: "what-is-restless-leg-syndrome" },
  { text: "What is narcolepsy?", slug: "what-is-narcolepsy" },
  { text: "What are sleep disorders related to circadian rhythm?", slug: "what-are-sleep-disorders-related-to-circadian-rhythm" },
  { text: "What is sleep maintenance insomnia?", slug: "what-is-sleep-maintenance-insomnia" },
  { text: "What causes nightmares and how can they be reduced?", slug: "what-causes-nightmares-and-how-can-they-be-reduced" },
  { text: "What is delayed sleep phase syndrome?", slug: "what-is-delayed-sleep-phase-syndrome" },
  { text: "Can anxiety cause sleep problems?", slug: "can-anxiety-cause-sleep-problems" },
  { text: "What is REM sleep behavior disorder?", slug: "what-is-rem-sleep-behavior-disorder" },
  { text: "How do you know if you have a sleep disorder?", slug: "how-do-you-know-if-you-have-a-sleep-disorder" },
  { text: "What are non-medication treatments for insomnia?", slug: "what-are-non-medication-treatments-for-insomnia" },
];

export default function SleepDisordersPage() {
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
          Sleep Disorders & Solutions
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          Common problems and evidence-based solutions
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/sleep-dreams/sleep-disorders/${q.slug}`}
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
