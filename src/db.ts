// Database operations for AITextCoach on Cloudflare D1

export interface Env {
  DB: D1Database;
  KV: KVNamespace;
  DS_API_KEY: string;
  PAYPAL_CLIENT_SECRET: string;
  PAYPAL_MODE: string;
  PAYPAL_PLAN_ID: string;
}

// ============ USERS ============

export async function isProUser(db: D1Database, email: string | null): Promise<boolean> {
  if (!email) return false;
  const result = await db
    .prepare("SELECT is_pro FROM users WHERE email = ?")
    .bind(email.toLowerCase().trim())
    .first<{ is_pro: number }>();
  return result ? result.is_pro === 1 : false;
}

export async function addProUser(db: D1Database, email: string, subscriptionId?: string): Promise<void> {
  const normalized = email.toLowerCase().trim();
  await db
    .prepare(`
      INSERT INTO users (email, is_pro, subscription_id)
      VALUES (?, 1, ?)
      ON CONFLICT(email) DO UPDATE SET
        is_pro = 1,
        subscription_id = COALESCE(EXCLUDED.subscription_id, users.subscription_id)
    `)
    .bind(normalized, subscriptionId || null)
    .run();
}

// ============ USAGE ============

function getToday(): string {
  return new Date().toISOString().slice(0, 10); // YYYY-MM-DD
}

export async function getTodayUsage(db: D1Database, email: string | null): Promise<number> {
  const today = getToday();
  if (!email) return 0;
  const result = await db
    .prepare("SELECT chars_used FROM usage_stats WHERE email = ? AND usage_date = ?")
    .bind(email.toLowerCase(), today)
    .first<{ chars_used: number }>();
  return result ? result.chars_used : 0;
}

export async function addUsage(db: D1Database, email: string | null, chars: number): Promise<void> {
  const today = getToday();
  const normalized = email ? email.toLowerCase().trim() : "anon";
  await db
    .prepare(`
      INSERT INTO usage_stats (email, chars_used, usage_date)
      VALUES (?, ?, ?)
      ON CONFLICT(email, usage_date) DO UPDATE SET
        chars_used = usage_stats.chars_used + EXCLUDED.chars_used
    `)
    .bind(normalized, chars, today)
    .run();
}

// ============ CLICK STATS ============

export async function trackClick(db: D1Database, button: string): Promise<void> {
  const today = getToday();
  await db
    .prepare(`
      INSERT INTO click_stats (button_type, click_date, count)
      VALUES (?, ?, 1)
      ON CONFLICT(button_type, click_date) DO UPDATE SET
        count = click_stats.count + 1
    `)
    .bind(button, today)
    .run();
}

export interface StatsResult {
  today: Record<string, number>;
  total: Record<string, number>;
  daily_breakdown: Record<string, Record<string, number>>;
}

export async function getStats(db: D1Database): Promise<StatsResult> {
  const today = getToday();

  const todayRows = await db
    .prepare("SELECT button_type, count FROM click_stats WHERE click_date = ?")
    .bind(today)
    .all<{ button_type: string; count: number }>();

  const totalRows = await db
    .prepare("SELECT button_type, SUM(count) as total FROM click_stats GROUP BY button_type")
    .all<{ button_type: string; total: number }>();

  const breakdownRows = await db
    .prepare("SELECT click_date, button_type, count FROM click_stats ORDER BY click_date DESC")
    .all<{ click_date: string; button_type: string; count: number }>();

  const todayStats: Record<string, number> = {};
  for (const r of todayRows.results || []) {
    todayStats[r.button_type] = r.count;
  }

  const totalStats: Record<string, number> = {};
  for (const r of totalRows.results || []) {
    totalStats[r.button_type] = r.total;
  }

  const breakdown: Record<string, Record<string, number>> = {};
  for (const r of breakdownRows.results || []) {
    const d = r.click_date;
    if (!breakdown[d]) breakdown[d] = {};
    breakdown[d][r.button_type] = r.count;
  }

  return { today: todayStats, total: totalStats, daily_breakdown: breakdown };
}
