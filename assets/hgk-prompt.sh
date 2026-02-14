#!/bin/bash
# Hegemonikón Terminal Prompt
# SOURCE this file from .bashrc: source ~/oikos/hegemonikon/assets/hgk-prompt.sh

# === HGK 6-Series Colors ===
# Flow (teal), Value (amber), Function (violet), Scale (blue), Valence (rose), Precision (silver)
C_FLOW='\[\033[38;2;94;186;187m\]'     # #5EBABB
C_VALUE='\[\033[38;2;224;175;104m\]'    # #E0AF68
C_FUNC='\[\033[38;2;158;134;200m\]'     # #9E86C8
C_SCALE='\[\033[38;2;122;162;247m\]'    # #7AA2F7
C_VALENCE='\[\033[38;2;219;141;150m\]'  # #DB8D96
C_PREC='\[\033[38;2;192;202;215m\]'     # #C0CAD7
C_DIM='\[\033[38;2;88;91;112m\]'        # #585B70
C_RESET='\[\033[0m\]'
C_BOLD='\[\033[1m\]'

# === HGK Status Function ===
__hgk_status() {
    local git_branch=""
    if git rev-parse --is-inside-work-tree &>/dev/null; then
        git_branch=$(git symbolic-ref --short HEAD 2>/dev/null || git describe --tags --exact-match 2>/dev/null || git rev-parse --short HEAD)
    fi

    # Project detection
    local project=""
    case "$PWD" in
        */hegemonikon*) project="⬡ HGK" ;;
        */oikos*)       project="⌂ Oikos" ;;
        *)              project="◇" ;;
    esac

    echo "$project|$git_branch"
}

# === Prompt Construction ===
# Structure: [Ω] project │ path │ branch ❯
__hgk_prompt() {
    local last_status=$?
    local info=$(__hgk_status)
    local project=$(echo "$info" | cut -d'|' -f1)
    local branch=$(echo "$info" | cut -d'|' -f2)

    # Error indicator
    local indicator="❯"
    if [ $last_status -ne 0 ]; then
        indicator="${C_VALENCE}✗${C_RESET}"
    fi

    # Build prompt
    PS1=""
    PS1+="${C_DIM}╭─${C_RESET}"
    PS1+="${C_FLOW}${C_BOLD} ${project} ${C_RESET}"
    PS1+="${C_DIM}│${C_RESET} "
    PS1+="${C_VALUE}\W${C_RESET}"

    if [ -n "$branch" ]; then
        PS1+=" ${C_DIM}│${C_RESET} ${C_FUNC}${branch}${C_RESET}"
    fi

    PS1+="\n"
    PS1+="${C_DIM}╰─${C_RESET} ${indicator} "
}

PROMPT_COMMAND=__hgk_prompt
