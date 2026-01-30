import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
import { getPhotosByTags } from "./database.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '.env') });

const allowedOrigins = (process.env.CLIENT_ORIGINS || "")
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);

if (allowedOrigins.length === 0) {
  console.error("CLIENT_ORIGINS environment variable not set or empty!");
  process.exit(1);
}

const app = express();
const HOST = process.env.HOST || "127.0.0.1";
const PORT = parseInt(process.env.PORT || "5000", 10);
const AWIM_BASE_URL = process.env.AWIM_BASE_URL || "https://awim.timev3tech.com";

// Middleware to parse JSON bodies
app.use(express.json({ limit: "20mb" }));

// Enable CORS for frontend origin
console.log('Allowed origins: ', allowedOrigins)
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
      if (awimTag == null) {
        console.warn(`Skipping ${Basename}: awimTag is null/undefined`);
        continue;
      }

      let parsedAwimTag = awimTag;
      if (typeof awimTag === "string") {
        try {
          parsedAwimTag = JSON.parse(awimTag);
        } catch (err) {
          console.warn(`Skipping ${Basename}: invalid awimTag JSON`, err);
          continue;
        }
      }

      formatted[Basename] = { awimTag: parsedAwimTag };
    }

    res.json(formatted);

  } catch (err) {
    console.error("DB query error:", err);
    res.status(500).send('DB query failed');
  }
});

const allowedAwimEndpoints = new Set(["getevents", "celestialinphotos"]);
app.post("/awim/:endpoint", async (req, res) => {
  const { endpoint } = req.params;
  if (!allowedAwimEndpoints.has(endpoint)) {
    return res.status(404).json({ error: "Unknown awim endpoint" });
  }

  try {
    const upstreamRes = await fetch(`${AWIM_BASE_URL}/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body ?? {}),
    });

    const contentType = upstreamRes.headers.get("content-type") || "application/json";
    res.status(upstreamRes.status);
    res.setHeader("Content-Type", contentType);

    const bodyText = await upstreamRes.text();
    res.send(bodyText);
  } catch (err) {
    console.error(`AWIM proxy error for ${endpoint}:`, err);
    res.status(502).json({ error: "AWIM proxy failed" });
  }
});


// Start server
app.listen(PORT, HOST, () => {
  console.log(`🚀 Server is running on http://${HOST}:${PORT}`);
});
