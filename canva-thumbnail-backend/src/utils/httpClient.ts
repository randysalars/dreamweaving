import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { logger } from './logger';

export function createHttpClient(config: AxiosRequestConfig): AxiosInstance {
  const instance = axios.create({
    timeout: 15000,
    ...config,
  });

  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      const status = error.response?.status;
      const url = error.config?.url;
      logger.error(
        {
          status,
          url,
          data: error.response?.data,
        },
        'HTTP request failed',
      );
      return Promise.reject(error);
    },
  );

  return instance;
}

export function createCanvaHttpClient(baseURL: string, accessToken: string): AxiosInstance {
  return createHttpClient({
    baseURL,
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}
