# Gnōsis Auto-Collect Script
# 自動収集スクリプト（ローテーション実行）

param(
    [int]$Limit = 50,
    [switch]$All,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$HEGEMONIKON_ROOT = "M:\Hegemonikon"
$CLI_PATH = "$HEGEMONIKON_ROOT\mekhane\anamnesis\cli.py"
$TOPICS_PATH = "$HEGEMONIKON_ROOT\mekhane\anamnesis\gnosis_topics.yaml"
$STATE_PATH = "$HEGEMONIKON_ROOT\gnosis_data\collection_state.json"

# Load topics
$topicsYaml = Get-Content $TOPICS_PATH -Raw
# Simple YAML parsing for queries
$queries = @(
    "LLM autonomous agent architecture",
    "Long-context memory management for LLM",
    "Active Inference in artificial intelligence",
    "Embodied cognition in Large Language Models",
    "Structured prompting languages for LLM",
    "Chain-of-Thought reasoning optimization",
    "Tool use and function calling in LLMs",
    "LLM integration in software development environment",
    "Self-correction and verification in LLM agents",
    "Evaluating autonomous agent performance"
)

# Load state
$state = @{ last_index = 0; last_collected = $null }
if (Test-Path $STATE_PATH) {
    $state = Get-Content $STATE_PATH | ConvertFrom-Json
}

Write-Host "`n[Hegemonikon] Gnosis Auto-Collect" -ForegroundColor Cyan
Write-Host "================================="

if ($All) {
    # Collect all topics
    Write-Host "Mode: Collect ALL topics ($($queries.Count) queries)"
    foreach ($query in $queries) {
        Write-Host "`n>> Collecting: $query" -ForegroundColor Yellow
        if (-not $DryRun) {
            python $CLI_PATH collect-all -q $query -l $Limit
        }
        else {
            Write-Host "   [DRY RUN] Would collect: $query"
        }
    }
}
else {
    # Rotation: collect next topic
    $index = $state.last_index
    $query = $queries[$index]
    
    Write-Host "Mode: Rotation (Topic $($index + 1)/$($queries.Count))"
    Write-Host "Query: $query" -ForegroundColor Yellow
    
    if (-not $DryRun) {
        python $CLI_PATH collect-all -q $query -l $Limit
        
        # Update state
        $state.last_index = ($index + 1) % $queries.Count
        $state.last_collected = (Get-Date).ToString("o")
        
        # Ensure directory exists
        $stateDir = Split-Path $STATE_PATH -Parent
        if (-not (Test-Path $stateDir)) {
            New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
        }
        $state | ConvertTo-Json | Set-Content $STATE_PATH
    }
    else {
        Write-Host "[DRY RUN] Would collect and update state"
    }
}

Write-Host "`n[Hegemonikon] Collection complete" -ForegroundColor Green
