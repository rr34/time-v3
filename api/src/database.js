import mysql from 'mysql2/promise';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '.env') });

const pool = mysql.createPool({
  host: process.env.MYSQL_HOST,
  user: process.env.MYSQL_USER,
  password: process.env.MYSQL_PASSWORD,
  database: process.env.MYSQL_DATABASE,
  timezone: 'Z',
});

// Query photos by tags, supporting include and exclude filters
export async function getPhotosByTags({ TagsInclude = [], TagsExclude = [] }) {
  let whereClauses = [];

  // Sanitize tags to avoid SQL injection (basic escaping)
  const escapeTag = (tag) => tag.replace(/"/g, '\\"');

  for (const tag of TagsInclude) {
    whereClauses.push(`JSON_CONTAINS(Tags, '["${escapeTag(tag)}"]')`);
  }

  for (const tag of TagsExclude) {
    whereClauses.push(`NOT JSON_CONTAINS(Tags, '["${escapeTag(tag)}"]')`);
  }

  const whereSQL = whereClauses.length ? `WHERE ${whereClauses.join(' AND ')}` : '';

  const query = `
    SELECT * FROM photos_awim
    ${whereSQL}
    ORDER BY MomentCapture DESC
    LIMIT 100
  `;

  const [rows] = await pool.query(query);
  return rows;
}
