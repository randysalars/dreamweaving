import { config } from '../config/env';
import { ThumbnailSpec } from '../rag/thumbnailSpec';
import { logger } from '../utils/logger';
import { authorizedCanvaClient } from './canvaClient';

export interface CanvaDesign {
  id: string;
}

export async function createDesignFromTemplate(spec: ThumbnailSpec): Promise<CanvaDesign> {
  const templateId = spec.templateId || config.canva.thumbnailTemplateId;
  if (!templateId) {
    throw new Error('No templateId provided for thumbnail generation');
  }

  const client = await authorizedCanvaClient();

  const payload: Record<string, unknown> = {
    template_id: templateId,
  };

  if (config.canva.brandKitId) {
    payload.brand_kit_id = config.canva.brandKitId;
  }

  const { data } = await client.post('/designs', payload);

  const designId: string | undefined = data?.id || data?.design_id || data?.design?.id;
  if (!designId) {
    throw new Error('Unable to extract design id from Canva response');
  }

  logger.info({ designId }, 'Created Canva design from template');
  return { id: designId };
}

export async function applyThumbnailSpecToDesign(designId: string, spec: ThumbnailSpec): Promise<void> {
  const client = await authorizedCanvaClient();

  const variables: Array<{ name: string; value: string }> = [];
  if (spec.titleText) {
    variables.push({ name: 'TITLE', value: spec.titleText });
  }
  if (spec.subtitleText) {
    variables.push({ name: 'SUBTITLE', value: spec.subtitleText });
  }

  if (variables.length === 0) {
    logger.warn('No variables to apply to design');
    return;
  }

  // Canva Connect supports autofill variables; adjust variable names to match your template layer names.
  const payload = { variables };

  await client.post(`/designs/${designId}/autofill`, payload);
  logger.info({ designId, variables }, 'Applied thumbnail spec to design');
}
