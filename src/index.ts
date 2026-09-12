// Main Cloudflare Worker entry point for AITextCoach
// All API routes — static files served by Pages

import {
  isProUser, addProUser, getTodayUsage, addUsage,
  trackClick, getStats, type Env,
} from "./db";
import { callDeepSeek, loadBudget, checkBudget } from "./deepseek";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
  "Content-Type": "application/json",
};

function jsonResponse(data: any, status = 200): Response {
  return new Response(JSON.stringify(data), { status, headers: CORS_HEADERS });
}

function getClientIp(request: Request): string {
  return request.headers.get("CF-Connecting-IP") || "unknown";
}

function getToday(): string {
  return new Date().toISOString().slice(0, 10);
}

// ============ ROUTE HANDLERS ============

async function handleConfig(env: Env): Promise<Response> {
  return jsonResponse({
    paypalClientId: "AdtYR0zkWzQfqViuiRqDPao6Dp1nwr-nXNNcBG3scWj0BFr3_zUTc-1IsGf95NqDb2gLaD8S20LLaFBl",
    paypalMode: env.PAYPAL_MODE,
    paypalPlanId: env.PAYPAL_PLAN_ID,
  });
}

async function handleStats(env: Env): Promise<Response> {
  const stats = await getStats(env.DB);
  const budget = checkBudget(await loadBudget(env.KV));
  return jsonResponse({
    ...stats,
    budget: {
      spent: Math.round(budget.spent * 100) / 100,
      limit: budget.limit,
      mode: budget.mode,
    },
  });
}

async function handleEnhance(request: Request, env: Env): Promise<Response> {
  let body: any;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: "Invalid JSON" }, 400);
  }

  const text = body.text || "";
  const style = body.style || "casual";
  const email = (body.email || "").toLowerCase().trim() || null;

  if (!text || text.length < 3) {
    return jsonResponse({ error: "Text too short (min 3 chars)" }, 400);
  }
  if (text.length > 5000) {
    return jsonResponse({ error: "Text too long (max 5000 chars)" }, 400);
  }

  const pro = await isProUser(env.DB, email);
  const todayUsage = await getTodayUsage(env.DB, email);

  // Quota: Free = 500 chars/day, Pro = unlimited
  const FREE_LIMIT = 500;
  if (!pro && todayUsage + text.length > FREE_LIMIT) {
    return jsonResponse({
      error: "Daily free limit reached",
      upgrade: true,
      used: todayUsage,
      limit: FREE_LIMIT,
    }, 429);
  }

  const budget = checkBudget(await loadBudget(env.KV));
  const dsResult = await callDeepSeek(text, style, env, budget.mode);

  if ("error" in dsResult) {
    return jsonResponse({ error: dsResult.error }, 503);
  }

  await addUsage(env.DB, email, text.length);

  return jsonResponse({
    result: dsResult.result,
    style,
    chars_used: todayUsage + text.length,
    pro,
  });
}

async function handleActivatePro(request: Request, env: Env): Promise<Response> {
  let body: any;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: "Invalid JSON" }, 400);
  }

  const subscriptionId = body.subscriptionId || "";
  const email = (body.email || "").toLowerCase().trim();

  if (!email || !subscriptionId) {
    return jsonResponse({ error: "Missing email or subscriptionId" }, 400);
  }

  // Verify subscription with PayPal (sandbox/live)
  const paypalUrl = env.PAYPAL_MODE === "sandbox"
    ? "https://api.sandbox.paypal.com"
    : "https://api.paypal.com";

  try {
    // Get access token
    const authResp = await fetch(`${paypalUrl}/v1/oauth2/token`, {
      method: "POST",
      headers: {
        "Authorization": `Basic ${btoa(`AdtYR0zkWzQfqViuiRqDPao6Dp1nwr-nXNNcBG3scWj0BFr3_zUTc-1IsGf95NqDb2gLaD8S20LLaFBl:${env.PAYPAL_CLIENT_SECRET}`)}`,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: "grant_type=client_credentials",
    });

    if (!authResp.ok) {
      return jsonResponse({ error: "PayPal authentication failed" }, 500);
    }

    const authData = await authResp.json() as any;
    const accessToken = authData.access_token;

    // Verify subscription
    const subResp = await fetch(`${paypalUrl}/v1/billing/subscriptions/${subscriptionId}`, {
      headers: { "Authorization": `Bearer ${accessToken}` },
    });

    if (!subResp.ok) {
      return jsonResponse({ error: "Invalid subscription" }, 400);
    }

    const subData = await subResp.json() as any;
    if (subData.status !== "ACTIVE") {
      return jsonResponse({ error: "Subscription not active" }, 400);
    }

    await addProUser(env.DB, email, subscriptionId);
    return jsonResponse({ success: true, email });
  } catch (e: any) {
    return jsonResponse({ error: `PayPal verification failed: ${e.message}` }, 500);
  }
}

async function handleTrackClick(request: Request, env: Env): Promise<Response> {
  let body: any;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: "Invalid JSON" }, 400);
  }

  const button = body.button || "";
  if (!button) {
    return jsonResponse({ error: "Missing button" }, 400);
  }

  await trackClick(env.DB, button);
  return jsonResponse({ success: true });
}

async function handleDebugAddPro(request: Request, env: Env): Promise<Response> {
  let body: any;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: "Invalid JSON" }, 400);
  }

  const email = (body.email || "").toLowerCase().trim();
  if (!email) {
    return jsonResponse({ error: "Missing email" }, 400);
  }

  await addProUser(env.DB, email, "debug");
  return jsonResponse({ success: true, email });
}

async function handleCheckPro(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  const email = (url.searchParams.get("email") || "").toLowerCase().trim();
  if (!email) {
    return jsonResponse({ is_pro: false });
  }
  const pro = await isProUser(env.DB, email);
  return jsonResponse({ is_pro: pro, email });
}

// ============ MAIN EXPORT ============

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const method = request.method;

    // Handle CORS preflight
    if (method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    try {
      if (url.pathname === "/api/config" && method === "GET") {
        return await handleConfig(env);
      }
      if (url.pathname === "/api/stats" && method === "GET") {
        return await handleStats(env);
      }
      if (url.pathname === "/api/enhance" && method === "POST") {
        return await handleEnhance(request, env);
      }
      if (url.pathname === "/api/activate-pro" && method === "POST") {
        return await handleActivatePro(request, env);
      }
      if (url.pathname === "/api/track-click" && method === "POST") {
        return await handleTrackClick(request, env);
      }
      if (url.pathname === "/api/debug-add-pro" && method === "POST") {
        return await handleDebugAddPro(request, env);
      }
      if (url.pathname === "/api/check-pro" && method === "GET") {
        return await handleCheckPro(request, env);
      }

      // 404 for unmatched API routes
      return jsonResponse({ error: "Not found" }, 404);
    } catch (e: any) {
      console.error("Worker error:", e);
      return jsonResponse({ error: "Internal server error" }, 500);
    }
  },
};
