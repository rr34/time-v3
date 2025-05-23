import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";

// Load environment variables
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '.env') });

const app = express();

const PORT = process.env.PORT || 5000;
const CLIENT_IP = process.env.CLIENT_IP;
console.log("CLIENT_IP env variable is: ", CLIENT_IP)

// Enable CORS with specific origins
app.use(
  cors({
    origin: CLIENT_IP, // Allow Vite React frontend default port
    methods: "GET,HEAD,PUT,PATCH,POST,DELETE",
    allowedHeaders: ["Content-Type", "Authorization"],
    credentials: true,
  })
);

// Serve static images with proper CORS headers
app.use(
  "/clockimages",
  (req, res, next) => {
    res.setHeader("Access-Control-Allow-Origin", CLIENT_IP);
    res.setHeader("Cross-Origin-Resource-Policy", "cross-origin");
    next();
  },
  express.static(path.join(__dirname, "public/clockimages"))
);

// Root route
app.get("/", (req, res) => {
  res.send("Hello from Express + JavaScript!");
});

// Endpoint to get clock image and metadata
app.get("/clockimage", (req, res) => {
  const baseName = "timhouse20220410 - NL100457";
  const imageFile = `${baseName}.PNG`;
  const jsonFile = `${baseName}.json`;

  const imagePath = path.join(__dirname, "public/clockimages", imageFile);
  const jsonPath = path.join(__dirname, "public/clockimages", jsonFile);

  if (!fs.existsSync(imagePath) || !fs.existsSync(jsonPath)) {
    return res.status(404).json({ error: "Clock image or metadata not found" });
  }

  const metadata = JSON.parse(fs.readFileSync(jsonPath, "utf-8"));
  const imageUrl = `/clockimages/${imageFile}`;

  res.json({ imageUrl, metadata });
});

// Start server
app.listen(PORT, "127.0.0.1", () => {
  console.log(`🚀 Server is running on http://localhost:${PORT}`);
});
