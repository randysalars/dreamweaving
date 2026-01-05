import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Sleep & Consciousness States | Sleep & Dreams",
  description: "Sleep as altered state, hypnagogia, and awareness",
  openGraph: {
    title: "Sleep & Consciousness States",
    description: "Sleep as altered state, hypnagogia, and awareness",
    type: "article",
  },
};

const questions = [
  { text: "Is sleep an altered state of consciousness?", slug: "is-sleep-an-altered-state-of-consciousness" },
  { text: "What is hypnagogia (the transition to sleep)?", slug: "what-is-hypnagogia-the-transition-to-sleep" },
  { text: "Can you be conscious while sleeping?", slug: "can-you-be-conscious-while-sleeping" },
  { text: "What is sleep paralysis and why does it happen?", slug: "what-is-sleep-paralysis-and-why-does-it-happen" },
  { text: "What is the hypnopompic state (waking from sleep)?", slug: "what-is-the-hypnopompic-state-waking-from-sleep" },
  { text: "What are false awakenings?", slug: "what-are-false-awakenings" },
  { text: "Can meditation help with sleep?", slug: "can-meditation-help-with-sleep" },
  { text: "What is the relationship between mindfulness and sleep?", slug: "what-is-the-relationship-between-mindfulness-and-sleep" },
  { text: "What happens to consciousness during deep sleep?", slug: "what-happens-to-consciousness-during-deep-sleep" },
  { text: "Can you experience awareness during dreamless sleep?", slug: "can-you-experience-awareness-during-dreamless-sleep" },
  { text: "What is sleep meditation?", slug: "what-is-sleep-meditation" },
  { text: "How does consciousness differ between waking and dreaming?", slug: "how-does-consciousness-differ-between-waking-and-dreaming" },
];

export default function SleepConsciousnessPage() {
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
          Sleep & Consciousness States
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          Sleep as altered state, hypnagogia, and awareness
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/sleep-dreams/sleep-consciousness/${q.slug}`}
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
