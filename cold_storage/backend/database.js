import sqlite3 from 'sqlite3';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DB_PATH = path.join(__dirname, 'cold_storage.db');

export const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error('Error opening SQLite database:', err.message);
  } else {
    console.log('Connected to SQLite cold_storage database.');
  }
});

export function initDatabase() {
  return new Promise((resolve, reject) => {
    db.serialize(() => {
      // Create or ensure table schema
      db.run(`
        CREATE TABLE IF NOT EXISTS cold_storages (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          address TEXT NOT NULL,
          village_or_area TEXT,
          district TEXT NOT NULL,
          state TEXT NOT NULL,
          pincode TEXT,
          latitude REAL NOT NULL,
          longitude REAL NOT NULL,
          phone_number TEXT,
          alternate_phone_number TEXT,
          contact_person TEXT,
          email TEXT,
          rating REAL,
          opening_hours TEXT,
          storage_capacity TEXT,
          suitable_crops TEXT,
          cold_storage_type TEXT,
          temperature_range TEXT,
          description TEXT,
          amenities TEXT,
          certifications TEXT,
          is_sample_data INTEGER DEFAULT 0,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `, (err) => {
        if (err) return reject(err);

        // Check if description column exists, if not recreate
        db.all('PRAGMA table_info(cold_storages)', (err, cols) => {
          if (err) return reject(err);
          const hasDesc = cols.some((c) => c.name === 'description');

          if (!hasDesc) {
            db.run('DROP TABLE cold_storages', (err) => {
              if (err) return reject(err);
              return initDatabase().then(resolve).catch(reject);
            });
            return;
          }

          // Clear and re-populate with fresh real data
          db.run('DELETE FROM cold_storages', (err) => {
            if (err) return reject(err);

            console.log('Seeding real agricultural cold storage facility data...');
            const dataPath = path.join(__dirname, 'data', 'sample_storages.json');
            const records = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

            const stmt = db.prepare(`
              INSERT INTO cold_storages (
                id, name, address, village_or_area, district, state, pincode,
                latitude, longitude, phone_number, alternate_phone_number,
                contact_person, email, rating, opening_hours, storage_capacity,
                suitable_crops, cold_storage_type, temperature_range,
                description, amenities, certifications, is_sample_data
              ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `);

            records.forEach((item) => {
              stmt.run([
                item.id,
                item.name,
                item.address,
                item.village_or_area || null,
                item.district,
                item.state,
                item.pincode || null,
                item.latitude,
                item.longitude,
                item.phone_number || null,
                item.alternate_phone_number || null,
                item.contact_person || null,
                item.email || null,
                item.rating || 4.5,
                item.opening_hours || '06:00 AM - 09:00 PM',
                item.storage_capacity || null,
                item.suitable_crops || null,
                item.cold_storage_type || null,
                item.temperature_range || null,
                item.description || null,
                item.amenities || null,
                item.certifications || null,
                item.is_sample_data ?? 0
              ]);
            });

            stmt.finalize((err) => {
              if (err) return reject(err);
              console.log(`Successfully populated ${records.length} real cold storage records.`);
              resolve();
            });
          });
        });
      });
    });
  });
}
