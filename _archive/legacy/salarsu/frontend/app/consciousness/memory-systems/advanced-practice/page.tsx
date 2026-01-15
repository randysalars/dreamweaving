import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Advanced Practice | Memory Systems",
  description: "Competition techniques, mastery, and optimization",
  openGraph: {
    title: "Advanced Practice",
    description: "Competition techniques, mastery, and optimization",
    type: "article",
  },
};

const questions = [
  { text: "How do memory champions memorize decks of cards?", slug: "how-do-memory-champions-memorize-decks-of-cards" },
  { text: "What is the Major System for memorizing numbers?", slug: "what-is-the-major-system-for-memorizing-numbers" },
  { text: "How do I improve my recall speed?", slug: "how-do-i-improve-my-recall-speed" },
  { text: "What are advanced linking and chaining techniques?", slug: "what-are-advanced-linking-and-chaining-techniques" },
  { text: "How do memory athletes train for competitions?", slug: "how-do-memory-athletes-train-for-competitions" },
  { text: "What is the PAO (Person-Action-Object) system?", slug: "what-is-the-pao-person-action-object-system" },
  { text: "How do I create and manage multiple Memory Palaces?", slug: "how-do-i-create-and-manage-multiple-memory-palaces" },
  { text: "What are synesthesia techniques in memory work?", slug: "what-are-synesthesia-techniques-in-memory-work" },
  { text: "How do I memorize abstract concepts and ideas?", slug: "how-do-i-memorize-abstract-concepts-and-ideas" },
  { text: "What is the Dominic System?", slug: "what-is-the-dominic-system" },
  { text: "How can I develop eidetic (photographic) memory skills?", slug: "how-can-i-develop-eidetic-photographic-memory-skills" },
];

export default function AdvancedPracticePage() {
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
          Advanced Practice
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          Competition techniques, mastery, and optimization
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/memory-systems/advanced-practice/${q.slug}`}
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
