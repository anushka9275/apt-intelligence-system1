
require("dotenv").config();

const express = require("express");
const cors = require("cors");

const { MongoClient } = require("mongodb");

const MONGODB_URI = process.env.MONGODB_URI;
const DB_NAME = process.env.DB_NAME || "drdo_apt_db";

if (!MONGODB_URI) {
  throw new Error("MONGODB_URI is missing. Check backend/.env");
}

const mongoClient = new MongoClient(MONGODB_URI);
let db;


const app = express();
const PORT = process.env.PORT || 5000;
const ML_API_URL = process.env.ML_API_URL || "http://127.0.0.1:8000";
const FRONTEND_URL = process.env.FRONTEND_URL;

const allowedOrigins = [
  "http://localhost:5173",
  "http://127.0.0.1:5173",
  FRONTEND_URL
].filter(Boolean);

app.use(cors({
  origin: allowedOrigins
}));
app.use(express.json());

app.get("/", (req, res) => {
  res.json({
    message: "DRDO APT Intelligence Backend is running",
    status: "healthy"
  });
});

app.get("/api/health", async (req, res) => {
  try {
    const response = await fetch(`${ML_API_URL}/health`);
    if (!response.ok) {
      throw new Error("ML API health check failed");
    }

    const mlStatus = await response.json();

    res.json({
      backend: "healthy",
      ml_api: mlStatus
    });
  } catch (error) {
    res.status(503).json({
      backend: "healthy",
      ml_api: "unavailable",
      message: "Check that the Python FastAPI server is running."
    });
  }
});

app.get("/api/ioc-history", async (req, res) => {
  try {
    const records = await db
      .collection("ioc_history")
      .find({})
      .sort({ createdAt: -1 })
      .limit(100)
      .toArray();

    res.json({
      count: records.length,
      records
    });
  } catch (error) {
    console.error("Failed to fetch IOC history:", error.message);
    res.status(500).json({
      error: "Unable to retrieve IOC history."
    });
  }
});



app.post("/api/predict", async (req, res) => {
  const { domain } = req.body || {};

  if (typeof domain !== "string" || !domain.trim()) {
    return res.status(400).json({
      error: "Please provide a non-empty domain."
    });
  }

  const cleanDomain = domain.trim().toLowerCase();

  if (cleanDomain.length > 253) {
    return res.status(400).json({
      error: "Domain must not exceed 253 characters."
    });
  }

  try {
    const response = await fetch(`${ML_API_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ domain: cleanDomain })
    });

    const data = await response.json();

    if (!response.ok) {
      return res.status(response.status).json(data);
    }

    // Save the successful prediction to MongoDB.
    try {
      await db.collection("ioc_history").insertOne({
        domain: data.domain || cleanDomain,
        predicted_label: data.predicted_label,
        model_scores: data.model_scores || {},
        warning: data.warning || "",
        createdAt: new Date()
      });

      console.log(`Saved IOC prediction: ${cleanDomain}`);

      return res.json({
        ...data,
        history_saved: true
      });
    } catch (dbError) {
      console.error("Failed to save IOC history:", dbError.message);

      // Return the prediction even if saving fails.
      return res.json({
        ...data,
        history_saved: false,
        history_message: "Prediction succeeded, but history could not be saved."
      });
    }
  } catch (error) {
    return res.status(502).json({
      error: "Unable to reach the Python ML API."
    });
  }
});



async function startServer() {
  try {
    await mongoClient.connect();
    db = mongoClient.db(DB_NAME);

    console.log("MongoDB Atlas connected successfully");
    console.log(`Database: ${DB_NAME}`);

    app.listen(PORT, () => {
      console.log(`DRDO backend running at http://localhost:${PORT}`);
    });
  } catch (error) {
    console.error(
      "Failed to connect to MongoDB Atlas:",
      error.message
    );
    process.exit(1);
  }
}

startServer();
