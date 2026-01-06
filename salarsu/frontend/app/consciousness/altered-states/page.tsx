import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, Layers } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states`;

export const metadata: Metadata = {
  title: "Altered States of Consciousness | Salars Consciousness",
  description: "Comprehensive guide to altered states of consciousness - methods, techniques, and 124 research-based answers covering definitions, entry pathways, scientific understanding, safety, and integration.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Altered States of Consciousness",
    description: "Comprehensive guide to altered states of consciousness - methods, techniques, and research-based answers.",
    url: pageUrl,
    type: "website",
  },
  keywords: ["altered states", "consciousness", "meditation", "hypnosis", "flow state", "breathwork", "psychedelics", "neuroscience", "psychology"],
};

const categories = [
  {
    slug: "definitions-foundations",
    name: "Core Definitions & Foundations",
    description: "Fundamental concepts and definitions about altered states of consciousness.",
    count: 12,
  },
  {
    slug: "natural-vs-induced",
    name: "Natural vs Induced Altered States",
    description: "Understanding naturally occurring versus deliberately induced altered states.",
    count: 10,
  },
  {
    slug: "entry-pathways",
    name: "Entry Pathways & Triggers",
    description: "Methods and triggers that can induce altered states of consciousness.",
    count: 14,
  },
  {
    slug: "subjective-experience",
    name: "Subjective Experience & Perception Changes",
    description: "How altered states change perception, sensation, and subjective experience.",
    count: 14,
  },
  {
    slug: "levels-and-depth",
    name: "Levels, Depths & Intensity",
    description: "Understanding shallow vs deep altered states and factors affecting depth.",
    count: 10,
  },
  {
    slug: "duration-aftereffects",
    name: "Duration & Aftereffects",
    description: "How long altered states last and their lingering effects.",
    count: 8,
  },
  {
    slug: "safety-and-risks",
    name: "Safety, Risks & Stability",
    description: "Understanding risks, contraindications, and safe practices.",
    count: 12,
  },
  {
    slug: "cultural-historical",
    name: "Cultural & Historical Perspectives",
    description: "How different cultures and eras have understood altered states.",
    count: 10,
  },
  {
    slug: "scientific-neurological",
    name: "Scientific & Neurological Models",
    description: "What neuroscience and psychology tell us about altered states.",
    count: 10,
  },
  {
    slug: "integration-meaning",
    name: "Integration, Meaning & Daily Life",
    description: "Applying insights from altered states to everyday life.",
    count: 10,
  },
  {
    slug: "misconceptions",
    name: "Misconceptions & Clarifications",
    description: "Common myths and misunderstandings about altered states.",
    count: 8,
  },
  {
    slug: "navigational",
    name: "Navigational & Exploratory Prompts",
    description: "Comparative questions to help explore different altered states.",
    count: 6,
  },
];

export default function AlteredStatesPage() {
  const totalQuestions = categories.reduce((sum, cat) => sum + cat.count, 0);

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Breadcrumb */}
        <Link
          href="/consciousness"
          className="text-primary hover:underline mb-4 inline-block"
        >
          <ArrowLeft className="inline h-4 w-4 mr-1" />
          Back to Learning & Consciousness
        </Link>

        {/* Header */}
        <h1 className="text-4xl md:text-5xl font-bold mb-6 text-foreground">
          Altered States of Consciousness
        </h1>

        {/* Introduction */}
        <div className="mb-12 bg-card/70 border rounded-lg p-8">
          <p className="text-lg text-foreground mb-4">
            Altered states of consciousness are experiences in which perception,
            thought, emotion, or sense of self are significantly changed from
            ordinary waking awareness. These states can be reached through a wide
            variety of methods—some ancient, some modern, some physical, some
            emotional or creative.
          </p>

          {/* Common Methods */}
          <h2 className="text-3xl font-bold mb-6 text-foreground mt-8">
            Common Methods for Altering Consciousness
          </h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-lg text-foreground">
                <strong>Breathwork</strong>: Controlled breathing techniques (like holotropic breathwork,
                pranayama, Wim Hof Method) use specific breath patterns to induce
                heightened awareness, deep relaxation, or even visionary states.
                Studies show breathwork can produce mind-expanding,
                psychedelic-like experiences without drugs.
              </span>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-lg text-foreground">
                <strong>Meditation and Mindfulness</strong>: Focusing your mind or quieting your thoughts. Deep or guided
                meditation can lead to transcendental or mystical experiences.
                Mindfulness can alter time perception and increase clarity.
              </span>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-lg text-foreground">
                <strong>Sensory Deprivation</strong>: Reducing or eliminating external sensory input (float tanks,
                dark retreats, earplugs, blindfolds). This can trigger vivid
                imagery, deep introspection, and altered realities similar to
                psychedelic states.
              </span>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-lg text-foreground">
                <strong>Psychedelics and Entheogens</strong>: Consuming substances like psilocybin, LSD, ayahuasca, peyote, or
                DMT can dramatically change perception, thought, emotion, and
                spiritual connection.
              </span>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-lg text-foreground">
                <strong>Fasting and Sleep Deprivation</strong>: Altering eating or sleeping habits to affect your mind. Extended
                fasting and sleep deprivation can lead to visions, heightened
                senses, and unusual thought patterns—used in many spiritual
                traditions.
              </span>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-lg text-foreground">
                <strong>Sleep, Dreams, and Hypnagogia</strong>:{" "}
                <Link href="/consciousness/sleep-dreams" className="text-primary hover:underline">
                  Natural altered states during sleep
                </Link>{" "}
                including REM dreaming, lucid dreams, hypnagogic transitions, and deep sleep consciousness.
                Sleep offers nightly access to profound altered states for insight, creativity, and healing.
              </span>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-lg text-foreground">
                <strong>Rituals and Chanting</strong>: Repetitive movements, sounds, or words (drumming, chanting,
                singing bowls, ecstatic dance) can induce trance states and
                feelings of unity.
              </span>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-lg text-foreground">
                <strong>Physical Extremes</strong>: Using physical stress or exertion (intense exercise, sweat
                lodges, cold/heat exposure) to produce euphoria, clarity, or
                spiritual connection.
              </span>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-lg text-foreground">
                <strong>Hypnosis and Visualization</strong>: Guided suggestion, hypnosis, or deep visualization can induce
                trance-like states where memory, sensation, and perception are
                altered.
              </span>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-lg text-foreground">
                <strong>Art, Music, and Creative Flow</strong>: Deep immersion in creativity (painting, music, writing) often
                causes transformation of time-sense and heightened consciousness.
              </span>
            </div>
          </div>

          {/* Napoleon Hill's Insights */}
          <h2 className="text-3xl font-bold mb-6 text-foreground mt-8">
            Emotional and Motivational States (Napoleon Hill's Insights)
          </h2>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-lg text-foreground">
                <strong>
                  <Link
                    href="/consciousness/altered-states/hills-alternate-states/love-romantic-connection"
                    className="text-primary hover:underline"
                  >
                    Love, Romance, and Emotional Intensity
                  </Link>
                </strong>
                : Deep affection, passion, or heartfelt connection with another
                person can dramatically shift your state of mind. Hill believed
                that strong romantic love, when combined with a burning desire,
                can lift people to higher levels of inspiration, motivation, and
                even genius.
              </span>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-lg text-foreground">
                <strong>
                  <Link
                    href="/consciousness/altered-states/hills-alternate-states/sexual-transmutation"
                    className="text-primary hover:underline"
                  >
                    Sexual Transmutation
                  </Link>
                </strong>
                : Redirecting sexual energy into creative, intellectual, or
                spiritual pursuits. Hill argued that history's most successful
                people often harnessed their sexual energy for "higher" creative
                or entrepreneurial purposes.
              </span>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-lg text-foreground">
                <strong>
                  <Link
                    href="/consciousness/altered-states/hills-alternate-states/intense-desire-passion"
                    className="text-primary hover:underline"
                  >
                    Desire and Passion
                  </Link>
                </strong>
                : Intense longing or enthusiasm can shift your entire mental
                state. Hill lists desire (especially "white-hot desire") as the
                starting point of all achievement.
              </span>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-lg text-foreground">
                <strong>
                  <Link
                    href="/consciousness/altered-states/hills-alternate-states/imagination-via-emotion"
                    className="text-primary hover:underline"
                  >
                    Imagination Stimulated by Love, Sex, and Romance
                  </Link>
                </strong>
                : Heightened emotion from love or romance fires up creativity and
                intuition, opening new channels in the brain "not available under
                ordinary emotions."
              </span>
            </div>
          </div>

          {/* Summary Tables */}
          <h2 className="text-3xl font-bold mb-6 text-foreground mt-8">
            Summary Table: Methods to Alter Consciousness
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-border">
              <thead>
                <tr className="bg-card">
                  <th className="border border-border p-3 text-left text-foreground">Method</th>
                  <th className="border border-border p-3 text-left text-foreground">Example Techniques</th>
                  <th className="border border-border p-3 text-left text-foreground">Typical Effects</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-border p-3 text-foreground">Breathwork</td>
                  <td className="border border-border p-3 text-foreground">Holotropic, Pranayama, Wim Hof</td>
                  <td className="border border-border p-3 text-foreground">Euphoria, visions, deep relaxation</td>
                </tr>
                <tr>
                  <td className="border border-border p-3 text-foreground">Meditation/Mindfulness</td>
                  <td className="border border-border p-3 text-foreground">Zen, Transcendental, Mindfulness</td>
                  <td className="border border-border p-3 text-foreground">Calm, unity, altered time perception</td>
                </tr>
                <tr>
                  <td className="border border-border p-3 text-foreground">Sensory Deprivation</td>
                  <td className="border border-border p-3 text-foreground">Float tanks, dark retreat</td>
                  <td className="border border-border p-3 text-foreground">Visuals, introspection, deep insight</td>
                </tr>
                <tr>
                  <td className="border border-border p-3 text-foreground">Psychedelics/Entheogens</td>
                  <td className="border border-border p-3 text-foreground">Psilocybin, LSD, Ayahuasca</td>
                  <td className="border border-border p-3 text-foreground">Visions, ego dissolution, bliss</td>
                </tr>
                <tr>
                  <td className="border border-border p-3 text-foreground">Fasting/Sleep Deprivation</td>
                  <td className="border border-border p-3 text-foreground">Food/sleep abstinence</td>
                  <td className="border border-border p-3 text-foreground">Visions, disorientation, spirituality</td>
                </tr>
                <tr>
                  <td className="border border-border p-3 text-foreground">Rituals/Chanting</td>
                  <td className="border border-border p-3 text-foreground">Drumming, mantras, dance</td>
                  <td className="border border-border p-3 text-foreground">Trance, unity, ecstasy</td>
                </tr>
                <tr>
                  <td className="border border-border p-3 text-foreground">Physical Extremes</td>
                  <td className="border border-border p-3 text-foreground">Endurance running, sweat lodge</td>
                  <td className="border border-border p-3 text-foreground">Euphoria, altered perception</td>
                </tr>
                <tr>
                  <td className="border border-border p-3 text-foreground">Hypnosis/Visualization</td>
                  <td className="border border-border p-3 text-foreground">Guided hypnosis, imagery</td>
                  <td className="border border-border p-3 text-foreground">Trance, altered memory/sensation</td>
                </tr>
                <tr>
                  <td className="border border-border p-3 text-foreground">Creative Flow</td>
                  <td className="border border-border p-3 text-foreground">Music, art, writing</td>
                  <td className="border border-border p-3 text-foreground">Timelessness, insight, absorption</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h2 className="text-3xl font-bold mb-6 text-foreground mt-8">
            Summary Table: Hill's Consciousness-Altering States
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-border">
              <thead>
                <tr className="bg-card">
                  <th className="border border-border p-3 text-left text-foreground">Method</th>
                  <th className="border border-border p-3 text-left text-foreground">Mechanism</th>
                  <th className="border border-border p-3 text-left text-foreground">Typical Effects</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-border p-3 text-foreground">
                    <Link
                      href="/consciousness/altered-states/hills-alternate-states/love-romantic-connection"
                      className="text-primary hover:underline"
                    >
                      Love/Romantic Connection
                    </Link>
                  </td>
                  <td className="border border-border p-3 text-foreground">Emotional and inspirational energy</td>
                  <td className="border border-border p-3 text-foreground">Enhanced creativity, joy, resilience, purpose</td>
                </tr>
                <tr>
                  <td className="border border-border p-3 text-foreground">
                    <Link
                      href="/consciousness/altered-states/hills-alternate-states/sexual-transmutation"
                      className="text-primary hover:underline"
                    >
                      Sexual Transmutation
                    </Link>
                  </td>
                  <td className="border border-border p-3 text-foreground">Channeling sexual energy</td>
                  <td className="border border-border p-3 text-foreground">Focus, ambition, charisma, increased life force</td>
                </tr>
                <tr>
                  <td className="border border-border p-3 text-foreground">
                    <Link
                      href="/consciousness/altered-states/hills-alternate-states/intense-desire-passion"
                      className="text-primary hover:underline"
                    >
                      Intense Desire/Passion
                    </Link>
                  </td>
                  <td className="border border-border p-3 text-foreground">Emotional arousal toward any goal</td>
                  <td className="border border-border p-3 text-foreground">Motivation, vision, confidence, resourcefulness</td>
                </tr>
                <tr>
                  <td className="border border-border p-3 text-foreground">
                    <Link
                      href="/consciousness/altered-states/hills-alternate-states/imagination-via-emotion"
                      className="text-primary hover:underline"
                    >
                      Imagination via Emotion
                    </Link>
                  </td>
                  <td className="border border-border p-3 text-foreground">Emotionally inspired creativity</td>
                  <td className="border border-border p-3 text-foreground">Innovative ideas, artistic output, intuitive insights</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* New Section: Explore Questions by Category */}
        <section className="mb-12">
          <div className="mb-6">
            <h2 className="text-3xl font-bold text-foreground mb-2">
              Explore {totalQuestions} Research-Based Questions
            </h2>
            <p className="text-lg text-muted-foreground">
              Dive deeper with our comprehensive Q&A guide covering definitions, entry pathways, scientific understanding, safety, and practical integration.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {categories.map((category) => (
              <Link
                key={category.slug}
                href={`/consciousness/altered-states/${category.slug}`}
                className="group rounded-xl border border-border bg-card/30 p-6 transition-all hover:bg-card/50 hover:border-primary/50"
              >
                <div className="flex items-start gap-4">
                  <div className="rounded-lg bg-primary/10 p-2.5">
                    <Layers className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="flex items-baseline justify-between gap-2">
                      <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                        {category.name}
                      </h3>
                      <span className="text-sm text-muted-foreground">
                        {category.count} questions
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {category.description}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* About Section */}
        <section className="rounded-2xl border border-border bg-card/40 p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">
            About This Guide
          </h2>
          <div className="space-y-3 text-muted-foreground leading-relaxed">
            <p>
              This guide provides both educational overviews and research-based answers to common questions about altered states of consciousness. Each answer follows an Answer Engine Optimization (AEO) structure with concise explanations, scientific context, and boundary clarifications.
            </p>
            <p>
              Altered states encompass a wide spectrum of consciousness shifts—from everyday experiences like flow states and intense emotions to deliberate practices like meditation and hypnosis, to naturally occurring states like dreams and near-death experiences.
            </p>
            <p>
              Understanding altered states helps us appreciate the flexibility of consciousness, navigate these experiences safely, and integrate insights into daily life.
            </p>
          </div>
        </section>

        {/* Depth Essay */}
        <section className="mt-12 rounded-2xl border border-border bg-card/40 p-6">
          <h2 className="text-xl font-semibold text-foreground mb-2">
            Depth Essay
          </h2>
          <p className="text-muted-foreground mb-4">
            A synthesis layer built on this map: how to prepare, stay oriented,
            and integrate altered states so they become usable change.
          </p>
          <Link
            href="/consciousness/altered-states/integration-compass"
            className="text-primary hover:underline"
          >
            Integration Compass: Turning Altered States into Lasting Change
          </Link>
        </section>
      </main>
    </div>
  );
}
