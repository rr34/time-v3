import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
import { getPhotosByTags } from "./database.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '.env') });

if (!process.env.CLIENT_ORIGIN1 || !process.env.CLIENT_ORIGIN2) {
  console.error("CLIENT_ORIGIN1 or CLIENT_ORIGIN2 environment variable not set!");
  process.exit(1);
}

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware to parse JSON bodies
app.use(express.json());

// Enable CORS for frontend origin
const allowedOrigins = [process.env.CLIENT_ORIGIN1, process.env.CLIENT_ORIGIN2];
app.use(
  cors({
    origin: (origin, callback) => {
      // Allow requests with no origin (like mobile apps or curl requests)
      if (!origin) return callback(null, true);
      if (allowedOrigins.includes(origin)) {
        return callback(null, true);
      }
      return callback(new Error("Not allowed by CORS"));
    },
    methods: "GET,HEAD,PUT,PATCH,POST,DELETE",
    allowedHeaders: ["Content-Type", "Authorization"],
    credentials: true,
  })
);


// Serve static images with CORS headers
app.use("/clockimages", (req, res, next) => {
    const origin = req.headers.origin;
    if (allowedOrigins.includes(origin)) {
      res.setHeader("Access-Control-Allow-Origin", origin);
    }
    res.setHeader("Cross-Origin-Resource-Policy", "cross-origin");
    next();
  },
  express.static(path.join(__dirname, "public/clockimages"))
);


// POST route to query photos by tags
app.post('/getimageslist/query', async (req, res) => {
  const { TagsInclude = [], TagsExclude = [] } = req.body;

  try {
    const photos = await getPhotosByTags({ TagsInclude, TagsExclude });

    // Transform array into object keyed by Basename
    const formatted = {};
    for (const { Basename, awimTag } of photos) {
      formatted[Basename] = { awimTag: JSON.parse(awimTag) };
    }

    res.json(formatted);

  } catch (err) {
    console.error("DB query error:", err);
    res.status(500).send('DB query failed');
  }
});


// Start server
app.listen(PORT, "0.0.0.0", () => {
  console.log(`🚀 Server is running on http://0.0.0.0:${PORT}`);
});