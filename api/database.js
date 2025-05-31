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

  // Basic sanitization (escaping quotes and %/_) to avoid SQL injection
  const escapeLike = (tag) =>
    tag.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/%/g, '\\%').replace(/_/g, '\\_');

  for (const tag of TagsInclude) {
    const escaped = escapeLike(tag);
    whereClauses.push(`Tags LIKE '%"${escaped}"%'`);
  }

  for (const tag of TagsExclude) {
    const escaped = escapeLike(tag);
    whereClauses.push(`Tags NOT LIKE '%"${escaped}"%'`);
  }

  const whereSQL = whereClauses.length ? `WHERE ${whereClauses.join(' AND ')}` : '';

  const query = `
    SELECT Basename, awimTag FROM photos_awim
    ${whereSQL}
    LIMIT 100
  `;

  const [rows] = await pool.query(query);
  return rows;
}
