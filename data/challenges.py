import random

# Challenge database
ALL_CHALLENGES = [
    # Communication Boosters
    {
        "id": "comm_1",
        "category": "Communication Boosters",
        "title": "Question Time",
        "description": "Take turns asking each other three intimate questions you've never asked before. Listen attentively without interrupting.",
        "difficulty": "Easy"
    },
    {
        "id": "comm_2",
        "category": "Communication Boosters",
        "title": "Technology-Free Evening",
        "description": "Spend an entire evening without phones, TV, or other technology. Focus solely on conversing and connecting with each other.",
        "difficulty": "Medium"
    },
    {
        "id": "comm_3",
        "category": "Communication Boosters",
        "title": "Appreciation Exchange",
        "description": "Write down three things you genuinely appreciate about your partner that you haven't expressed recently. Share them and discuss how those qualities impact your relationship.",
        "difficulty": "Easy"
    },
    {
        "id": "comm_4",
        "category": "Communication Boosters",
        "title": "Active Listening Practice",
        "description": "Choose a topic that matters to your partner. Practice active listening for 10 minutes without formulating responses while they speak, then repeat back what you heard before responding.",
        "difficulty": "Medium"
    },
    {
        "id": "comm_5",
        "category": "Communication Boosters",
        "title": "Needs & Desires Conversation",
        "description": "Have an honest conversation about one unfulfilled need or desire you each have in your relationship, using 'I' statements and avoiding blame.",
        "difficulty": "Hard"
    },
    
    # Physical Touch & Affection
    {
        "id": "touch_1",
        "category": "Physical Touch & Affection",
        "title": "15-Minute Massage Exchange",
        "description": "Take turns giving each other a 15-minute massage, focusing on areas where your partner holds tension. Use gentle touches and ask for feedback.",
        "difficulty": "Easy"
    },
    {
        "id": "touch_2",
        "category": "Physical Touch & Affection",
        "title": "Hand Tracing Intimacy",
        "description": "Sit facing each other. Take turns slowly tracing your partner's hands with your fingertips, maintaining eye contact. Focus on the sensation and connection.",
        "difficulty": "Easy"
    },
    {
        "id": "touch_3",
        "category": "Physical Touch & Affection",
        "title": "Morning Embrace",
        "description": "Before getting out of bed tomorrow morning, hold each other in a full-body embrace for two full minutes. Notice your breathing and heartbeats.",
        "difficulty": "Easy"
    },
    {
        "id": "touch_4",
        "category": "Physical Touch & Affection",
        "title": "Blindfolded Exploration",
        "description": "Blindfold your partner and spend 10 minutes exploring their face and neck with your fingertips, then switch roles. Discuss the experience afterward.",
        "difficulty": "Medium"
    },
    {
        "id": "touch_5",
        "category": "Physical Touch & Affection",
        "title": "Dancing Connection",
        "description": "Put on a slow song and dance together in close embrace. Focus on leading and following, and the points where your bodies connect.",
        "difficulty": "Medium"
    },
    
    # Creative Date Night Ideas
    {
        "id": "date_1",
        "category": "Creative Date Night Ideas",
        "title": "Memory Lane Dinner",
        "description": "Recreate your first date as closely as possible — same restaurant or meal, similar clothes, and reminisce about your early relationship.",
        "difficulty": "Medium"
    },
    {
        "id": "date_2",
        "category": "Creative Date Night Ideas",
        "title": "Stargazing Adventure",
        "description": "Find a spot away from city lights, bring blankets and hot drinks, and spend an evening stargazing while sharing dreams and hopes for the future.",
        "difficulty": "Easy"
    },
    {
        "id": "date_3",
        "category": "Creative Date Night Ideas",
        "title": "DIY Paint Night",
        "description": "Set up canvases side by side and paint portraits of each other. No artistic talent required — it's about fun and seeing each other's perspective.",
        "difficulty": "Medium"
    },
    {
        "id": "date_4",
        "category": "Creative Date Night Ideas",
        "title": "Childhood Games Night",
        "description": "Each partner chooses a favorite game from childhood. Spend the evening playing these games and sharing memories from your early years.",
        "difficulty": "Easy"
    },
    {
        "id": "date_5",
        "category": "Creative Date Night Ideas",
        "title": "Mystery Taste Testing",
        "description": "Blindfold each other and take turns feeding small bites of different foods. Try to guess what you're tasting. Include a mix of familiar and exotic items.",
        "difficulty": "Medium"
    },
    
    # Sexual Exploration
    {
        "id": "sex_1",
        "category": "Sexual Exploration",
        "title": "Desire Mapping",
        "description": "Draw outlines of your bodies on paper. Take turns marking erogenous zones and discussing how you like to be touched in each area.",
        "difficulty": "Medium"
    },
    {
        "id": "sex_2",
        "category": "Sexual Exploration",
        "title": "Fantasy Sharing",
        "description": "Share a sexual fantasy you've never told your partner before. Listen without judgment, then discuss elements that interest you both.",
        "difficulty": "Hard"
    },
    {
        "id": "sex_3",
        "category": "Sexual Exploration",
        "title": "Sensory Focus",
        "description": "Spend intimate time together focusing solely on touch and sensation, without the goal of climax. Take turns being the giver and receiver of pleasure.",
        "difficulty": "Medium"
    },
    {
        "id": "sex_4",
        "category": "Sexual Exploration",
        "title": "Intimate Q&A",
        "description": "Take turns asking each other questions about desires, preferences, and boundaries. Use this as an opportunity to learn something new about your partner's sexuality.",
        "difficulty": "Medium"
    },
    {
        "id": "sex_5",
        "category": "Sexual Exploration",
        "title": "Pleasure Mapping",
        "description": "Use the PlayLoveToys pleasure mapping guide to identify and explore new erogenous zones with your partner. Communicate openly about what feels good.",
        "difficulty": "Medium"
    },
    
    # Emotional Connection
    {
        "id": "emotion_1",
        "category": "Emotional Connection",
        "title": "Gratitude Practice",
        "description": "Share three things you're grateful for about your relationship that have happened in the past week. Be specific and authentic.",
        "difficulty": "Easy"
    },
    {
        "id": "emotion_2",
        "category": "Emotional Connection",
        "title": "Vulnerability Exchange",
        "description": "Take turns sharing something you feel vulnerable about in your life right now. Practice supportive listening without trying to fix or solve.",
        "difficulty": "Hard"
    },
    {
        "id": "emotion_3",
        "category": "Emotional Connection",
        "title": "Shared Goals Visualization",
        "description": "Discuss where you see yourselves in 5 years. Create a list of shared goals and dreams for your relationship's future.",
        "difficulty": "Medium"
    },
    {
        "id": "emotion_4",
        "category": "Emotional Connection",
        "title": "Love Languages Check-in",
        "description": "Discuss your primary love languages and one specific way your partner can express love to you this week that would be meaningful.",
        "difficulty": "Medium"
    },
    {
        "id": "emotion_5",
        "category": "Emotional Connection",
        "title": "Relationship Timeline",
        "description": "Create a timeline of your relationship highlighting significant moments — both joyful and challenging. Reflect on how you've grown together through each phase.",
        "difficulty": "Medium"
    }
]

