import { Router } from 'express';
import { generateThumbnailsForVideo } from '../services/thumbnailService';
import { logger } from '../utils/logger';
import { ThumbnailInput } from '../rag/thumbnailSpec';

export const thumbnailsRouter = Router();

function coerceStringArray(value: unknown): string[] | undefined {
  if (!value) {
    return undefined;
  }
  if (Array.isArray(value)) {
    return value.map((v) => String(v));
  }
  if (typeof value === 'string') {
    return [value];
  }
  return undefined;
}

thumbnailsRouter.post('/thumbnails/generate', async (req, res) => {
  const { videoId, title, topic, styleHints, archetypes, uploadToYouTube } = req.body || {};

  if (!videoId || !title) {
    return res.status(400).json({ error: 'videoId and title are required' });
  }

  const input: ThumbnailInput = {
    videoId: String(videoId),
    title: String(title),
    topic: topic ? String(topic) : undefined,
    styleHints: coerceStringArray(styleHints),
    archetypes: coerceStringArray(archetypes),
    uploadToYouTube: Boolean(uploadToYouTube),
  };

  try {
    const thumbnails = await generateThumbnailsForVideo(input);
    return res.json({ videoId: input.videoId, thumbnails });
  } catch (error) {
    logger.error({ error }, 'Failed to generate thumbnails');
    return res.status(500).json({ error: 'Failed to generate thumbnails' });
  }
});
