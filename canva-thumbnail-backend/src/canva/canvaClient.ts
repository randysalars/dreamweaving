import axios, { AxiosInstance } from 'axios';
import { config } from '../config/env';
import { createCanvaHttpClient } from '../utils/httpClient';
import { logger } from '../utils/logger';

interface CanvaTokenResponse {
  access_token: string;
  expires_in: number;
}

let cachedToken: { token: string; expiresAt: number } | null = null;

async function refreshAccessToken(): Promise<string> {
  const tokenUrl = `${config.canva.apiBaseUrl}/rest/v1/oauth/token`;

  const params = new URLSearchParams({
    grant_type: 'refresh_token',
    refresh_token: config.canva.refreshToken,
    client_id: config.canva.clientId,
    client_secret: config.canva.clientSecret,
    redirect_uri: config.canva.redirectUri,
  });

  const { data } = await axios.post<CanvaTokenResponse>(tokenUrl, params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    timeout: 15000,
  });

  const expiresAt = Date.now() + (data.expires_in * 1000 - 60_000);
  cachedToken = { token: data.access_token, expiresAt };
  logger.info('Refreshed Canva access token');
  return data.access_token;
}

export async function getCanvaAccessToken(): Promise<string> {
  if (cachedToken && cachedToken.expiresAt > Date.now()) {
    return cachedToken.token;
  }
  return refreshAccessToken();
}

export async function authorizedCanvaClient(): Promise<AxiosInstance> {
  const token = await getCanvaAccessToken();
  const baseURL = `${config.canva.apiBaseUrl}/rest/v1`;
  return createCanvaHttpClient(baseURL, token);
}
