import { config } from '../config/env';
import { logger } from '../utils/logger';
import { createChatCompletion } from '../utils/llmClient';

export interface ThumbnailSpec {
  videoId: string;
  titleText: string;
  subtitleText?: string;
  mood?: string;
  colors?: string[];
  backgroundDescription?: string;
  faceStyle?: string;
  logoPlacement?: 'top_left' | 'top_right' | 'bottom_left' | 'bottom_right';
  variants?: number;
  templateId?: string;
}

export interface ThumbnailInput {
  videoId: string;
  title: string;
  topic?: string;
  styleHints?: string[];
  archetypes?: string[];
  uploadToYouTube?: boolean;
}

function coerceVariants(value?: number): number {
  if (!value || Number.isNaN(value)) {
    return 1;
  }
  const safeValue = Math.max(1, Math.min(3, Math.round(value)));
  return safeValue;
}

export function normalizeThumbnailSpec(spec: Partial<ThumbnailSpec>): ThumbnailSpec {
  if (!spec.videoId) {
    throw new Error('ThumbnailSpec.videoId is required');
  }
  if (!spec.titleText) {
    throw new Error('ThumbnailSpec.titleText is required');
  }

  const variants = coerceVariants(spec.variants);
  const templateId = spec.templateId || config.canva.thumbnailTemplateId;

  return {
    videoId: spec.videoId,
    titleText: spec.titleText,
    subtitleText: spec.subtitleText,
    mood: spec.mood || 'bold-high-contrast',
    colors: spec.colors && spec.colors.length > 0 ? spec.colors : ['#0f172a', '#22d3ee', '#f97316'],
    backgroundDescription: spec.backgroundDescription || 'High-contrast abstract gradient background with clean separation',
    faceStyle: spec.faceStyle || 'cutout-with-soft-shadow',
    logoPlacement: spec.logoPlacement || 'top_right',
    variants,
    templateId,
  };
}

function stripCodeFences(payload: string): string {
  const trimmed = payload.trim();
  if (trimmed.startsWith('```')) {
    return trimmed.replace(/```json|```/g, '').trim();
  }
  return trimmed;
}

export async function generateThumbnailSpec(input: ThumbnailInput): Promise<ThumbnailSpec> {
  const systemPrompt = [
    'You are Dreamweaver, an expert YouTube thumbnail art director.',
    'Return concise JSON only, matching the ThumbnailSpec TypeScript type.',
    'Rules:',
    '- Prioritize high contrast, minimal words, and a single focal point.',
    '- Keep titleText short (<8 words) and punchy.',
    '- Use bold colors and clear hierarchy; avoid small text.',
    '- Choose colors that pop against YouTube light/dark themes.',
    '- subtitleText is optional; omit if unnecessary.',
  ].join('\n');

  const userPrompt = [
    `videoId: ${input.videoId}`,
    `title: ${input.title}`,
    `topic: ${input.topic || 'n/a'}`,
    `styleHints: ${(input.styleHints || []).join(', ') || 'n/a'}`,
    `archetypes: ${(input.archetypes || []).join(', ') || 'n/a'}`,
    'Respond with JSON only.',
  ].join('\n');

  const raw = await createChatCompletion(
    [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt },
    ],
    { responseFormat: 'json_object' },
  );

  const cleaned = stripCodeFences(raw);

  try {
    const parsed = JSON.parse(cleaned) as Partial<ThumbnailSpec>;
    const hydrated: Partial<ThumbnailSpec> = {
      ...parsed,
      videoId: input.videoId,
      titleText: parsed.titleText || input.title,
      variants: parsed.variants || undefined,
      templateId: parsed.templateId || config.canva.thumbnailTemplateId,
    };

    return normalizeThumbnailSpec(hydrated);
  } catch (error) {
    logger.error({ cleaned }, 'Failed to parse ThumbnailSpec from LLM');
    throw error;
  }
}
