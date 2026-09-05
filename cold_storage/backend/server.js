import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import { initDatabase } from './database.js';
import routes from './routes.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

process.on('uncaughtException', (err) => {
  console.warn('⚠️ Global uncaughtException (handled):', err.message);
});

process.on('unhandledRejection', (reason) => {
  console.warn('⚠️ Global unhandledRejection (handled):', reason?.message || reason);
});

app.use(cors());
app.use(express.json());


// API Routes
app.use(routes);

// Serve Frontend Static Files
const frontendPath = path.join(__dirname, '..', 'frontend');
app.use(express.static(frontendPath));

// Fallback for SPA
app.get('*', (req, res, next) => {
  if (req.path.startsWith('/api') || req.path.startsWith('/cold-storages')) {
    return next();
  }
  res.sendFile(path.join(frontendPath, 'index.html'));
});

// Initialize database then start server
initDatabase()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`====================================================`);
      console.log(`🌾 FarmFusion Cold Storage Finder is running!`);
      console.log(`🔗 Local URL: http://localhost:${PORT}`);
      console.log(`====================================================`);
    });
  })
  .catch((err) => {
    console.error('Failed to initialize database:', err);
    process.exit(1);
  });
