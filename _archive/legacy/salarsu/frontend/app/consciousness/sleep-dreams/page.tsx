import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, Layers, HelpCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/sleep-dreams`;

export const metadata: Metadata = {
  title: "Sleep & Dreams | Salars Consciousness",
  description: "Understanding sleep cycles, dream states, and consciousness during rest. Explore 90+ questions about sleep science, lucid dreaming, sleep optimization, and dream interpretation.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Sleep & Dreams | Salars Consciousness",
    description: "Understanding sleep cycles, dream states, and consciousness during rest. Explore sleep science, lucid dreaming, and dream interpretation.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "sleep science",
    "lucid dreaming",
    "sleep cycles",
    "rem sleep",
    "sleep optimization",
    "dream interpretation",
    "sleep hygiene",
    "hypnagogia",
    "dream recall",
    "sleep disorders",
    "circadian rhythm",
    "sleep and memory",
  ],
};

const categories = [
  {
    slug: "sleep-fundamentals",
    name: "Sleep Fundamentals",
    description: "How sleep works and why we need it",
    count: 12,
  },
  {
    slug: "dream-science",
    name: "Dream Science & Lucid Dreaming",
    description: "Understanding dreams, lucidity, and dream control",
    count: 15,
  },
  {
    slug: "sleep-consciousness",
    name: "Sleep & Consciousness States",
    description: "Sleep as altered state, hypnagogia, and awareness",
    count: 12,
  },
  {
    slug: "sleep-disorders",
    name: "Sleep Disorders & Solutions",
    description: "Common problems and evidence-based solutions",
    count: 14,
  },
  {
    slug: "sleep-optimization",
    name: "Sleep Optimization & Hygiene",
    description: "Improving sleep quality and establishing healthy habits",
    count: 15,
  },
  {
    slug: "sleep-performance",
    name: "Sleep & Performance",
    description: "How sleep affects memory, learning, and cognition",
    count: 12,
  },
  {
    slug: "dream-work",
    name: "Dream Work & Interpretation",
    description: "Working with dreams for insight and growth",
    count: 10,
  },
];

export default function SleepDreamsPage() {
  const totalQuestions = categories.reduce((sum, cat) => sum + cat.count, 0);

  return (
    <div className='min-h-screen bg-background'>
      <div className='container mx-auto px-4 py-8'>
        <Link
          href='/consciousness'
          className='text-primary hover:underline mb-4 inline-block'
        >
          <ArrowLeft className='h-4 w-4 inline mr-2' />
          Back to Consciousness
        </Link>

        <h1 className='text-4xl md:text-5xl font-bold mb-4 text-foreground'>
          Sleep & Dreams
        </h1>
        <p className='text-lg italic mb-6 text-muted-foreground'>
          Understanding the science of sleep cycles, altered states during rest,
          and the mysterious world of dreams. From sleep optimization to lucid
          dreaming, explore how consciousness transforms during our nightly journey.
        </p>

        <div className='mb-12 bg-card/70 text-card-foreground border p-8 rounded-lg'>
          <h2 className='text-3xl font-bold mb-6 text-foreground'>
            Why Study Sleep & Dreams?
          </h2>
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Improve sleep quality and daily performance
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Learn to navigate lucid dream states
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Enhance memory consolidation during sleep
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Understand consciousness in sleep states
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Address sleep disorders with evidence-based approaches
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Work with dreams for personal growth
              </span>
            </div>
          </div>
        </div>

        <div className='mb-12 bg-card/70 text-card-foreground border p-8 rounded-lg'>
          <h2 className='text-3xl font-bold mb-6 text-foreground'>
            Sleep as an Altered State
          </h2>
          <p className='text-lg text-foreground leading-relaxed mb-4'>
            Sleep is not simply an "off" state—it's a complex altered state of consciousness
            with distinct stages, each serving unique functions for brain health, memory,
            and psychological well-being.
          </p>
          <p className='text-lg text-foreground leading-relaxed mb-4'>
            During sleep, consciousness transforms through multiple cycles:
          </p>
          <div className='grid gap-4 md:grid-cols-2'>
            <div className='p-4 bg-background/50 rounded-lg'>
              <h3 className='text-xl font-semibold mb-2 text-foreground'>REM Sleep</h3>
              <p className='text-muted-foreground'>
                Where vivid dreams occur, characterized by rapid eye movements, increased
                brain activity, and temporary muscle paralysis. Essential for emotional
                processing and creative problem-solving.
              </p>
            </div>
            <div className='p-4 bg-background/50 rounded-lg'>
              <h3 className='text-xl font-semibold mb-2 text-foreground'>Deep Sleep</h3>
              <p className='text-muted-foreground'>
                The most restorative sleep stage, crucial for physical recovery, immune
                function, and memory consolidation. Brain waves slow dramatically into
                delta rhythms.
              </p>
            </div>
            <div className='p-4 bg-background/50 rounded-lg'>
              <h3 className='text-xl font-semibold mb-2 text-foreground'>Hypnagogia</h3>
              <p className='text-muted-foreground'>
                The liminal state between waking and sleeping, often featuring vivid imagery,
                creative insights, and altered perception. A gateway to lucid dreaming.
              </p>
            </div>
            <div className='p-4 bg-background/50 rounded-lg'>
              <h3 className='text-xl font-semibold mb-2 text-foreground'>Lucid Dreams</h3>
              <p className='text-muted-foreground'>
                Dreams where you're aware you're dreaming, allowing conscious exploration
                of the dream world. Used for creative practice, psychological exploration,
                and consciousness research.
              </p>
            </div>
          </div>
        </div>

        <div className='mb-12 bg-card/70 text-card-foreground border p-8 rounded-lg'>
          <h2 className='text-3xl font-bold mb-6 text-foreground'>
            Sleep & Performance
          </h2>
          <p className='text-lg text-foreground leading-relaxed mb-6'>
            Sleep is perhaps the single most powerful performance enhancer available.
            Research consistently shows that quality sleep:
          </p>
          <div className='space-y-3'>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <p className='text-foreground'>
                <strong>Consolidates memories</strong> - transferring learning from short-term
                to long-term storage during specific sleep stages
              </p>
            </div>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <p className='text-foreground'>
                <strong>Enhances creativity</strong> - making novel connections between
                ideas during REM sleep
              </p>
            </div>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <p className='text-foreground'>
                <strong>Regulates emotions</strong> - processing emotional experiences
                and maintaining psychological balance
              </p>
            </div>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <p className='text-foreground'>
                <strong>Clears metabolic waste</strong> - the glymphatic system actively
                removes toxins from the brain during deep sleep
              </p>
            </div>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <p className='text-foreground'>
                <strong>Maintains immune function</strong> - sleep deprivation significantly
                weakens the immune response
              </p>
            </div>
          </div>
        </div>

        <Separator className='my-16' />

        <section className='py-8'>
          <div className='text-center mb-12'>
            <Badge variant='outline' className='mb-4'>
              Question Hub
            </Badge>
            <h2 className='text-4xl md:text-5xl font-bold text-foreground mb-6'>
              Explore Common Questions About Sleep & Dreams
            </h2>
            <p className='text-xl text-muted-foreground max-w-3xl mx-auto'>
              {totalQuestions} answers to help optimize your sleep, understand
              dreams, and explore consciousness during rest
            </p>
          </div>

          <div className='grid gap-6 md:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto'>
            {categories.map((category) => (
              <Link
                key={category.slug}
                href={`/consciousness/sleep-dreams/${category.slug}`}
                className='group'
              >
                <div className='h-full p-6 rounded-2xl border border-border bg-card/40 hover:bg-card/60 transition-all hover:scale-105 hover:shadow-lg'>
                  <div className='flex items-center gap-3 mb-3'>
                    <div className='p-2 rounded-lg bg-primary/10'>
                      <Layers className='h-5 w-5 text-primary' />
                    </div>
                    <h3 className='text-xl font-semibold text-foreground group-hover:text-primary transition-colors'>
                      {category.name}
                    </h3>
                  </div>
                  <p className='text-sm text-muted-foreground mb-4'>
                    {category.description}
                  </p>
                  <div className='flex items-center gap-2 text-sm text-primary'>
                    <HelpCircle className='h-4 w-4' />
                    <span>{category.count} questions</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>

        <div className='mt-16 bg-card/70 text-card-foreground border p-8 rounded-lg'>
          <h2 className='text-3xl font-bold mb-6 text-foreground'>
            Related Topics
          </h2>
          <div className='grid gap-4 md:grid-cols-3'>
            <Link href='/consciousness/altered-states' className='p-4 bg-background/50 rounded-lg hover:bg-background/70 transition-colors'>
              <h3 className='text-xl font-semibold mb-2 text-primary'>Altered States</h3>
              <p className='text-sm text-muted-foreground'>
                Explore other altered states of consciousness and how they relate to sleep
              </p>
            </Link>
            <Link href='/consciousness/meditation' className='p-4 bg-background/50 rounded-lg hover:bg-background/70 transition-colors'>
              <h3 className='text-xl font-semibold mb-2 text-primary'>Meditation</h3>
              <p className='text-sm text-muted-foreground'>
                Learn meditation practices that can improve sleep quality
              </p>
            </Link>
            <Link href='/consciousness/memory-systems' className='p-4 bg-background/50 rounded-lg hover:bg-background/70 transition-colors'>
              <h3 className='text-xl font-semibold mb-2 text-primary'>Memory Systems</h3>
              <p className='text-sm text-muted-foreground'>
                Understand how sleep consolidates memories and enhances learning
              </p>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
