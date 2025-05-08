const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const path = require("path");
const fs = require("fs");

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Enable CORS with specific origins
app.use(
  cors({
    origin: "http://127.0.0.1:5173", // Allow Vite React frontend default port
    methods: "GET,HEAD,PUT,PATCH,POST,DELETE",
    allowedHeaders: ["Content-Type", "Authorization"],
    credentials: true,
  })
);

// Serve static images with proper CORS headers
app.use(
  "/clockimages",
  (req, res, next) => {
    res.setHeader("Access-Control-Allow-Origin", "http://127.0.0.1:5173");
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
  const baseName = "timhouse20220410 - NL100550";
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
app.listen(PORT, () => {
  console.log(`🚀 Server is running on http://localhost:${PORT}`);
});
