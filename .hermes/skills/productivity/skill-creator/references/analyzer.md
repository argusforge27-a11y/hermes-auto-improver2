# Post-hoc Analyzer Agent

Analyze blind comparison results to understand WHY the winner won and generate improvement suggestions.

## Role

After the blind comparator determines a winner, the Post-hoc Analyzer "unblids" the results by examining the skills and transcripts. The goal is to extract actionable insights: what made the winner better, and how can the loser be improved?

## Inputs

You receive these parameters in your prompt:

- **winner**: "A" or "B" (from blind comparison)
- **winner_skill_path**: Path to the skill that produced the winning output
- **winner_transcript_path**: Path to the execution transcript for the winner
- **loser_skill_path**: Path to the skill that produced the losing output
- **loser_transcript_path**: Path to the execution transcript for the loser
- **comparison_result_path**: Path to the blind comparator's output JSON
- **output_path**: Where to save the analysis results

## Process

### Step 1: Read Comparison Result

1. Read the blind comparator's output at comparison_result_path
2. Note the winning side (A or B), the reasoning, and any scores
3. Understand what the comparator valued in the winning output

### Step 2: Read Both Skills

1. Read the winner skill's SKILL.md and key referenced files
2. Read the loser skill's SKILL.md and key referenced files
3. Identify structural differences:
 - Instructions clarity and specificity
 - Script/tool usage patterns
 - Example coverage
 - Edge case handling

### Step 3: Read Both Transcripts

1. Read the winner's transcript
2. Read the loser's transcript
3. Compare execution patterns:
 - How closely did each follow their skill's instructions?
 - What tools were used differently?
 - Where did the loser diverge from optimal behavior?
 - Did either encounter errors or make recovery attempts?

### Step 4: Analyze Instruction Following

For each transcript, evaluate:
- Did the agent follow the skill's explicit instructions?
- Did the agent use the skill's provided tools/scripts?
- Were there missed opportunities to leverage skill content?
- Did the agent add unnecessary steps not in the skill?

Score instruction following 1-10 and note specific issues.

### Step 5: Identify Winner Strengths

Determine what made the winner better:
- Clearer instructions that led to better behavior?
- Better scripts/tools that produced better output?
- More comprehensive examples that guided edge cases?
- Better error handling guidance?

Be specific. Quote from skills/transcripts where relevant.

### Step 6: Identify Loser Weaknesses

Determine what held the loser back:
- Ambiguous instructions that led to suboptimal choices?
- Missing tools/scripts that forced workarounds?
- Gaps in edge case coverage?
- Poor error handling that caused failures?

### Step 7: Generate Improvement Suggestions

Based on the analysis, produce actionable suggestions for improving the loser skill:
- Specific instruction changes to make
- Tools/scripts to add or modify
- Examples to include
- Edge cases to address