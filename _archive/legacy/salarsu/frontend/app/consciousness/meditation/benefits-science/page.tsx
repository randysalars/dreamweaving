import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Benefits & Science of Meditation | Meditation",
  description: "Research-backed benefits and neuroscience of meditation",
  openGraph: {
    title: "Benefits & Science of Meditation",
    description: "Research-backed benefits and neuroscience of meditation",
    type: "article",
  },
};

const questions = [
  { text: "What does scientific research say about meditation benefits?", slug: "what-does-scientific-research-say-about-meditation-benefits" },
  { text: "How does meditation change the brain?", slug: "how-does-meditation-change-the-brain" },
  { text: "Can meditation help with stress and anxiety?", slug: "can-meditation-help-with-stress-and-anxiety" },
  { text: "Does meditation improve focus and concentration?", slug: "does-meditation-improve-focus-and-concentration" },
  { text: "Can meditation help with sleep problems?", slug: "can-meditation-help-with-sleep-problems" },
  { text: "How long before I notice benefits from meditation?", slug: "how-long-before-i-notice-benefits-from-meditation" },
  { text: "Does meditation improve emotional regulation?", slug: "does-meditation-improve-emotional-regulation" },
  { text: "Can meditation boost creativity?", slug: "can-meditation-boost-creativity" },
];

export default function BenefitsSciencePage() {
  return (
    <div className='min-h-screen bg-background'>
      <main className='container mx-auto px-4 py-12 max-w-4xl'>
        <Link
          href='/consciousness/meditation'
          className='text-primary hover:underline mb-6 inline-flex items-center gap-2'
        >
          <ArrowLeft className='h-4 w-4' />
          Back to Meditation
        </Link>

        <h1 className='text-4xl md:text-5xl font-bold mb-4 text-foreground'>
          Benefits & Science of Meditation
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          Research-backed benefits and neuroscience of meditation
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/meditation/benefits-science/${q.slug}`}
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
