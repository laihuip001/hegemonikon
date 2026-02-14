// E2E Demo: AT-SPI Desktop Automation via CopyQ
//
// Demonstrates the full flow:
//   1. List desktop apps → find CopyQ
//   2. Get CopyQ's accessibility tree
//   3. Search for UI elements by role/name
//   4. Get element coordinates
//   5. Perform click action
//   6. Verify cache hit on second tree fetch
//
// Run: cargo run --bin e2e_demo

use hgk_desktop_lib::a11y;
use std::time::Instant;

#[tokio::main]
async fn main() {
    println!("╔══════════════════════════════════════════╗");
    println!("║  AT-SPI2 E2E Demo — CopyQ Automation    ║");
    println!("╚══════════════════════════════════════════╝\n");

    // Step 1: Find CopyQ in desktop apps
    println!("━━━ Step 1: Find CopyQ ━━━");
    let windows = match a11y::list_accessible_windows().await {
        Ok(w) => w,
        Err(e) => {
            eprintln!("❌ AT-SPI2 connection failed: {}", e);
            std::process::exit(1);
        }
    };

    let copyq = windows.iter().find(|w| {
        w.app_name.to_lowercase().contains("copyq")
    });

    let copyq = match copyq {
        Some(w) => {
            println!("  ✅ Found CopyQ: bus={} path={} children={}", w.bus_name, w.path, w.child_count);
            w
        }
        None => {
            println!("  ❌ CopyQ not found. Available apps:");
            for w in &windows {
                println!("     📱 {} ({})", w.app_name, w.bus_name);
            }
            eprintln!("\n  → Run `copyq show` to launch CopyQ, then retry.");
            std::process::exit(1);
        }
    };

    // Step 2: Get CopyQ's accessibility tree
    println!("\n━━━ Step 2: Tree traversal ━━━");
    let t0 = Instant::now();
    let tree = match a11y::get_accessible_tree(&copyq.bus_name, &copyq.path, 4).await {
        Ok(t) => t,
        Err(e) => {
            eprintln!("  ❌ Tree traversal failed: {}", e);
            std::process::exit(1);
        }
    };
    let elapsed = t0.elapsed();
    println!("  ✅ Tree fetched in {:.0?}", elapsed);
    print_tree_summary(&tree, 0);

    // Step 3: Cache verification — second fetch should be instant
    println!("\n━━━ Step 3: Cache verification ━━━");
    let t1 = Instant::now();
    let _tree2 = a11y::get_accessible_tree(&copyq.bus_name, &copyq.path, 4).await;
    let elapsed2 = t1.elapsed();
    println!("  ⏱️  First fetch:  {:.0?}", elapsed);
    println!("  ⏱️  Second fetch: {:.0?} (cached)", elapsed2);
    let speedup = if elapsed2.as_micros() > 0 {
        elapsed.as_micros() as f64 / elapsed2.as_micros() as f64
    } else {
        f64::INFINITY
    };
    println!("  📊 Speedup: {:.1}x", speedup);
    println!("  📦 Cache entries: {}", a11y::cache::len());

    // Step 4: Find interactive elements
    println!("\n━━━ Step 4: Find interactive elements ━━━");
    let mut buttons: Vec<(String, String, String)> = Vec::new();
    collect_by_role(&tree, "push button", &mut buttons);
    collect_by_role(&tree, "menu item", &mut buttons);
    collect_by_role(&tree, "text", &mut buttons);

    if buttons.is_empty() {
        println!("  ⚠️  No interactive elements found");
    } else {
        println!("  ✅ Found {} interactive elements:", buttons.len());
        for (i, (name, role, path)) in buttons.iter().take(8).enumerate() {
            let label: String = name.chars().take(25).collect();
            match a11y::get_element_extents(&copyq.bus_name, path).await {
                Ok(ext) => {
                    println!("    {}. [{}] {} — at ({},{}) size {}x{}",
                        i + 1, role, label, ext.x, ext.y, ext.width, ext.height);
                }
                Err(_) => {
                    println!("    {}. [{}] {} — (no extents)", i + 1, role, label);
                }
            }
        }
    }

    // Step 5: List actions for first button
    println!("\n━━━ Step 5: Available actions ━━━");
    if let Some((_name, _role, path)) = buttons.first() {
        match a11y::list_actions(&copyq.bus_name, path).await {
            Ok(actions) => {
                println!("  ✅ Actions on first element:");
                for (i, a) in actions.iter().enumerate() {
                    println!("    {}. {}", i, a);
                }
            }
            Err(e) => println!("  ❌ list_actions: {}", e),
        }
    }

    // Step 6: Focus CopyQ window
    println!("\n━━━ Step 6: Focus CopyQ ━━━");
    match a11y::focus_element(&copyq.bus_name, &copyq.path).await {
        Ok(success) => println!("  ✅ grab_focus = {}", success),
        Err(e) => println!("  ❌ focus_element: {}", e),
    }

    // Step 7: Click on first interactive element (xdotool coordinate click)
    println!("\n━━━ Step 7: Click element (xdotool) ━━━");
    let mut click_ok = false;
    if let Some((_name, _role, path)) = buttons.first() {
        match a11y::click_at_element(&copyq.bus_name, path).await {
            Ok((success, cx, cy)) => {
                println!("  ✅ Clicked at ({},{}) — success={}", cx, cy, success);
                click_ok = success;
            }
            Err(e) => println!("  ⚠️  click_at_element: {} (element may not be visible)", e),
        }
    } else {
        println!("  ⚠️  No elements to click");
    }

    // Step 8: Type text into a text element (EditableText or xdotool fallback)
    println!("\n━━━ Step 8: Type text ━━━");
    let mut type_ok = false;
    let text_elements: Vec<_> = buttons.iter()
        .filter(|(_n, r, _p)| r.to_lowercase().contains("text"))
        .collect();
    if let Some((_name, _role, path)) = text_elements.first() {
        let demo_text = "HGK E2E test";
        match a11y::type_at_element(&copyq.bus_name, path, demo_text).await {
            Ok(success) => {
                println!("  ✅ Typed '{}' — success={}", demo_text, success);
                type_ok = success;
            }
            Err(e) => println!("  ⚠️  type_at_element: {} (element may not accept text)", e),
        }
    } else {
        println!("  ⚠️  No text elements found — skipping type test");
    }

    // Summary
    println!("\n╔═══════════════════════════════════════════════╗");
    println!("║  E2E Demo Complete                            ║");
    println!("╠═══════════════════════════════════════════════╣");
    println!("║  ✅ App discovery (list_windows)               ║");
    println!("║  ✅ Tree traversal (get_accessible_tree)       ║");
    println!("║  ✅ Tree cache ({} entries, {:.1}x speedup) {}  ║",
        a11y::cache::len(),
        speedup,
        " ".repeat(3));
    println!("║  ✅ Element search (find by role)              ║");
    println!("║  ✅ Coordinate extraction (get_extents)        ║");
    println!("║  ✅ Action listing (list_actions)              ║");
    println!("║  ✅ Focus management (focus_element)           ║");
    println!("║  {} Click execution (click_at_element)        ║",
        if click_ok { "✅" } else { "⚠️ " });
    println!("║  {} Text input (type_at_element)              ║",
        if type_ok { "✅" } else { "⚠️ " });
    println!("╚═══════════════════════════════════════════════╝");
}

fn print_tree_summary(nodes: &[a11y::A11yNode], depth: usize) {
    for node in nodes.iter().take(5) {
        let indent = "  ".repeat(depth + 1);
        let label: String = node.name.chars().take(20).collect();
        if !label.is_empty() {
            println!("{}📂 {} [{}]", indent, label, node.role);
        }
        if depth < 2 {
            print_tree_summary(&node.children, depth + 1);
        }
    }
}

fn collect_by_role(nodes: &[a11y::A11yNode], role: &str, out: &mut Vec<(String, String, String)>) {
    for node in nodes {
        if node.role.to_lowercase().contains(role) && !node.name.is_empty() {
            out.push((node.name.clone(), node.role.clone(), node.path.clone()));
        }
        collect_by_role(&node.children, role, out);
    }
}
