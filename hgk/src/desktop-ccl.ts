// CCL → Tauri Desktop Command Bridge
//
// Parses @desktop{action, ...params} CCL expressions and dispatches
// them to the corresponding Tauri IPC commands.
//
// Architecture:
//   CCL expression (text) → parse → DesktopCommand → invoke() → result
//
// This is the "方式 C" bridge: all logic runs in the frontend,
// calling Tauri IPC directly without any intermediate server.

import { invoke } from '@tauri-apps/api/core';

/** Supported desktop CCL actions */
export type DesktopAction =
    | 'list'
    | 'tree'
    | 'click'
    | 'type'
    | 'screenshot'
    | 'find'
    | 'focus'
    | 'do_action'
    | 'extents';

/** Parsed desktop command */
export interface DesktopCommand {
    action: DesktopAction;
    params: Record<string, string | number>;
}

/** Command execution result */
export interface CommandResult {
    success: boolean;
    action: DesktopAction;
    data: unknown;
    elapsed_ms: number;
}

/**
 * Parse a @desktop{...} CCL expression into a DesktopCommand.
 *
 * Examples:
 *   @desktop{list}
 *   @desktop{tree, app="firefox"}
 *   @desktop{click, x=100, y=200}
 *   @desktop{type, text="hello world"}
 *   @desktop{find, role="push button", name="Save"}
 */
export function parseCCL(expr: string): DesktopCommand | null {
    // Match @desktop{content}
    const match = expr.match(/@desktop\{([^}]+)\}/);
    if (!match) return null;

    const content = match[1];
    if (!content) return null;
    const parts = content.trim().split(',').map(p => p.trim());

    const action = parts[0] as DesktopAction;
    if (!VALID_ACTIONS.has(action)) return null;

    const params: Record<string, string | number> = {};

    for (let i = 1; i < parts.length; i++) {
        const part = parts[i];
        if (!part) continue;
        const kv = part.match(/^(\w+)\s*=\s*"?([^"]*)"?$/);
        if (kv && kv[1] && kv[2] !== undefined) {
            const key = kv[1];
            const val = kv[2];
            // Try to parse as number
            const num = Number(val);
            params[key] = isNaN(num) ? val : num;
        }
    }

    return { action, params };
}

const VALID_ACTIONS = new Set<DesktopAction>([
    'list', 'tree', 'click', 'type', 'screenshot',
    'find', 'focus', 'do_action', 'extents',
]);

/**
 * Execute a parsed DesktopCommand via Tauri IPC.
 */
export async function executeCommand(cmd: DesktopCommand): Promise<CommandResult> {
    const start = performance.now();

    try {
        let data: unknown;

        switch (cmd.action) {
            case 'list':
                data = await invoke('list_desktop');
                break;

            case 'tree':
                data = await invoke('get_element_tree', {
                    busName: String(cmd.params.bus || ''),
                    path: String(cmd.params.path || '/org/a11y/atspi/accessible/root'),
                    maxDepth: Number(cmd.params.depth) || 3,
                });
                break;

            case 'click':
                data = await invoke('desktop_click', {
                    busName: cmd.params.bus ? String(cmd.params.bus) : undefined,
                    objectPath: cmd.params.path ? String(cmd.params.path) : undefined,
                    x: cmd.params.x != null ? Number(cmd.params.x) : undefined,
                    y: cmd.params.y != null ? Number(cmd.params.y) : undefined,
                });
                break;

            case 'type':
                data = await invoke('desktop_type', {
                    busName: cmd.params.bus ? String(cmd.params.bus) : undefined,
                    objectPath: cmd.params.path ? String(cmd.params.path) : undefined,
                    text: String(cmd.params.text || ''),
                });
                break;

            case 'screenshot':
                data = await invoke('desktop_screenshot');
                break;

            case 'find':
                data = await invoke('desktop_find_elements', {
                    busName: String(cmd.params.bus || ''),
                    objectPath: String(cmd.params.path || '/org/a11y/atspi/accessible/root'),
                    role: cmd.params.role ? String(cmd.params.role) : undefined,
                    name: cmd.params.name ? String(cmd.params.name) : undefined,
                    maxDepth: Number(cmd.params.depth) || 4,
                });
                break;

            case 'focus':
                data = await invoke('desktop_focus', {
                    busName: String(cmd.params.bus || ''),
                    objectPath: String(cmd.params.path || ''),
                });
                break;

            case 'do_action':
                data = await invoke('desktop_do_action', {
                    busName: String(cmd.params.bus || ''),
                    objectPath: String(cmd.params.path || ''),
                    actionIndex: Number(cmd.params.index) || 0,
                });
                break;

            case 'extents':
                data = await invoke('desktop_get_extents', {
                    busName: String(cmd.params.bus || ''),
                    objectPath: String(cmd.params.path || ''),
                });
                break;

            default:
                throw new Error(`Unknown action: ${cmd.action}`);
        }

        return {
            success: true,
            action: cmd.action,
            data,
            elapsed_ms: performance.now() - start,
        };
    } catch (err) {
        return {
            success: false,
            action: cmd.action,
            data: String(err),
            elapsed_ms: performance.now() - start,
        };
    }
}

/**
 * Parse and execute a CCL expression in one call.
 * Convenience function for direct use.
 */
export async function executeCCL(expr: string): Promise<CommandResult> {
    const cmd = parseCCL(expr);
    if (!cmd) {
        return {
            success: false,
            action: 'list' as DesktopAction,
            data: `Invalid CCL expression: ${expr}`,
            elapsed_ms: 0,
        };
    }
    return executeCommand(cmd);
}
