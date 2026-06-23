"""
All prompt templates for outreach generation.
Isolated from business logic.
"""

SYSTEM_PROMPT = """\
You are an elite recruitment copywriter specializing in candidate 
outreach that consistently earns replies from highly qualified candidates.

Your job is to write personalized outreach messages that feel human, 
relevant, respectful, and compelling.

Strict rules:
- Sound human — never templated
- Reference candidate's specific details (name, role, company, skills)
- One CTA only per message
- Lead with opportunity, not desperation
- Never use: rockstar, ninja, superstar, passionate, game-changing,
  exciting opportunity, "I hope this finds you well"
- Connection notes: curiosity-driven, no pitch, under 300 characters
- Follow-ups: add value, never beg, never guilt-trip
- Adapt style completely based on platform and tone\
"""

OUTREACH_PROMPT = """\
Generate a complete outreach package for this candidate.

Candidate Details:
- Name: {candidate_name}
- Current Role: {current_role}
- Current Company: {current_company}
- Key Skills: {skills}

Recruiting For: {target_job}
Tone: {tone}
Platform: {platform}
Tone instruction: {tone_instruction}
Platform instruction: {platform_instruction}

Return EXACTLY in this format — no extra commentary:

## Connection Note
[Max 300 characters. Curiosity-driven. No pitch.]

## Outreach Message
[150-200 words. Personalized opening. Why they fit. One CTA.]

## Follow-Up Message
[Day 4, no response. Short. Add value. Not pushy.]

## Subject Lines
[5 subject line options — email style, even if platform is LinkedIn]

## Personalization Score
[Score XX/100 with one-line reasoning]

## Spam Risk
[Low/Medium/High with specific flags if any]\
"""

VARIATION_PROMPT = """\
Generate {variation_label} of this outreach package using a different 
psychological angle than the original.

Candidate: {candidate_name} — {current_role} at {current_company}
Skills: {skills}
Recruiting for: {target_job}
Tone: {tone}
Platform: {platform}

Use a distinct angle: social proof, curiosity, direct value, 
FOMO, or peer comparison — whichever wasn't used in the original.

Return same format:
## Connection Note
## Outreach Message  
## Follow-Up Message\
"""

TONE_INSTRUCTIONS = {
    "Professional": "formal, polished, respectful — appropriate for senior roles",
    "Casual": "conversational, warm, friendly — like a smart colleague reaching out",
    "LinkedIn-native": "short, punchy, native to LinkedIn culture — no corporate speak"
}

PLATFORM_INSTRUCTIONS = {
    "LinkedIn": "Keep connection note under 300 chars. Messages should feel native to LinkedIn culture.",
    "Email": "Include subject lines. Messages can be slightly longer and more formal.",
    "WhatsApp": "Very short and conversational. Maximum 3-4 sentences per message."
}