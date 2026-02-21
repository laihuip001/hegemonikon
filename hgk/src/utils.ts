/**
 * Shared utilities for HGK Desktop views.
 * Extracted from main.ts for modularity.
 */

import type { Notification } from './api/client';
import { isPermissionGranted, requestPermission, sendNotification } from '@tauri-apps/plugin-notification';

// ─── Route State ─────────────────────────────────────────────

let _currentRoute = '';

export function getCurrentRoute(): string { return _currentRoute; }
export function setCurrentRoute(route: string): void { _currentRoute = route; }

// ─── HTML Escape ─────────────────────────────────────────────

/** Escape HTML to prevent XSS */
export function esc(s: string | undefined | null): string {
    if (!s) return '';
    return s
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// ─── Animations ──────────────────────────────────────────────

/** Animate a number counting up from 0 to target */
export function animateCountUp(el: HTMLElement, target: number, duration = 800): void {
    const start = performance.now();
    const isFloat = !Number.isInteger(target);
    function update(now: number): void {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = target * eased;
        el.textContent = isFloat ? current.toFixed(1) : String(Math.round(current));
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

/** Apply count-up animation to all [data-count-target] elements within a container */
export function applyCountUpAnimations(container: HTMLElement): void {
    container.querySelectorAll('[data-count-target]').forEach(el => {
        const target = parseFloat((el as HTMLElement).dataset.countTarget || '0');
        if (target > 0) {
            const observer = new IntersectionObserver(entries => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        animateCountUp(el as HTMLElement, target);
                        observer.disconnect();
                    }
                });
            });
            observer.observe(el);
        }
    });
}

/** Apply staggered fade-in to cards within a container */
export function applyStaggeredFadeIn(container: HTMLElement): void {
    const cards = container.querySelectorAll('.card');
    cards.forEach((card, index) => {
        const el = card as HTMLElement;
        el.style.opacity = '0';
        el.style.transform = 'translateY(12px)';
        el.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 60);
    });
}

// ─── Polling Manager ─────────────────────────────────────────

let pollingTimers: ReturnType<typeof setInterval>[] = [];

export function clearPolling(): void {
    pollingTimers.forEach(t => clearInterval(t));
    pollingTimers = [];
}

export function startPolling(fn: () => Promise<void>, intervalMs: number): void {
    pollingTimers.push(setInterval(() => { void fn(); }, intervalMs));
}

// ─── OS Notifications ────────────────────────────────────────

const sentOsNotifIds = new Set<string>();

/** Fire OS native notifications for CRITICAL/HIGH items */
export async function fireOsNotifications(notifications: Notification[]): Promise<void> {
    const urgent = notifications.filter(
        n => (n.level === 'CRITICAL' || n.level === 'HIGH') && !sentOsNotifIds.has(n.id),
    );
    if (urgent.length === 0) return;

    let permOk = await isPermissionGranted();
    if (!permOk) {
        const perm = await requestPermission();
        permOk = perm === 'granted';
    }
    if (!permOk) return;

    for (const n of urgent) {
        sendNotification({ title: n.title, body: n.body.substring(0, 200) });
        sentOsNotifIds.add(n.id);
    }
}

// ─── Relative Time ───────────────────────────────────────────

/** Convert ISO timestamp to Japanese relative time string */
export function relativeTime(isoTimestamp: string): string {
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

/** Convert Date object to Japanese relative time string */
export function formatTimeAgo(date: Date): string {
    const now = Date.now();
    const diffSec = Math.floor((now - date.getTime()) / 1000);
    if (diffSec < 60) return `${diffSec}秒前`;
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}分前`;
    const diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) return `${diffHour}時間前`;
    return date.toLocaleDateString('ja-JP');
}

// ─── Skeleton Loader ─────────────────────────────────────────

/** Skeleton loader HTML for page transitions */
export function skeletonHTML(): string {
    return `
    <div class="skeleton-loader">
      <div class="skeleton-header"></div>
      <div class="skeleton-grid">
        <div class="skeleton-card"></div>
        <div class="skeleton-card"></div>
        <div class="skeleton-card"></div>
      </div>
      <div class="skeleton-table"></div>
    </div>
  `;
}
