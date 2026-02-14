import { api } from '../api/client';
import type { Notification } from '../api/client';
import { getCurrentRoute, esc, applyStaggeredFadeIn, startPolling, fireOsNotifications } from '../utils';

function relativeTime(isoTimestamp: string): string {
    const now = Date.now();
    const then = new Date(isoTimestamp).getTime();
    const diffSec = Math.floor((now - then) / 1000);
    if (diffSec < 60) return `${diffSec}秒前`;
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}分前`;
    const diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) return `${diffHour}時間前`;
    const diffDay = Math.floor(diffHour / 24);
    return `${diffDay}日前`;
}

const LEVEL_LABELS: Record<string, string> = {
    CRITICAL: '🚨 緊急',
    HIGH: '⚠️ 重要',
    INFO: 'ℹ️ 情報',
};

function formatNotifBody(body: string): string {
    const lines = body.split('\n');
    const metaTags: string[] = [];
    const textLines: string[] = [];

    for (const line of lines) {
        const match = line.match(/^([A-Za-z_]+):\s*(.+)$/);
        if (match) {
            metaTags.push(`<span class="notif-meta-tag"><strong>${esc(match[1])}</strong> ${esc(match[2])}</span>`);
        } else if (line.trim()) {
            textLines.push(esc(line));
        }
    }

    let html = '';
    if (textLines.length > 0) {
        html += `<div class="notif-body-text">${textLines.join('<br>')}</div>`;
    }
    if (metaTags.length > 0) {
        html += `<div class="notif-meta-row">${metaTags.join('')}</div>`;
    }
    return html;
}

let notifLevelFilter = '';

export async function renderNotifications(): Promise<void> {
    await renderNotificationsContent();
    startPolling(renderNotificationsContent, 30_000);
}

async function renderNotificationsContent(): Promise<void> {
    let notifications: Notification[] = [];
    try {
        notifications = await api.notifications(50, notifLevelFilter || undefined);
    } catch (err) {
        const app = document.getElementById('view-content')!;
        if (getCurrentRoute() !== 'notifications') return;
        app.innerHTML = `<div class="card status-error">通知を取得できません: ${esc((err as Error).message)}</div>`;
        return;
    }

    const pksNuggets = await api.pksPush().catch((): null => null);
    if (pksNuggets && pksNuggets.nuggets.length > 0) {
        const pksAsNotifs: Notification[] = pksNuggets.nuggets.map((n) => ({
            id: `pks-${n.title.slice(0, 20)}`,
            timestamp: pksNuggets.timestamp,
            source: '📡 PKS',
            level: 'INFO' as const,
            title: n.title,
            body: (n.push_reason ? `💡 ${n.push_reason}\n` : '') +
                (n.abstract ? n.abstract.substring(0, 200) : '') +
                (n.relevance_score ? `\nRelevance: ${(n.relevance_score * 100).toFixed(0)}%` : ''),
            data: { pks: true, relevance_score: n.relevance_score },
        }));
        notifications = [...pksAsNotifs, ...notifications];
    }

    const app = document.getElementById('view-content')!;
    if (getCurrentRoute() !== 'notifications') return;

    const critCount = notifications.filter(n => n.level === 'CRITICAL').length;
    const highCount = notifications.filter(n => n.level === 'HIGH').length;
    const infoCount = notifications.filter(n => n.level === 'INFO').length;

    const filtered = notifLevelFilter
        ? notifications.filter(n => n.level === notifLevelFilter)
        : notifications;

    const cardsHtml = filtered.length === 0
        ? `<div class="empty-state"><div style="font-size:2.5rem; margin-bottom:0.5rem;">📭</div><p>通知はありません</p></div>`
        : filtered.map((n: Notification) => {
            const levelClass = n.level.toLowerCase();
            const levelLabel = LEVEL_LABELS[n.level] ?? n.level;
            const dotCls = n.level === 'CRITICAL' ? 'error' : n.level === 'HIGH' ? 'warn' : 'ok';
            const isDigestor = n.data?.digestor === true;
            const digestorUrl = isDigestor && n.data?.url ? String(n.data.url) : '';
            const digestorScore = isDigestor && n.data?.score ? Number(n.data.score) : 0;
            return `
          <div class="card notif-card level-${levelClass}${isDigestor ? ' notif-digestor' : ''}">
            <div class="notif-top">
              <span class="status-dot ${dotCls}"></span>
              <span class="notif-source">${esc(n.source)}</span>
              <span class="notif-level ${levelClass}">${esc(levelLabel)}</span>
              ${isDigestor && digestorScore > 0
                    ? `<span class="notif-score" title="関連度スコア">${(digestorScore * 100).toFixed(0)}%</span>`
                    : ''}
              <span class="notif-time">${esc(relativeTime(n.timestamp))}</span>
            </div>
            <div class="notif-title">${esc(n.title)}</div>
            <div class="notif-body">${formatNotifBody(n.body)}</div>
            ${digestorUrl
                    ? `<a href="${esc(digestorUrl)}" target="_blank" rel="noopener" class="btn btn-sm notif-link-btn">📎 論文を開く</a>`
                    : ''}
          </div>`;
        }).join('');

    const tabData = [
        { value: '', label: 'すべて', count: notifications.length },
        { value: 'CRITICAL', label: '🚨 緊急', count: critCount },
        { value: 'HIGH', label: '⚠️ 重要', count: highCount },
        { value: 'INFO', label: 'ℹ️ 情報', count: infoCount },
    ];

    const tabsHtml = tabData.map(t =>
        `<button class="notif-tab ${notifLevelFilter === t.value ? 'active' : ''}" data-level="${esc(t.value)}">
      ${t.label}
      <span class="notif-tab-count">${t.count}</span>
    </button>`
    ).join('');

    app.innerHTML = `
    <div class="notif-header">
      <h1>通知</h1>
      <div class="metric-label" style="margin-left:auto;">${notifications.length} 件</div>
      <button id="notif-refresh-btn" class="btn btn-sm">更新</button>
    </div>
    <div class="notif-tab-bar">${tabsHtml}</div>
    ${cardsHtml}
  `;

    void fireOsNotifications(notifications);

    document.querySelectorAll('.notif-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            notifLevelFilter = tab.getAttribute('data-level') ?? '';
            void renderNotificationsContent();
        });
    });

    document.getElementById('notif-refresh-btn')?.addEventListener('click', () => {
        void renderNotificationsContent();
    });

    applyStaggeredFadeIn(app);
}
