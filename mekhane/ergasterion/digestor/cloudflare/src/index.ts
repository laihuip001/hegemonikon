/**
 * Digestor Scheduler - Cloudflare Workers Cron
 * 
 * 毎日 6:00 JST に論文収集を実行
 * 
 * Setup:
 *   cd cloudflare
 *   npm install
 *   wrangler secret put SLACK_WEBHOOK_URL --env production
 *   wrangler deploy --env production
 */

export interface Env {
    SLACK_WEBHOOK_URL?: string;
    DIGESTOR_MAX_PAPERS: string;
    DIGESTOR_MAX_CANDIDATES: string;
}

interface DigestorResult {
    timestamp: string;
    total_papers: number;
    candidates_selected: number;
    candidates: Array<{
        title: string;
        score: number;
        url: string;
    }>;
}

export default {
    async scheduled(
        event: ScheduledEvent,
        env: Env,
        ctx: ExecutionContext
    ): Promise<void> {
        console.log(`[Digestor] Cron triggered at ${new Date().toISOString()}`);

        try {
            // arXiv API で論文検索
            const papers = await fetchFromArxiv(env);

            // 結果をログ
            console.log(`[Digestor] Fetched ${papers.length} papers`);

            // Slack 通知（設定されている場合）
            if (env.SLACK_WEBHOOK_URL && papers.length > 0) {
                await notifySlack(env.SLACK_WEBHOOK_URL, papers);
            }

            console.log(`[Digestor] Complete`);
        } catch (error) {
            console.error(`[Digestor] Error: ${error}`);

            // エラー時も Slack 通知
            if (env.SLACK_WEBHOOK_URL) {
                await fetch(env.SLACK_WEBHOOK_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text: `❌ Digestor Scheduler failed: ${error}`
                    })
                });
            }

            throw error;
        }
    }
};

async function fetchFromArxiv(env: Env): Promise<Array<{ title: string; url: string }>> {
    const queries = [
        'LLM autonomous agent architecture',
        'active inference cognitive',
        'metacognition AI systems'
    ];

    const papers: Array<{ title: string; url: string }> = [];
    const maxPapers = parseInt(env.DIGESTOR_MAX_PAPERS) || 30;
    const perQuery = Math.floor(maxPapers / queries.length);

    for (const query of queries) {
        const url = `http://export.arxiv.org/api/query?search_query=all:${encodeURIComponent(query)}&start=0&max_results=${perQuery}&sortBy=submittedDate&sortOrder=descending`;

        const response = await fetch(url);
        const xml = await response.text();

        // 簡易 XML パース（タイトルと URL を抽出）
        const entries = xml.match(/<entry>[\s\S]*?<\/entry>/g) || [];

        for (const entry of entries) {
            const titleMatch = entry.match(/<title>([\s\S]*?)<\/title>/);
            const idMatch = entry.match(/<id>([\s\S]*?)<\/id>/);

            if (titleMatch && idMatch) {
                papers.push({
                    title: titleMatch[1].replace(/\s+/g, ' ').trim(),
                    url: idMatch[1].trim()
                });
            }
        }
    }

    // 重複除去
    const seen = new Set<string>();
    return papers.filter(p => {
        if (seen.has(p.url)) return false;
        seen.add(p.url);
        return true;
    });
}

async function notifySlack(
    webhookUrl: string,
    papers: Array<{ title: string; url: string }>
): Promise<void> {
    const maxCandidates = 5;
    const topPapers = papers.slice(0, maxCandidates);

    const message = {
        text: `🍽️ Digestor: ${papers.length} 論文を収集しました`,
        blocks: [
            {
                type: 'header',
                text: {
                    type: 'plain_text',
                    text: `🍽️ Digestor: ${papers.length} 論文収集`
                }
            },
            {
                type: 'section',
                text: {
                    type: 'mrkdwn',
                    text: topPapers.map((p, i) =>
                        `${i + 1}. <${p.url}|${p.title.substring(0, 50)}...>`
                    ).join('\n')
                }
            }
        ]
    };

    await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(message)
    });
}
