require("dotenv").config();
const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcodeTerminal = require("qrcode-terminal");
const QRCode = require("qrcode");
const express = require("express");
const { default: PQueue } = require("p-queue");

const app = express();
const PORT = process.env.WA_PORT || 3001;
app.use(express.json());

// Auth Middleware
function auth(req, res, next) {
    const key = req.headers["x-service-key"] || req.headers["x-api-key"];
    if (!key || key !== SERVICE_KEY) {
        return res.status(403).json({ error: "Forbidden: Invalid service key" });
    }
    next();
}

// ── State ────────────────────────────────────────────────────────
let isReady = false;
let qrGenerated = false;
let latestQrBase64 = null;
const activeSends = new Set();  // Track in-flight message IDs
const queue = new PQueue({ concurrency: 1 });
const SERVICE_KEY = process.env.INTERNAL_API_KEY;

// ── WhatsApp Client ──────────────────────────────────────────────
const client = new Client({
    authStrategy: new LocalAuth({ dataPath: ".wwebjs_auth" }),
    puppeteer: {
        headless: "new", // Set to "new" for headless environment
        args: [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--remote-debugging-port=9222",
        ],
        // If the bundled chromium fails, try to use system chrome:
        // executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    },
});

client.on("qr", async (qr) => {
    qrGenerated = true;
    console.log("\n📱 Scan this QR code with WhatsApp Business:\n");
    qrcodeTerminal.generate(qr, { small: true });
    
    try {
        // Generate base64 for the frontend
        latestQrBase64 = await QRCode.toDataURL(qr);
        // data:image/png;base64,... -> strip prefix if backend expects raw base64
        latestQrBase64 = latestQrBase64.replace(/^data:image\/png;base64,/, "");
    } catch (err) {
        console.error("Failed to generate QR base64:", err);
    }
    
    console.log("\n⏳ Waiting for scan...\n");
});

client.on("authenticated", () => {
    console.log("🔐 Authenticated — session saved");
});

client.on("ready", () => {
    isReady = true;
    console.log("✅ WhatsApp client ready\n");
});

client.on("disconnected", (reason) => {
    isReady = false;
    console.error(`❌ Disconnected: ${reason}`);
    // Auto-reconnect after 10s
    setTimeout(() => {
        console.log("🔄 Reconnecting...");
        client.initialize().catch(console.error);
    }, 10000);
});

// ── Helpers ──────────────────────────────────────────────────────
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const randomDelay = (minMs, maxMs) =>
    sleep(Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs);

function validatePhone(phone) {
    const cleaned = phone.replace(/\s/g, "");
    return /^\+\d{10,15}$/.test(cleaned);
}

// ── Routes ───────────────────────────────────────────────────────

// Health check
app.get("/health", (req, res) => {
    res.json({
        ready: isReady,
        qr_generated: qrGenerated,
        timestamp: Date.now(),
    });
});

// QR Code endpoint
app.get("/qr", (req, res) => {
    if (isReady) {
        return res.json({ qr_base64: null, message: "Client is already ready" });
    }
    if (!latestQrBase64) {
        return res.status(404).json({ qr_base64: null, error: "QR not yet generated" });
    }
    res.json({ qr_base64: latestQrBase64 });
});

// Send single message
app.post("/send", auth, async (req, res) => {
    const { phone, message } = req.body;

    if (!isReady) {
        return res.status(503).json({ status: "error", error: "WhatsApp not ready — scan QR first" });
    }
    if (!phone || !message) {
        return res.status(400).json({ status: "error", error: "phone and message are required" });
    }
    if (!validatePhone(phone)) {
        return res.status(400).json({ status: "error", error: `Invalid phone format: ${phone}` });
    }

    const chatId = phone.replace("+", "") + "@c.us";

    // Add to PQueue
    try {
        const result = await queue.add(async () => {
            // Check if number is on WhatsApp
            const isRegistered = await client.isRegisteredUser(chatId);
            if (!isRegistered) {
                return { status: "not_on_whatsapp", phone };
            }

            // Simulate human delay
            await randomDelay(2000, 4000);

            const msg = await client.sendMessage(chatId, message);
            return {
                status: "sent",
                messageId: msg.id.id,
                phone,
            };
        });
        return res.json(result);
    } catch (err) {
        console.error(`❌ Send failed to ${phone}: ${err.message}`);
        return res.json({ status: "error", error: err.message, phone });
    }
});

// Bulk send (sequential, with rate-limit delays)
app.post("/bulk", auth, async (req, res) => {
    const { messages } = req.body;

    if (!isReady) {
        return res.status(503).json({ error: "WhatsApp not ready" });
    }
    if (!Array.isArray(messages) || messages.length === 0) {
        return res.status(400).json({ error: "messages must be a non-empty array" });
    }
    if (messages.length > 50) {
        return res.status(400).json({ error: "Max 50 messages per bulk request" });
    }

    // Respond immediately — process in background
    res.json({ status: "processing", total: messages.length });

    const results = [];
    for (let i = 0; i < messages.length; i++) {
        const { phone, message } = messages[i];
        try {
            if (!validatePhone(phone)) {
                results.push({ phone, status: "invalid_phone" });
                continue;
            }
            const chatId = phone.replace("+", "") + "@c.us";
            const isRegistered = await client.isRegisteredUser(chatId);
            if (!isRegistered) {
                results.push({ phone, status: "not_on_whatsapp" });
            } else {
                await randomDelay(2000, 4000);
                const msg = await client.sendMessage(chatId, message);
                results.push({ phone, status: "sent", messageId: msg.id.id });
                console.log(`✅ [${i + 1}/${messages.length}] Sent to ${phone}`);
            }
        } catch (err) {
            results.push({ phone, status: "error", error: err.message });
        }
        // 25–50s human-like delay between messages
        if (i < messages.length - 1) {
            const delaySec = Math.floor(Math.random() * 25) + 25;
            console.log(`  ⏳ Waiting ${delaySec}s before next message...`);
            await sleep(delaySec * 1000);
        }
    }
    console.log(`\n📊 Bulk done: ${results.filter(r => r.status === "sent").length}/${messages.length} sent`);
});

// ── Start ────────────────────────────────────────────────────────
client.initialize().catch((err) => {
    console.error("Failed to initialize WhatsApp client:", err);
    process.exit(1);
});

app.listen(PORT, () => {
    console.log(`🚀 WA server running on http://localhost:${PORT}`);
    console.log(`   GET  /health`);
    console.log(`   POST /send   { phone, message }`);
    console.log(`   POST /bulk   { messages: [{phone, message}] }\n`);
});
