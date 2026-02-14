// AT-SPI2 Tree Cache — TTL-based caching for accessibility tree data
//
// Caches tree traversal results to avoid repeated D-Bus queries during
// rapid successive operations (e.g. find → click → verify).
// Cache entries expire after TTL_SECS seconds.

use std::collections::HashMap;
use std::sync::{LazyLock, Mutex};
use std::time::{Duration, Instant};

use super::tree::A11yNode;

/// Cache TTL — entries older than this are considered stale
const TTL_SECS: u64 = 5;

/// Cache key: (bus_name, object_path, max_depth)
type CacheKey = (String, String, u32);

/// Cache entry: tree nodes + insertion time
struct CacheEntry {
    nodes: Vec<A11yNode>,
    inserted_at: Instant,
}

/// Global tree cache (process-wide singleton)
static TREE_CACHE: LazyLock<Mutex<HashMap<CacheKey, CacheEntry>>> =
    LazyLock::new(|| Mutex::new(HashMap::new()));

/// Look up a cached tree. Returns None if not found or expired.
pub fn get(bus_name: &str, path: &str, max_depth: u32) -> Option<Vec<A11yNode>> {
    let cache = TREE_CACHE.lock().ok()?;
    let key = (bus_name.to_string(), path.to_string(), max_depth);
    let entry = cache.get(&key)?;

    if entry.inserted_at.elapsed() < Duration::from_secs(TTL_SECS) {
        Some(entry.nodes.clone())
    } else {
        None // expired
    }
}

/// Insert a tree into the cache.
pub fn put(bus_name: &str, path: &str, max_depth: u32, nodes: Vec<A11yNode>) {
    if let Ok(mut cache) = TREE_CACHE.lock() {
        let key = (bus_name.to_string(), path.to_string(), max_depth);
        cache.insert(key, CacheEntry {
            nodes,
            inserted_at: Instant::now(),
        });
    }
}

/// Invalidate all cache entries for a specific bus_name.
/// Called when window changes are detected via events::detect_changes.
pub fn invalidate_bus(bus_name: &str) {
    if let Ok(mut cache) = TREE_CACHE.lock() {
        cache.retain(|k, _| k.0 != bus_name);
    }
}

/// Clear the entire cache.
pub fn clear() {
    if let Ok(mut cache) = TREE_CACHE.lock() {
        cache.clear();
    }
}

/// Evict expired entries (housekeeping).
pub fn evict_expired() {
    if let Ok(mut cache) = TREE_CACHE.lock() {
        let ttl = Duration::from_secs(TTL_SECS);
        cache.retain(|_, v| v.inserted_at.elapsed() < ttl);
    }
}

/// Current cache size (for diagnostics).
pub fn len() -> usize {
    TREE_CACHE.lock().map(|c| c.len()).unwrap_or(0)
}
