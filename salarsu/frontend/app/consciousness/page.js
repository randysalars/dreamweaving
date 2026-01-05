'use client';

import Link from 'next/link';
import { ModernHero } from '../../components/ui/modern-hero';
import { AnimatedCard } from '../../components/ui/animated-cards';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { Separator } from '../../components/ui/separator';

export default function ConsciousnessPage() {
  return (
    <div className='min-h-screen'>
      {/* Modern Hero Section */}
      <ModernHero
        title='Learning & Consciousness'
        subtitle='✨ Mind Expansion & Awareness'
        description='Explore the frontiers of mind, awareness, and human potential through practices and insights that expand your cognitive and perceptual capacities.'
        badges={[
          'Mind Explorer',
          'Cognitive Enhancement',
          'Awareness Training',
          'Learning Optimization',
        ]}
        primaryCta={{
          text: 'Start Exploring',
          href: '#expanding-awareness',
        }}
        secondaryCta={{
          text: 'Learn Methods',
          href: '#accelerated-learning',
        }}
        backgroundImage='/images/consciousness.png'
        className='animate-fade-in'
      />

      {/* Expanding Awareness */}
      <section
        id='expanding-awareness'
        className='container mx-auto px-4 py-20'
      >
        <div className='text-center mb-16'>
          <Badge variant='outline' className='mb-4 animate-fade-in'>
            Consciousness Expansion
          </Badge>
          <h2 className='text-4xl md:text-5xl font-bold text-foreground mb-6 animate-slide-up'>
            Expanding Awareness
          </h2>
          <p className='text-xl text-muted-foreground max-w-3xl mx-auto animate-slide-up'>
            Practices for broadening perception, cultivating presence, and
            accessing heightened states of consciousness
          </p>
        </div>

        <AnimatedCard
          className='max-w-4xl mx-auto p-8 animate-slide-up'
          hoverEffect='glow'
        >
          <p className='text-lg md:text-xl text-muted-foreground leading-relaxed mb-6'>
            Expanding awareness is not just about extraordinary experiences—it's
            about deepening your connection to the present moment and noticing
            subtle shifts in your thoughts, feelings, and environment. By
            training your perception, you can unlock new levels of insight,
            creativity, and empathy.
          </p>

          <div className='grid gap-6 md:grid-cols-2 lg:grid-cols-5 mt-8'>
            <Link href='/consciousness/perceptual-exercises'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>👁️</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Perceptual Exercises
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Shift habitual patterns of perception
                </p>
              </AnimatedCard>
            </Link>

            <Link href='/consciousness/meditation'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>🧘</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Meditation
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Cultivate awareness and inner calm
                </p>
              </AnimatedCard>
            </Link>

            <Link href='/consciousness/mindfulness'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>🌿</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Mindfulness
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Increase present-moment awareness
                </p>
              </AnimatedCard>
            </Link>

            <Link href='/consciousness/altered-states'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>🌀</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Altered States
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Explore non-ordinary consciousness
                </p>
              </AnimatedCard>
            </Link>

            <Link href='/consciousness/sleep-dreams'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>🌙</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Sleep & Dreams
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Explore sleep states and dream consciousness
                </p>
              </AnimatedCard>
            </Link>

            <Link href='/consciousness/integration'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>⚓</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Integration & Grounding
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Embody insights and stay functional
                </p>
              </AnimatedCard>
            </Link>
          </div>
        </AnimatedCard>

        {/* Featured Digital Product */}
        <div className='mt-16 max-w-4xl mx-auto'>
          <AnimatedCard className='p-8 bg-gradient-to-br from-indigo-900/10 to-transparent border-indigo-200/20' hoverEffect='scale' gradient>
            <div className='flex flex-col md:flex-row items-center gap-8'>
              <div className='flex-1'>
                <Badge className='mb-3 bg-indigo-600 hover:bg-indigo-700'>Featured Guide</Badge>
                <h3 className='text-2xl font-bold mb-3'>Mind Expansion Techniques</h3>
                <p className='text-muted-foreground mb-6'>
                  Explore the frontiers of consciousness through proven, safe techniques. Covers breathwork, meditation, sensory protocols, and creative flow states with 8 guided audio sessions.
                </p>
                <Button asChild size='lg' className='w-full md:w-auto'>
                  <Link href='/digital/mind-expansion-techniques'>
                    Start Expanding <span className='ml-2'>→</span>
                  </Link>
                </Button>
              </div>
              <div className='w-full md:w-1/3 aspect-[3/4] rounded-lg overflow-hidden relative shadow-xl'>
                <div className='absolute inset-0 bg-gradient-to-br from-indigo-800 to-indigo-900 flex items-center justify-center text-indigo-100'>
                  <div className='text-center p-4'>
                    <div className='text-4xl mb-2'>🧠</div>
                    <div className='font-serif text-sm'>Audio Course</div>
                  </div>
                </div>
              </div>
            </div>
          </AnimatedCard>
        </div>

        {/* Mental States Map */}
        <div className='mt-8 max-w-4xl mx-auto'>
          <AnimatedCard className='p-8 border border-border/60' hoverEffect='scale'>
            <div className='flex flex-col md:flex-row items-center gap-8'>
              <div className='flex-1'>
                <Badge variant='outline' className='mb-3'>
                  Reference Map
                </Badge>
                <h3 className='text-2xl font-bold mb-3'>
                  The Complete Map of Consciousness‑Altering Mental States
                </h3>
                <p className='text-muted-foreground mb-6'>
                  A practical orientation layer: states → mechanisms → outcomes. Use it to
                  diagnose why effort is failing (and which lever actually shifts the state).
                </p>
                <Button asChild size='lg' className='w-full md:w-auto'>
                  <Link href='/consciousness/mental-states-map'>
                    Open the Map <span className='ml-2'>→</span>
                  </Link>
                </Button>
              </div>
              <div className='w-full md:w-1/3 aspect-[3/4] rounded-lg overflow-hidden relative shadow-xl'>
                <div className='absolute inset-0 bg-gradient-to-br from-slate-800 to-slate-950 flex items-center justify-center text-slate-100'>
                  <div className='text-center p-4'>
                    <div className='text-4xl mb-2'>🗺️</div>
                    <div className='font-serif text-sm'>Mental States</div>
                  </div>
                </div>
              </div>
            </div>
          </AnimatedCard>
        </div>
      </section>

      <Separator className='my-16' />

      {/* Accelerated Learning */}
      <section
        id='accelerated-learning'
        className='container mx-auto px-4 py-20'
      >
        <div className='text-center mb-16'>
          <Badge variant='outline' className='mb-4 animate-fade-in'>
            Learning Enhancement
          </Badge>
          <h2 className='text-4xl md:text-5xl font-bold text-foreground mb-6 animate-slide-up'>
            Accelerated Learning
          </h2>
          <p className='text-xl text-muted-foreground max-w-3xl mx-auto animate-slide-up'>
            Discover powerful approaches to knowledge acquisition that work with
            your brain's natural processes
          </p>
        </div>

        <AnimatedCard
          className='max-w-4xl mx-auto p-8 animate-slide-up'
          hoverEffect='glow'
        >
          <p className='text-lg md:text-xl text-muted-foreground leading-relaxed mb-6'>
            Accelerated learning combines proven techniques from cognitive
            science with practical strategies for mastering new skills quickly.
            Whether you're a student, professional, or lifelong learner, these
            methods can help you absorb information more efficiently and apply
            it with confidence.
          </p>

          <div className='grid gap-6 md:grid-cols-3 mt-8'>
            <Link href='/consciousness/memory-systems'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>🧠</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Memory Systems
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Encode and retrieve information effectively
                </p>
              </AnimatedCard>
            </Link>

            <Link href='/consciousness/speed-reading'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>📚</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Speed Reading
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Increase reading speed and comprehension
                </p>
              </AnimatedCard>
            </Link>

            <Link href='/consciousness/concept-mapping'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>🗺️</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Concept Mapping
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Organize and connect ideas visually
                </p>
              </AnimatedCard>
            </Link>
          </div>
        </AnimatedCard>
      </section>

      <Separator className='my-16' />

      {/* Cognitive Optimization */}
      <section className='container mx-auto px-4 py-20'>
        <div className='text-center mb-16'>
          <Badge variant='outline' className='mb-4 animate-fade-in'>
            Mental Performance
          </Badge>
          <h2 className='text-4xl md:text-5xl font-bold text-foreground mb-6 animate-slide-up'>
            Cognitive Optimization
          </h2>
          <p className='text-xl text-muted-foreground max-w-3xl mx-auto animate-slide-up'>
            Practices for enhancing focus, processing speed, and mental clarity
            through neurologically-informed approaches
          </p>
        </div>

        <AnimatedCard
          className='max-w-4xl mx-auto p-8 animate-slide-up'
          hoverEffect='glow'
        >
          <p className='text-lg md:text-xl text-muted-foreground leading-relaxed mb-6'>
            Cognitive optimization is about tuning your mental habits and
            environment for peak performance. By understanding how your brain
            works and adopting supportive routines, you can boost productivity,
            reduce mental fatigue, and maintain clarity even under pressure.
          </p>

          <div className='grid gap-6 md:grid-cols-3 mt-8'>
            <Link href='/consciousness/focus-training'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>🎯</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Focus Training
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Improve sustained attention
                </p>
              </AnimatedCard>
            </Link>

            <Link href='/consciousness/processing-speed'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>⚡</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Processing Speed
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Increase mental agility
                </p>
              </AnimatedCard>
            </Link>

            <Link href='/consciousness/neuroplasticity'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>🔄</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Neuroplasticity
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Support brain growth and adaptability
                </p>
              </AnimatedCard>
            </Link>
          </div>
        </AnimatedCard>
      </section>

      <Separator className='my-16' />

      {/* Learning Frameworks */}
      <section className='container mx-auto px-4 py-20'>
        <div className='text-center mb-16'>
          <Badge variant='outline' className='mb-4 animate-fade-in'>
            Learning Systems
          </Badge>
          <h2 className='text-4xl md:text-5xl font-bold text-foreground mb-6 animate-slide-up'>
            Learning Frameworks
          </h2>
          <p className='text-xl text-muted-foreground max-w-3xl mx-auto animate-slide-up'>
            Structural approaches to organizing knowledge acquisition that
            maximize comprehension and application
          </p>
        </div>

        <AnimatedCard
          className='max-w-4xl mx-auto p-8 animate-slide-up'
          hoverEffect='glow'
        >
          <p className='text-lg md:text-xl text-muted-foreground leading-relaxed mb-6'>
            Learning frameworks provide a roadmap for tackling complex subjects
            and integrating new knowledge. By using structured methods, you can
            break down big goals into manageable steps, track your progress, and
            adapt your approach as you grow.
          </p>

          <div className='grid gap-6 md:grid-cols-3 mt-8'>
            <Link href='/consciousness/spaced-repetition'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>📅</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Spaced Repetition
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Boost long-term retention
                </p>
              </AnimatedCard>
            </Link>

            <Link href='/consciousness/active-recall'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>💭</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Active Recall
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Strengthen memory through testing
                </p>
              </AnimatedCard>
            </Link>

            <Link href='/consciousness/multimodal-learning'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>🎨</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Multimodal Learning
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Combine visual, auditory, and kinesthetic methods
                </p>
              </AnimatedCard>
            </Link>
          </div>
        </AnimatedCard>
      </section>

      <Separator className='my-16' />

      {/* Integration & Practice */}
      <section className='container mx-auto px-4 py-20'>
        <AnimatedCard
          className='max-w-4xl mx-auto text-center p-12 animate-slide-up'
          hoverEffect='glow'
          gradient
        >
          <h2 className='text-4xl md:text-5xl font-bold text-foreground mb-6'>
            Integration & Practice
          </h2>
          <p className='text-xl text-muted-foreground mb-8 max-w-3xl mx-auto'>
            The journey of consciousness expansion and accelerated learning
            isn't just about collecting techniques—it's about integrating them
            into a cohesive practice that transforms your experience of reality
            and capacity for knowledge.
          </p>

          <div className='grid gap-6 md:grid-cols-3 mb-8'>
            <Link href='/consciousness/habit-formation'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>🔄</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Habit Formation
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Make new practices stick
                </p>
              </AnimatedCard>
            </Link>

            <Link href='/consciousness/journaling'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>📝</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Journaling
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Reflective writing for growth
                </p>
              </AnimatedCard>
            </Link>

            <Link href='/consciousness/self-assessment'>
              <AnimatedCard
                className='h-full group cursor-pointer text-center p-6'
                hoverEffect='lift'
              >
                <div className='text-4xl mb-3'>📊</div>
                <h3 className='text-lg font-semibold text-foreground mb-2'>
                  Self-Assessment
                </h3>
                <p className='text-sm text-muted-foreground'>
                  Track progress and adjust approach
                </p>
              </AnimatedCard>
            </Link>
          </div>

          <p className='text-lg text-muted-foreground'>
            Through consistent application and experimentation with these
            approaches, you can develop a personalized system for navigating
            both inner and outer realms with greater awareness, understanding,
            and effectiveness.
          </p>
        </AnimatedCard>
      </section>
    </div>
  );
}
