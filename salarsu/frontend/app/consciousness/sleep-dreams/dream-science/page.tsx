import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Dream Science & Lucid Dreaming | Sleep & Dreams",
  description: "Understanding dreams, lucidity, and dream control",
  openGraph: {
    title: "Dream Science & Lucid Dreaming",
    description: "Understanding dreams, lucidity, and dream control",
    type: "article",
  },
};

const questions = [
  { text: "What are dreams and why do we dream?", slug: "what-are-dreams-and-why-do-we-dream" },
  { text: "What is lucid dreaming?", slug: "what-is-lucid-dreaming" },
  { text: "How can I learn to lucid dream?", slug: "how-can-i-learn-to-lucid-dream" },
  { text: "What is dream recall and how can I improve it?", slug: "what-is-dream-recall-and-how-can-i-improve-it" },
  { text: "Why do some people remember dreams better than others?", slug: "why-do-some-people-remember-dreams-better-than-others" },
  { text: "What are the techniques for inducing lucid dreams?", slug: "what-are-the-techniques-for-inducing-lucid-dreams" },
  { text: "Do dreams have meaning?", slug: "do-dreams-have-meaning" },
  { text: "What causes vivid dreams?", slug: "what-causes-vivid-dreams" },
  { text: "What is the relationship between REM sleep and dreaming?", slug: "what-is-the-relationship-between-rem-sleep-and-dreaming" },
  { text: "Can you control your dreams?", slug: "can-you-control-your-dreams" },
  { text: "What are reality checks for lucid dreaming?", slug: "what-are-reality-checks-for-lucid-dreaming" },
  { text: "What is the WILD (Wake-Induced Lucid Dream) technique?", slug: "what-is-the-wild-wake-induced-lucid-dream-technique" },
  { text: "What is the MILD (Mnemonic Induction of Lucid Dreams) technique?", slug: "what-is-the-mild-mnemonic-induction-of-lucid-dreams-technique" },
  { text: "Are lucid dreams safe?", slug: "are-lucid-dreams-safe" },
  { text: "What is dream journaling and why is it important?", slug: "what-is-dream-journaling-and-why-is-it-important" },
];

export default function DreamSciencePage() {
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
          Dream Science & Lucid Dreaming
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          Understanding dreams, lucidity, and dream control
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/sleep-dreams/dream-science/${q.slug}`}
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
