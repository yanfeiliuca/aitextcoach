// DeepSeek API integration with budget control

import type { Env } from "./db";

const DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions";
const DEEPSEEK_MODEL = "deepseek-chat";

export interface BudgetState {
  spent: number;
  limit: number;
  mode: "normal" | "limited" | "critical";
}

const BUDGET_KEY = "budget_state";
const BUDGET_LIMIT = 10.0;

export async function loadBudget(kv: KVNamespace): Promise<BudgetState> {
  const data = await kv.get(BUDGET_KEY, "json");
  if (data) {
    return data as BudgetState;
  }
  return { spent: 0, limit: BUDGET_LIMIT, mode: "normal" };
}

export async function saveBudget(kv: KVNamespace, state: BudgetState): Promise<void> {
  await kv.put(BUDGET_KEY, JSON.stringify(state));
}

export function checkBudget(state: BudgetState): BudgetState {
  const pct = state.spent / state.limit;
  if (pct >= 0.95) {
    return { ...state, mode: "critical" };
  } else if (pct >= 0.75) {
    return { ...state, mode: "limited" };
  }
  return { ...state, mode: "normal" };
}

// Rough cost estimation per 1K tokens (DeepSeek Chat ~$0.0003/1K input, $0.001/1K output)
function estimateCost(inputTokens: number, outputTokens: number): number {
  return (inputTokens * 0.0003 + outputTokens * 0.001) / 1000;
}

export async function callDeepSeek(
  text: string,
  style: string,
  env: Env,
  budgetMode: string = "normal"
): Promise<{ result: string; cost: number } | { error: string }> {
  const budget = checkBudget(await loadBudget(env.KV));

  if (budget.mode === "critical") {
    return { error: "Service temporarily unavailable due to budget limit. Please try again later." };
  }

  const prompts: Record<string, string> = {
    formal: `Rewrite the following text to be more formal, professional, and polished. Maintain the original meaning but improve vocabulary and structure:\n\n${text}`,
    casual: `Rewrite the following text to be more casual, friendly, and conversational. Keep it natural and approachable:\n\n${text}`,
    academic: `Rewrite the following text in an academic style. Use sophisticated vocabulary, clear structure, and formal tone suitable for scholarly writing:\n\n${text}`,
    simple: `Rewrite the following text to be simpler and easier to understand. Use plain language, shorter sentences, and clear explanations:\n\n${text}`,
    creative: `Rewrite the following text to be more creative and engaging. Use vivid language, storytelling elements, and compelling narrative:\n\n${text}`,
    business: `Rewrite the following text for a business context. Make it clear, actionable, and professional:\n\n${text}`,
  };

  const prompt = prompts[style] || prompts.casual;

  // Budget-aware token limits
  const maxTokens = budgetMode === "limited" ? 300 : budgetMode === "critical" ? 150 : 500;

  try {
    const response = await fetch(DEEPSEEK_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${env.DS_API_KEY}`,
      },
      body: JSON.stringify({
        model: DEEPSEEK_MODEL,
        messages: [{ role: "user", content: prompt }],
        max_tokens: maxTokens,
        temperature: 0.7,
      }),
    });

    if (!response.ok) {
      const err = await response.text();
      return { error: `DeepSeek API error: ${response.status} - ${err}` };
    }

    const data = await response.json() as any;
    const content = data.choices?.[0]?.message?.content || "";

    // Estimate and update budget
    const inputTokens = Math.ceil(prompt.length / 4);
    const outputTokens = Math.ceil(content.length / 4);
    const cost = estimateCost(inputTokens, outputTokens);

    budget.spent += cost;
    await saveBudget(env.KV, checkBudget(budget));

    return { result: content.trim(), cost };
  } catch (e: any) {
    return { error: `DeepSeek request failed: ${e.message}` };
  }
}
