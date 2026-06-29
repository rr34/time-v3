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

export async function getPhotosByGroup({ groupId, groupSlug, groupType = "clock" }) {
  const useSlug = typeof groupSlug === "string" && groupSlug.trim().length > 0;
  const useId = Number.isFinite(groupId);
  const normalizedGroupType = typeof groupType === "string" && groupType.trim()
    ? groupType.trim()
    : "clock";

  if (!useSlug && !useId) {
    return [];
  }

  const whereClause = useSlug ? "g.GroupSlug = ?" : "g.group_id = ?";
  const param = useSlug ? groupSlug.trim() : groupId;

  const query = `
    SELECT p.Basename, p.awimTag
    FROM photos_awim p
    JOIN photos_groups_join pg ON pg.PhotoID = p.photo_id
    JOIN photos_groups g ON g.group_id = pg.GroupID
    WHERE ${whereClause}
      AND g.GroupType = ?
    ORDER BY p.photo_id
    LIMIT 100
  `;

  const [rows] = await pool.query(query, [param, normalizedGroupType]);
  return rows;
}