def get_challenge_by_id(challenge_id):
    """Retrieve a challenge by its ID"""
    for challenge in ALL_CHALLENGES:
        if challenge["id"] == challenge_id:
            return challenge
    return None

def get_challenge_by_category(category, exclude_ids=None, return_all=False):
    """
    Get a random challenge from a specific category, optionally excluding certain IDs.
    If return_all is True, returns all challenges in the category instead of a random one.
    """
    if exclude_ids is None:
        exclude_ids = []
    
    # Filter challenges by category and not in exclude list
    available_challenges = [
        c for c in ALL_CHALLENGES 
        if c["category"] == category and c["id"] not in exclude_ids
    ]
    
    # Return all challenges or a random one
    if return_all:
        return available_challenges
    elif available_challenges:
        return random.choice(available_challenges)
    return None

def get_challenges_by_category(category):
    """Get all challenges in a specific category"""
    return [c for c in ALL_CHALLENGES if c["category"] == category]

def get_random_challenge(exclude_ids=None):
    """Get a completely random challenge, optionally excluding certain IDs"""
    if exclude_ids is None:
        exclude_ids = []
    
    available_challenges = [c for c in ALL_CHALLENGES if c["id"] not in exclude_ids]
    
    if available_challenges:
        return random.choice(available_challenges)
    return None
