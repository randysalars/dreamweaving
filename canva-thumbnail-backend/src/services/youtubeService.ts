import axios from 'axios';
import fs from 'fs';
import FormData from 'form-data';
import { config } from '../config/env';
import { logger } from '../utils/logger';

interface YoutubeTokenResponse {
  access_token: string;
  expires_in: number;
}

let cachedToken: { token: string; expiresAt: number } | null = null;

async function refreshYoutubeAccessToken(): Promise<string> {
  if (!config.youtube) {
    throw new Error('YouTube configuration not provided');
  }

  const params = new URLSearchParams({
    grant_type: 'refresh_token',
    refresh_token: config.youtube.refreshToken,
    client_id: config.youtube.clientId,
    client_secret: config.youtube.clientSecret,
  });

  const { data } = await axios.post<YoutubeTokenResponse>('https://oauth2.googleapis.com/token', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    timeout: 15000,
  });

  const expiresAt = Date.now() + (data.expires_in * 1000 - 60_000);
  cachedToken = { token: data.access_token, expiresAt };
  logger.info('Refreshed YouTube access token');
  return data.access_token;
}

async function getYoutubeAccessToken(): Promise<string> {
  if (cachedToken && cachedToken.expiresAt > Date.now()) {
    return cachedToken.token;
  }
  return refreshYoutubeAccessToken();
}

export async function setVideoThumbnail(videoId: string, imagePath: string): Promise<void> {
  if (!config.youtube) {
    throw new Error('YouTube configuration missing; cannot set thumbnail');
  }

  const accessToken = await getYoutubeAccessToken();
  const form = new FormData();
  form.append('media', fs.createReadStream(imagePath));

  const url = `${config.youtube.apiBaseUrl}/thumbnails/set?videoId=${encodeURIComponent(videoId)}`;

  await axios.post(url, form, {
    headers: {
      ...form.getHeaders(),
      Authorization: `Bearer ${accessToken}`,
    },
    maxBodyLength: Infinity,
    timeout: 20000,
  });

  logger.info({ videoId, imagePath }, 'Uploaded thumbnail to YouTube');
}
