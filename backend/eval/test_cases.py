TEST_CASES = [
    {
        "name": "Preference recall",
        "system_prompt": "Act as an assistant.",
        "turns": [
            "My favorite editor is Neovim and I prefer concise answers.",
            "We are discussing memory systems for AI agents.",
            "What is my preferred editor and how should you answer?",
        ],
        "expect": ["Neovim", "concise"],
        "dimension": "recall",
    },
    {
        "name": "Personality stability",
        "system_prompt": "Act as an assistant.",
        "turns": [
            "I like calm, concise answers with no hype.",
            "We are still discussing the same project.",
            "Reply in the style I asked for and mention that style explicitly.",
        ],
        "expect": ["calm", "concise"],
        "dimension": "personality",
    },
    {
        "name": "Rule stability",
        "system_prompt": "Act as an assistant.",
        "turns": [
            "Always format code examples in fenced code blocks.",
            "Summarize how you should present code.",
        ],
        "expect": ["fenced", "code"],
        "dimension": "consistency",
    },
    {
        "name": "Knowledge accumulation",
        "system_prompt": "Act as an assistant.",
        "turns": [
            "Project Atlas launches on May 14.",
            "The owner of Project Atlas is Team Orion.",
            "Tell me the launch date and owner for Project Atlas.",
        ],
        "expect": ["May 14", "Team Orion"],
        "dimension": "knowledge",
    },
    {
        "name": "Noise forgetting",
        "system_prompt": "Act as an assistant.",
        "turns": [
            "Remember only this important fact: the deployment code is Atlas-42.",
            "Noise item one about coffee.",
            "Noise item two about weather.",
            "Noise item three about traffic.",
            "What is the deployment code?",
        ],
        "expect": ["Atlas-42"],
        "dimension": "forgetting",
    },
]
