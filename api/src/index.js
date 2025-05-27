import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
import { getPhotosByTags } from "./database.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '.env') });

if (!process.env.CLIENT_IP) {
  console.error("CLIENT_IP environment variable not set!");
  process.exit(1);
}

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware to parse JSON bodies
app.use(express.json());

// Enable CORS for frontend origin
app.use(
  cors({
    origin: process.env.CLIENT_IP,
    methods: "GET,HEAD,PUT,PATCH,POST,DELETE",
    allowedHeaders: ["Content-Type", "Authorization"],
    credentials: true,
  })
);

// Serve static images with CORS headers
app.use(
  "/clockimages",
  (req, res, next) => {
    res.setHeader("Access-Control-Allow-Origin", process.env.CLIENT_IP);
    res.setHeader("Cross-Origin-Resource-Policy", "cross-origin");
    next();
  },
  express.static(path.join(__dirname, "public/clockimages"))
);

// Root route
app.get("/", (req, res) => {
  res.send("Hello from Express + JavaScript!");
});

// POST route to query photos by tags
app.post('/clockimages/query', async (req, res) => {
  const { TagsInclude = [], TagsExclude = [] } = req.body;

  try {
    const photos = await getPhotosByTags({ TagsInclude, TagsExclude });
    res.json(photos);
  } catch (err) {
    console.error("DB query error:", err);
    res.status(500).send('DB query failed');
  }
});

// Start server
app.listen(PORT, "127.0.0.1", () => {
  console.log(`🚀 Server is running on http://localhost:${PORT}`);
});
