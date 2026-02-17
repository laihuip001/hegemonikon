# OS and System Requirements

Google Antigravity has specific requirements for various operating systems to ensure stable execution of the IDE and its underlying agent processes.

## 1. Linux Requirements

Antigravity for Linux requires modern library versions (glibc/glibcxx).

- **glibc**: `>= 2.28`
- **glibcxx**: `>= 3.4.25`

**Verified Distributions**:

- Ubuntu 20+
- Debian 10+
- Fedora 36+
- RHEL 8+

## 2. macOS Requirements

Antigravity is optimized for Apple Silicon and modern macOS versions.

- **Version**: macOS 12 (Monterey) or higher.
- **Architecture**: **X86 is not supported**. Apple Silicon (M1/M2/M3) is required.
- **Maintenance**: Typically supports the current and two previous macOS versions receiving security updates.

## 3. Windows Requirements

- **OS**: Windows 10 (64-bit) or higher.

## 4. Update Protocol

The application manages its own updates via a "Restart to Update" notification in the UI, ensuring that all agent-orchestration logic remains current with the host platform.
