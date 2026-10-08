"""Business logic. Routers stay thin and call into these modules:

    errors        GameError (a rule was broken -> HTTP status + machine-readable code)
    rules         tunable game constants
    clock         the learner's "today", streak and daily-XP helpers
    hearts        lose / gain / lazily regenerate hearts
    answers       answer normalisation, typo tolerance, match-pair tokens, exercise payloads
    path          unlock rules, the learning path (skills, chests, trophies), practice pools
    achievements  metrics + badge unlocking
    sessions      start / answer / pair / complete / abandon a study session
    users         the learner snapshot returned to the client, demo-data reset
    social        leaderboard, profile, daily quests
"""
