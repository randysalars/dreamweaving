import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Classic Memory Techniques | Memory Systems",
  description: "Time-tested methods like Memory Palace and mnemonics",
  openGraph: {
    title: "Classic Memory Techniques",
    description: "Time-tested methods like Memory Palace and mnemonics",
    type: "article",
  },
};

const questions = [
  { text: "What is the Method of Loci (Memory Palace) technique?", slug: "what-is-the-method-of-loci-memory-palace-technique" },
  { text: "How do I build and use a Memory Palace effectively?", slug: "how-do-i-build-and-use-a-memory-palace-effectively" },
  { text: "What are mnemonic devices and how do they work?", slug: "what-are-mnemonic-devices-and-how-do-they-work" },
  { text: "How does the peg system work for memorizing lists?", slug: "how-does-the-peg-system-work-for-memorizing-lists" },
  { text: "What is chunking and how does it improve memory?", slug: "what-is-chunking-and-how-does-it-improve-memory" },
  { text: "How does the link method work for memorization?", slug: "how-does-the-link-method-work-for-memorization" },
  { text: "What is the story method for remembering information?", slug: "what-is-the-story-method-for-remembering-information" },
  { text: "How do acronyms and acrostics help with memory?", slug: "how-do-acronyms-and-acrostics-help-with-memory" },
  { text: "What is the substitution method for abstract concepts?", slug: "what-is-the-substitution-method-for-abstract-concepts" },
  { text: "How does the Major System work for numbers?", slug: "how-does-the-major-system-work-for-numbers" },
  { text: "What is the Dominic System for memory?", slug: "what-is-the-dominic-system-for-memory" },
  { text: "How can visualization enhance memory techniques?", slug: "how-can-visualization-enhance-memory-techniques" },
];

export default function ClassicTechniquesPage() {
  return (
    <div className='min-h-screen bg-background'>
      <main className='container mx-auto px-4 py-12 max-w-4xl'>
        <Link
          href='/consciousness/memory-systems'
          className='text-primary hover:underline mb-6 inline-flex items-center gap-2'
        >
          <ArrowLeft className='h-4 w-4' />
          Back to Memory Systems
        </Link>

        <h1 className='text-4xl md:text-5xl font-bold mb-4 text-foreground'>
          Classic Memory Techniques
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          Time-tested methods like Memory Palace and mnemonics
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/memory-systems/classic-techniques/${q.slug}`}
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
