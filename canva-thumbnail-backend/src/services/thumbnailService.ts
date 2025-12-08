import fs from 'fs/promises';
import path from 'path';
import sharp from 'sharp';
import { createDesignFromTemplate, applyThumbnailSpecToDesign } from '../canva/designs';
import {
  createDesignExportJob,
  downloadExportedImage,
  waitForExportJobCompletion,
} from '../canva/exports';
import { generateThumbnailSpec, ThumbnailInput } from '../rag/thumbnailSpec';
import { logger } from '../utils/logger';
import { setVideoThumbnail } from './youtubeService';

export interface GeneratedThumbnail {
  variant: number;
  filePath: string;
}

async function ensureOutputDir(): Promise<string> {
  const dir = path.resolve(process.cwd(), 'thumbnails');
  await fs.mkdir(dir, { recursive: true });
  return dir;
}

async function maybeCompressImage(filePath: string): Promise<void> {
  const stats = await fs.stat(filePath);
  if (stats.size <= 2_000_000) {
    return;
  }

  const tempPath = filePath.replace(/\.png$/i, '.jpg');
  await sharp(filePath).jpeg({ quality: 85 }).toFile(tempPath);
  await fs.rename(tempPath, filePath);
  logger.info({ filePath }, 'Compressed large thumbnail image');
}

export async function generateThumbnailsForVideo(input: ThumbnailInput): Promise<GeneratedThumbnail[]> {
  const spec = await generateThumbnailSpec(input);
  const results: GeneratedThumbnail[] = [];
  const outputDir = await ensureOutputDir();

  for (let variant = 1; variant <= (spec.variants || 1); variant += 1) {
    const design = await createDesignFromTemplate(spec);
    await applyThumbnailSpecToDesign(design.id, spec);
    const exportJob = await createDesignExportJob(design.id, 'png');
    const completedJob = await waitForExportJobCompletion(exportJob.id);

    if (!completedJob.downloadUrl) {
      throw new Error(`Export job ${completedJob.id} completed without downloadUrl`);
    }

    const filename = `${input.videoId}-v${variant}.png`;
    const filePath = path.join(outputDir, filename);

    await downloadExportedImage(completedJob.downloadUrl, filePath);
    await maybeCompressImage(filePath);

    results.push({ variant, filePath });
  }

  if (input.uploadToYouTube && results.length > 0) {
    try {
      await setVideoThumbnail(input.videoId, results[0].filePath);
    } catch (error) {
      logger.error({ error }, 'Failed to upload thumbnail to YouTube');
    }
  }

  return results;
}
