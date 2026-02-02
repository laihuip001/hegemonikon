/**
 * Swarm Scheduler - Cloudflare Workers
 * 
 * Backup scheduler for Hegemonikon 720 daily reviews.
 * Runs at 4:00 AM JST (19:00 UTC) via Cron Trigger.
 * 
 * Primary: systemd timer on home PC
 * Backup: This Cloudflare Worker (failover)
 */

export interface Env {
    JULES_BASE_URL: string;
    JULES_API_KEY_1: string;
    JULES_API_KEY_2: string;
    JULES_API_KEY_3: string;
    JULES_API_KEY_4: string;
    JULES_API_KEY_5: string;
    JULES_API_KEY_6: string;
    JULES_API_KEY_7: string;
    JULES_API_KEY_8: string;
    JULES_API_KEY_9: string;
    SLACK_WEBHOOK_URL?: string;
}

interface AllocationTask {
    domain: string;
    axis: string;
    perspective_id: string;
    allocation_type: string;
}

// Weekly focus rotation (Monday = 0)
const WEEKLY_FOCUS: Record<number, string[]> = {
    0: ["Security", "Auth"],     // Monday
    1: ["Performance", "Memory"], // Tuesday
    2: ["Error", "Async"],       // Wednesday
    3: ["API", "Integration"],   // Thursday
    4: ["Testing", "Docs"],      // Friday
    5: ["Logging", "Config"],    // Saturday
    6: ["Architecture", "DI"],   // Sunday
};

const ALL_DOMAINS = [
    "Security", "Error", "Performance", "Memory",
    "Async", "Logging", "Testing", "API",
    "Auth", "Config", "Modules", "DI",
    "Lifecycle", "Caching", "Networking", "DB",
    "UI", "Docs", "Architecture", "Integration",
];

const ALL_AXES = [
    "O1", "O2", "O3", "O4", "S1", "S2", "S3", "S4",
    "H1", "H2", "H3", "H4", "P1", "P2", "P3", "P4",
    "K1", "K2", "K3", "K4", "A1", "A2", "A3", "A4",
];

function generateAllocationPlan(budget: number): AllocationTask[] {
    const tasks: AllocationTask[] = [];
    const weekday = new Date().getDay();

    // 40% Change-driven (simplified: use focus domains)
    const changeBudget = Math.floor(budget * 0.4);
    const focusDomains = WEEKLY_FOCUS[weekday] || ["Architecture"];

    for (const domain of focusDomains) {
        for (const axis of ALL_AXES.slice(0, 5)) {
            if (tasks.length >= changeBudget) break;
            tasks.push({
                domain,
                axis,
                perspective_id: `${domain}-${axis}`,
                allocation_type: "change_driven"
            });
        }
    }

    // 40% Discovery (random sampling)
    const discoveryBudget = Math.floor(budget * 0.4);
    while (tasks.length < changeBudget + discoveryBudget) {
        const domain = ALL_DOMAINS[Math.floor(Math.random() * ALL_DOMAINS.length)];
        const axis = ALL_AXES[Math.floor(Math.random() * ALL_AXES.length)];
        const id = `${domain}-${axis}`;

        if (!tasks.some(t => t.perspective_id === id)) {
            tasks.push({
                domain,
                axis,
                perspective_id: id,
                allocation_type: "discovery"
            });
        }
    }

    // 20% Weekly focus
    const focusBudget = budget - tasks.length;
    for (const domain of focusDomains) {
        for (const axis of ALL_AXES) {
            if (tasks.length >= budget) break;
            const id = `${domain}-${axis}`;
            if (!tasks.some(t => t.perspective_id === id)) {
                tasks.push({
                    domain,
                    axis,
                    perspective_id: id,
                    allocation_type: "weekly_focus"
                });
            }
        }
    }

    return tasks.slice(0, budget);
}

