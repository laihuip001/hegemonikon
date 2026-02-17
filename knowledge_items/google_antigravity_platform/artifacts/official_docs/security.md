# Security & Controls

## Strict Mode

Enhanced security controls for sensitive environments.

- **URL Control**: Enforces Allowlist/Denylist for Read URL tool and markdown images.
- **Review Policies**: Terminal, Browser JS, and Artifact review are all locked to "Request Review".
- **File System**: Respects `.gitignore` and disables access outside the workspace.

---

## Sandbox Mode

Explains kernel-level isolation for terminal commands.

- **Platform Support**: Primarily macOS using Seatbelt.
- **Restrictions**: Limited file system and network access.
- **Violation Handling**: System provides notifications when a command attempts to violate safety constraints.

---

## Allowlist / Denylist

The security model for web interaction.

- **Global Denylist**: Dangerous URLs are blocked via a server-side denylist (`BadUrlsChecker`).
- **Local Allowlist**: Trusted URLs can be added to a local allowlist for seamless access.
