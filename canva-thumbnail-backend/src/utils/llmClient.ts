import axios from 'axios';
import { config } from '../config/env';
import { logger } from './logger';

export type ChatRole = 'system' | 'user' | 'assistant';

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

export interface ChatCompletionOptions {
  model?: string;
  temperature?: number;
  responseFormat?: 'json_object' | 'text';
}

export async function createChatCompletion(
  messages: ChatMessage[],
  options?: ChatCompletionOptions,
): Promise<string> {
  const model = options?.model || config.llm.model || 'gpt-4o-mini';

  try {
    const { data } = await axios.post(
      `${config.llm.baseUrl}/v1/chat/completions`,
      {
        model,
        messages,
        temperature: options?.temperature ?? 0.2,
        ...(options?.responseFormat === 'json_object'
          ? { response_format: { type: 'json_object' } }
          : {}),
      },
      {
        headers: {
          Authorization: `Bearer ${config.llm.apiKey}`,
          'Content-Type': 'application/json',
        },
        timeout: 20000,
      },
    );

    const content: string | undefined = data?.choices?.[0]?.message?.content;
    if (!content) {
      throw new Error('LLM response missing content');
    }

    return content;
  } catch (error) {
    logger.error({ error }, 'LLM completion failed');
    throw error;
  }
}
