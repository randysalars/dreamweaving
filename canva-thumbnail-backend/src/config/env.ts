import dotenv from 'dotenv';

dotenv.config();

interface CanvaConfig {
  clientId: string;
  clientSecret: string;
  refreshToken: string;
  redirectUri: string;
  apiBaseUrl: string;
  brandKitId?: string;
  thumbnailTemplateId?: string;
}

interface LlmConfig {
  apiKey: string;
  baseUrl: string;
  model?: string;
}

interface YoutubeConfig {
  clientId: string;
  clientSecret: string;
  refreshToken: string;
  apiBaseUrl: string;
}

export interface AppConfig {
  port: number;
  canva: CanvaConfig;
  llm: LlmConfig;
  youtube?: YoutubeConfig;
}

function requireEnv(key: string): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
  return value;
}

function optionalEnv(key: string): string | undefined {
  return process.env[key];
}

const port = Number(process.env.PORT ?? 4000);

export const config: AppConfig = {
  port: Number.isFinite(port) ? port : 4000,
  canva: {
    clientId: requireEnv('CANVA_CLIENT_ID'),
    clientSecret: requireEnv('CANVA_CLIENT_SECRET'),
    refreshToken: requireEnv('CANVA_REFRESH_TOKEN'),
    redirectUri: requireEnv('CANVA_REDIRECT_URI'),
    apiBaseUrl: process.env.CANVA_API_BASE_URL || 'https://api.canva.com',
    brandKitId: optionalEnv('CANVA_BRAND_KIT_ID'),
    thumbnailTemplateId: optionalEnv('CANVA_THUMBNAIL_TEMPLATE_ID'),
  },
  llm: {
    apiKey: requireEnv('LLM_API_KEY'),
    baseUrl: requireEnv('LLM_API_BASE_URL'),
    model: optionalEnv('LLM_MODEL'),
  },
  youtube:
    optionalEnv('YT_CLIENT_ID') &&
    optionalEnv('YT_CLIENT_SECRET') &&
    optionalEnv('YT_REFRESH_TOKEN')
      ? {
          clientId: requireEnv('YT_CLIENT_ID'),
          clientSecret: requireEnv('YT_CLIENT_SECRET'),
          refreshToken: requireEnv('YT_REFRESH_TOKEN'),
          apiBaseUrl: process.env.YT_API_BASE_URL || 'https://www.googleapis.com/youtube/v3',
        }
      : undefined,
};

export function ensureConfig(): AppConfig {
  return config;
}
