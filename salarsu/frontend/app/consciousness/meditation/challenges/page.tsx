import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Common Challenges | Meditation",
  description: "Overcoming obstacles and difficulties in meditation practice",
  openGraph: {
    title: "Common Challenges",
    description: "Overcoming obstacles and difficulties in meditation practice",
    type: "article",
  },
};

const questions = [
  { text: "How do I deal with a busy or wandering mind during meditation?", slug: "how-do-i-deal-with-a-busy-or-wandering-mind-during-meditation" },
  { text: "What should I do if I feel restless or fidgety during meditation?", slug: "what-should-i-do-if-i-feel-restless-or-fidgety-during-meditation" },
  { text: "Why do I feel sleepy or fall asleep when I meditate?", slug: "why-do-i-feel-sleepy-or-fall-asleep-when-i-meditate" },
  { text: "How do I handle physical discomfort or pain while meditating?", slug: "how-do-i-handle-physical-discomfort-or-pain-while-meditating" },
  { text: "What if I do not have enough time to meditate?", slug: "what-if-i-do-not-have-enough-time-to-meditate" },
  { text: "Why does meditation sometimes feel boring or pointless?", slug: "why-does-meditation-sometimes-feel-boring-or-pointless" },
  { text: "Is it normal to feel worse after meditation?", slug: "is-it-normal-to-feel-worse-after-meditation" },
  { text: "What are difficult meditation experiences and how do I handle them?", slug: "what-are-difficult-meditation-experiences-and-how-do-i-handle-them" },
];

export default function ChallengesPage() {
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
          Common Challenges
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          Overcoming obstacles and difficulties in meditation practice
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/meditation/challenges/${q.slug}`}
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
