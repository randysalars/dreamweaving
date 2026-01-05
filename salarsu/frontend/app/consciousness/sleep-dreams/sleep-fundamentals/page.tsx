import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Sleep Fundamentals | Sleep & Dreams",
  description: "How sleep works and why we need it",
  openGraph: {
    title: "Sleep Fundamentals",
    description: "How sleep works and why we need it",
    type: "article",
  },
};

const questions = [
  { text: "What are the stages of sleep and what happens in each?", slug: "what-are-the-stages-of-sleep-and-what-happens-in-each" },
  { text: "Why do we need sleep?", slug: "why-do-we-need-sleep" },
  { text: "How much sleep do adults actually need?", slug: "how-much-sleep-do-adults-actually-need" },
  { text: "What is the circadian rhythm and how does it affect sleep?", slug: "what-is-the-circadian-rhythm-and-how-does-it-affect-sleep" },
  { text: "What is REM sleep and why is it important?", slug: "what-is-rem-sleep-and-why-is-it-important" },
  { text: "What is non-REM sleep?", slug: "what-is-non-rem-sleep" },
  { text: "How does sleep change with age?", slug: "how-does-sleep-change-with-age" },
  { text: "What happens in the brain during sleep?", slug: "what-happens-in-the-brain-during-sleep" },
  { text: "What is the role of melatonin in sleep?", slug: "what-is-the-role-of-melatonin-in-sleep" },
  { text: "How long is a complete sleep cycle?", slug: "how-long-is-a-complete-sleep-cycle" },
  { text: "What is deep sleep and why is it important?", slug: "what-is-deep-sleep-and-why-is-it-important" },
  { text: "Can you make up for lost sleep?", slug: "can-you-make-up-for-lost-sleep" },
];

export default function SleepFundamentalsPage() {
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
          Sleep Fundamentals
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          How sleep works and why we need it
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/sleep-dreams/sleep-fundamentals/${q.slug}`}
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