function getApiKeys(env: Env): string[] {
    return [
        env.JULES_API_KEY_1,
        env.JULES_API_KEY_2,
        env.JULES_API_KEY_3,
        env.JULES_API_KEY_4,
        env.JULES_API_KEY_5,
        env.JULES_API_KEY_6,
        env.JULES_API_KEY_7,
        env.JULES_API_KEY_8,
        env.JULES_API_KEY_9,
    ].filter(Boolean);
}

async function createSession(
    baseUrl: string,
    apiKey: string,
    task: AllocationTask
): Promise<{ success: boolean; sessionId?: string; error?: string }> {
    const prompt = `You are a ${task.domain} specialist reviewing code through the lens of ${task.axis}.

## Your Unique Perspective
**Domain Focus:** ${task.domain}
**Cognitive Lens:** ${task.axis}

## Review Protocol
1. Analyze the code specifically from your perspective
2. Identify issues ONLY within your domain × axis intersection
3. Report findings in structured format

## Silence Protocol
If you find nothing from your unique perspective, respond:
SILENCE: No issues found from ${task.domain} × ${task.axis} perspective
`;

    try {
        const response = await fetch(`${baseUrl}/sessions`, {
            method: 'POST',
            headers: {
                'X-Goog-Api-Key': apiKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: `Synedrion v2: ${task.perspective_id}`,
                prompt,
                source_context: {
                    source: "sources/github/laihuip001/hegemonikon",
                    github_repo_context: { starting_branch: "master" }
                }
            })
        });

        if (!response.ok) {
            return { success: false, error: `HTTP ${response.status}` };
        }

        const data = await response.json() as { id?: string };
        return { success: true, sessionId: data.id };
    } catch (e) {
        return { success: false, error: String(e) };
    }
}

export default {
    async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
        const startTime = new Date().toISOString();
        console.log(`[${startTime}] Swarm Scheduler triggered`);

        const DAILY_BUDGET = 720;
        const SESSIONS_PER_KEY = 80;

        const tasks = generateAllocationPlan(DAILY_BUDGET);
        const keys = getApiKeys(env);

        console.log(`Tasks: ${tasks.length}, Keys: ${keys.length}`);

        if (keys.length === 0) {
            console.error("No API keys configured!");
            return;
        }

        let successCount = 0;
        let failCount = 0;

        // Distribute tasks across keys
        for (let i = 0; i < tasks.length; i++) {
            const keyIndex = Math.floor(i / SESSIONS_PER_KEY) % keys.length;
            const key = keys[keyIndex];
            const task = tasks[i];

            const result = await createSession(env.JULES_BASE_URL, key, task);

            if (result.success) {
                successCount++;
                console.log(`✓ ${task.perspective_id} → ${result.sessionId}`);
            } else {
                failCount++;
                console.error(`✗ ${task.perspective_id}: ${result.error}`);
            }

            // Rate limiting: 2 requests per second
            await new Promise(r => setTimeout(r, 500));
        }

        const endTime = new Date().toISOString();
        const summary = {
            startTime,
            endTime,
            totalTasks: tasks.length,
            success: successCount,
            failed: failCount,
        };

        console.log(`[${endTime}] Complete:`, JSON.stringify(summary));

        // Slack notification
        if (env.SLACK_WEBHOOK_URL) {
            await fetch(env.SLACK_WEBHOOK_URL, {
                method: 'POST',
                body: JSON.stringify({
                    text: `🤖 Swarm Scheduler Complete\n✅ ${successCount} / ❌ ${failCount} / Total: ${tasks.length}`
                })
            });
        }
    },

    // HTTP handler for manual testing
    async fetch(request: Request, env: Env): Promise<Response> {
        const url = new URL(request.url);

        if (url.pathname === '/test') {
            const keys = getApiKeys(env);
            return new Response(JSON.stringify({
                status: "ok",
                keysConfigured: keys.length,
                baseUrl: env.JULES_BASE_URL,
            }), {
                headers: { 'Content-Type': 'application/json' }
            });
        }

        return new Response("Swarm Scheduler - Cloudflare Workers\n\nEndpoints:\n  /test - Check configuration", {
            headers: { 'Content-Type': 'text/plain' }
        });
    }
};
