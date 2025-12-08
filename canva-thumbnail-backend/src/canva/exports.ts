import axios from 'axios';
import fs from 'fs/promises';
import { authorizedCanvaClient } from './canvaClient';
import { logger } from '../utils/logger';

export interface CanvaExportJob {
  id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  downloadUrl?: string;
}

export async function createDesignExportJob(designId: string, fileType: 'png' | 'jpg'): Promise<CanvaExportJob> {
  const client = await authorizedCanvaClient();
  const { data } = await client.post(`/designs/${designId}/exports`, {
    file_type: fileType,
  });

  const jobId: string | undefined = data?.id || data?.job_id || data?.export_job_id;
  const status: CanvaExportJob['status'] = data?.status || 'pending';

  if (!jobId) {
    throw new Error('Failed to create Canva export job');
  }

  logger.info({ designId, jobId }, 'Created Canva export job');
  return { id: jobId, status };
}

export async function getDesignExportJob(jobId: string): Promise<CanvaExportJob> {
  const client = await authorizedCanvaClient();
  const { data } = await client.get(`/exports/${jobId}`);

  const status: CanvaExportJob['status'] = data?.status || 'pending';
  const downloadUrl: string | undefined = data?.download_url || data?.result?.url;

  return { id: jobId, status, downloadUrl };
}

export async function waitForExportJobCompletion(
  jobId: string,
  timeoutMs = 60_000,
  pollIntervalMs = 2_000,
): Promise<CanvaExportJob> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const job = await getDesignExportJob(jobId);
    if (job.status === 'completed') {
      return job;
    }
    if (job.status === 'failed') {
      throw new Error(`Canva export job ${jobId} failed`);
    }
    await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
  }

  throw new Error(`Canva export job ${jobId} timed out after ${timeoutMs}ms`);
}

export async function downloadExportedImage(downloadUrl: string, destPath: string): Promise<void> {
  const response = await axios.get<ArrayBuffer>(downloadUrl, { responseType: 'arraybuffer', timeout: 20000 });
  await fs.writeFile(destPath, Buffer.from(response.data));
  logger.info({ destPath }, 'Downloaded exported thumbnail');
}
