import express from 'express';
import { config } from './config/env';
import { logger } from './utils/logger';
import { thumbnailsRouter } from './routes/thumbnails';

const app = express();

app.use(express.json());

app.get('/healthz', (_req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api', thumbnailsRouter);

app.use((error: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  logger.error({ error: error.message, stack: error.stack }, 'Unhandled error');
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(config.port, () => {
  logger.info(`Thumbnail backend listening on port ${config.port}`);
});
