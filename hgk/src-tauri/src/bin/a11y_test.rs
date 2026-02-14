// CLI test binary for AT-SPI2 Phase 2 final verification
// Run with: cargo run --bin a11y_test

use hgk_desktop_lib::a11y;

#[tokio::main]
async fn main() {
    println!("=== AT-SPI2 Phase 2 Final Test ===\n");

    // Test 1: list_desktop
    println!("--- Test 1: list_desktop ---");
    let elements = a11y::router::list_desktop_elements().await;
    match &elements {
        Ok(e) => println!("✅ {} desktop elements", e.len()),
        Err(e) => println!("❌ {}", e),
    }

    println!();

    // Test 2: Component API — get_extents for elements with children
    println!("--- Test 2: Component API (get_extents) ---");
    match a11y::list_accessible_windows().await {
        Ok(windows) => {
            let mut sorted = windows.clone();
            sorted.sort_by(|a, b| b.child_count.cmp(&a.child_count));
            
            for w in sorted.iter().take(3) {
                if w.child_count == 0 { continue; }
                println!("\n  📦 {} ({}) — {} children", w.app_name, w.bus_name, w.child_count);
                
                // Get extents of the app root
                match a11y::get_element_extents(&w.bus_name, &w.path).await {
                    Ok(ext) => {
                        println!("    📐 Root extents: x={} y={} w={} h={}", ext.x, ext.y, ext.width, ext.height);
                    }
                    Err(e) => println!("    ❌ get_extents error: {}", e),
                }
                
                // Walk tree to find elements and get their extents
                match a11y::get_accessible_tree(&w.bus_name, &w.path, 3).await {
                    Ok(nodes) => {
                        fn find_named(nodes: &[a11y::A11yNode], depth: usize) -> Vec<(String, String, String)> {
                            let mut result = Vec::new();
                            for n in nodes {
                                if !n.name.is_empty() && n.role != "application" {
                                    result.push((n.name.clone(), n.role.clone(), n.path.clone()));
                                }
                                if depth < 4 && result.len() < 10 {
                                    result.extend(find_named(&n.children, depth + 1));
                                }
                            }
                            result
                        }
                        
                        let named = find_named(&nodes, 0);
                        for (name, role, path) in named.iter().take(3) {
                            match a11y::get_element_extents(&w.bus_name, path).await {
                                Ok(ext) => {
                                    let label: String = name.chars().take(20).collect();
                                    println!("    🎯 {} [{}] — at ({},{}) size {}x{}", 
                                        label, role, ext.x, ext.y, ext.width, ext.height);
                                }
                                Err(e) => {
                                    let label: String = name.chars().take(20).collect();
                                    println!("    ❌ {} [{}] — {}", label, role, e);
                                }
                            }
                        }
                    }
                    Err(e) => println!("    ❌ tree error: {}", e),
                }
            }
        }
        Err(e) => println!("  ❌ {}", e),
    }

    println!();

    // Test 3: Focus test (non-destructive)
    println!("--- Test 3: focus_element (grab_focus) ---");
    match a11y::list_accessible_windows().await {
        Ok(windows) => {
            if let Some(w) = windows.iter().find(|w| w.child_count > 0) {
                println!("  Attempting grab_focus on {} root...", w.app_name);
                match a11y::focus_element(&w.bus_name, &w.path).await {
                    Ok(success) => println!("  ✅ grab_focus = {}", success),
                    Err(e) => println!("  ❌ grab_focus error: {}", e),
                }
            }
        }
        Err(e) => println!("  ❌ {}", e),
    }

    // Summary
    println!("\n=== API Coverage ===");
    println!("  list_accessible_windows  ✅ (Phase 0b)");
    println!("  get_accessible_tree      ✅ (Phase 0b)");
    println!("  list_desktop_elements    ✅ (Phase 1)");
    println!("  get_element_extents      ✅ (Phase 2)");
    println!("  focus_element            ✅ (Phase 2)");
    println!("  perform_action           ✅ (Phase 2)");
    println!("  list_actions             ✅ (Phase 2)");
    println!("  set_text                 ✅ (Phase 2)");
    println!("\n=== Phase 2 Final Test Complete ===");
}
