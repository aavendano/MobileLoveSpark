"""
AI-powered challenge generator utility.
Uses Google's Gemini API for generating relationship challenges
with cost optimization strategies built in.
"""

import os
import json
import random
import hashlib
import datetime
from typing import Dict, List, Optional, Any

import google.generativeai as genai

# Configure the Google API with the key from environment
API_KEY = os.environ.get("GOOGLE_API_KEY")

# Helper function to handle different versions of the Google AI library
def init_gemini():
    """Initialize Google Gemini API based on available library version"""
    if not API_KEY:
        return False
        
    try:
        # Try the newer syntax
        genai.configure(api_key=API_KEY)
        return True
    except (AttributeError, TypeError):
        try:
            # Try older syntax or alternative approach
            genai.api_key = API_KEY
            return True
        except Exception as e:
            print(f"Failed to initialize Google AI: {str(e)}")
            return False

# Initialize the API
AI_AVAILABLE = init_gemini()

# Cache for storing generated challenges to reduce API calls
# Structure: {cache_key: {"timestamp": datetime, "challenges": [list_of_challenges]}}
CHALLENGE_CACHE = {}
CACHE_LIFETIME = datetime.timedelta(days=30)  # Cache lifetime - 30 days

# Categories
CATEGORIES = [
    "Communication Boosters",
    "Physical Touch & Affection",
    "Creative Date Night Ideas", 
    "Sexual Exploration",
    "Emotional Connection"
]

# Difficulty levels
DIFFICULTY_LEVELS = ["easy", "medium", "hard"]

def get_cache_key(user_profile: Dict[str, Any], category: Optional[str] = None) -> str:
    """
    Create a deterministic cache key based on relevant user profile data
    and optionally a specific category.
    """
    # We only include non-identifying profile elements that affect challenge generation
    cache_data = {
        "relationship_status": user_profile.get("relationship_status", ""),
        "relationship_duration": user_profile.get("relationship_duration", ""),
        "category": category
    }
    # Create a consistent cache key
    cache_str = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(cache_str.encode()).hexdigest()

def check_cache(cache_key: str) -> List[Dict[str, Any]]:
    """Check if we have valid cached challenges for this profile/category."""
    if cache_key in CHALLENGE_CACHE:
        cache_entry = CHALLENGE_CACHE[cache_key]
        cache_time = cache_entry.get("timestamp")
        now = datetime.datetime.now()
        
        # If cache is still valid and has challenges
        if (now - cache_time < CACHE_LIFETIME) and cache_entry.get("challenges"):
            return cache_entry.get("challenges", [])
    
    return []

def store_in_cache(cache_key: str, challenges: List[Dict[str, Any]]) -> None:
    """Store generated challenges in the cache."""
    CHALLENGE_CACHE[cache_key] = {
        "timestamp": datetime.datetime.now(),
        "challenges": challenges
    }

def should_use_ai(user_profile: Dict[str, Any], completed_challenges: List[str], 
                 available_challenges: List[str], category: Optional[str] = None) -> bool:
    """
    Determine if we should use AI to generate a challenge based on various factors
    to optimize API usage and costs.
    """
    # If user has completed most available challenges in this category
    if category and len(available_challenges) > 0:
        completion_ratio = len(completed_challenges) / len(available_challenges)
        if completion_ratio > 0.7:  # If user has completed 70% of available challenges
            return True
    
    # Generate special AI challenges on milestone days
    streak = user_profile.get("streak", 0)
    if streak in [7, 14, 30, 50, 100]:  # Milestones
        return True
    
    # If user has completed many challenges total
    total_completed = user_profile.get("total_completed", 0)
    if total_completed > 0 and total_completed % 10 == 0:  # Every 10 challenges
        return True
    
    # Otherwise, stick with pre-defined challenges
    return False

def generate_challenge_prompt(user_profile: Dict[str, Any], category: Optional[str] = None) -> str:
    """Generate an appropriate prompt for the AI based on user profile and category."""
    partner1 = user_profile.get("partner1_name", "Partner 1")
    partner2 = user_profile.get("partner2_name", "Partner 2") 
    rel_status = user_profile.get("relationship_status", "dating")
    rel_duration = user_profile.get("relationship_duration", "")
    
    prompt = f"""Generate a unique relationship challenge for a couple.

Relationship Context:
- Partner names: {partner1} and {partner2}
- Relationship status: {rel_status}
- Relationship duration: {rel_duration}
"""

    if category:
        prompt += f"- Challenge category: {category}\n"
        
        # Add category-specific guidance
        if category == "Communication Boosters":
            prompt += "Focus on exercises that improve verbal and non-verbal communication skills.\n"
        elif category == "Physical Touch & Affection":
            prompt += "Focus on non-sexual physical connection, affection, and touch exercises.\n"
        elif category == "Creative Date Night Ideas":
            prompt += "Focus on unique, creative activities the couple can do together.\n"
        elif category == "Sexual Exploration":
            prompt += "Focus on intimate activities that enhance sexual connection, while being respectful and consensual.\n"
        elif category == "Emotional Connection":
            prompt += "Focus on activities that deepen emotional intimacy and understanding.\n"
    
    # Add structure requirements
    prompt += """
Please provide the response in the following JSON format:
```json
{
  "id": "unique_id",
  "title": "Challenge Title",
  "description": "Detailed challenge description with specific steps",
  "category": "Category Name",
  "difficulty": "easy|medium|hard",
  "estimated_time": "Approximate time to complete",
  "benefits": ["benefit1", "benefit2"]
}
```

Keep in mind:
1. Challenge should be actionable and specific
2. Use {partner1} and {partner2} as placeholders in description
3. Make it appropriate for their relationship status and duration
4. Ensure the challenge is respectful and consensual
5. Provide a unique ID in the format "ai_categoryname_001"
"""
    
    return prompt

def extract_challenge_from_response(response_text: str) -> Dict[str, Any]:
    """Extract and parse the JSON challenge from the AI response."""
    try:
        # Look for JSON between triple backticks
        if "```json" in response_text and "```" in response_text.split("```json")[1]:
            json_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            # Try to find any code block
            json_text = response_text.split("```")[1].split("```")[0].strip()
        else:
            # Just try to parse the whole thing
            json_text = response_text.strip()
        
        challenge = json.loads(json_text)
        
        # Validate required fields
        required_fields = ["id", "title", "description", "category", "difficulty"]
        for field in required_fields:
            if field not in challenge:
                raise ValueError(f"Missing required field: {field}")
        
        return challenge
    
    except (json.JSONDecodeError, ValueError, IndexError) as e:
        # Fallback: create a structured challenge from unstructured response
        return {
            "id": f"ai_fallback_{random.randint(1000, 9999)}",
            "title": "AI-Generated Challenge",
            "description": response_text.replace("```", "").strip(),
            "category": "Relationship Challenge",
            "difficulty": "medium"
        }

def generate_ai_challenge(user_profile: Dict[str, Any], category: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a challenge using Google's Gemini AI.
    Includes caching and error handling to minimize API usage.
    """
    # Check cache first
    cache_key = get_cache_key(user_profile, category)
    cached_challenges = check_cache(cache_key)
    
    if cached_challenges:
        # Return a random challenge from cache
        return random.choice(cached_challenges)
    
    try:
        # Create the AI model - using Gemini Pro for structured content generation
        def create_model():
            """Helper function to create the AI model with version compatibility"""
            try:
                # Try different approaches based on API version
                try:
                    return genai.GenerativeModel('gemini-1.5-pro')
                except AttributeError:
                    try:
                        return genai.get_model('gemini-1.5-pro')
                    except AttributeError:
                        return genai.models.get_model('gemini-1.5-pro')
            except Exception as e:
                print(f"Error creating model: {str(e)}")
                return None
                
        model = create_model()
        
        # Generate the prompt
        prompt = generate_challenge_prompt(user_profile, category)
        
        # Only proceed if we have a valid model
        if model:
            try:
                # Get the response from Gemini - handle different API versions
                try:
                    response = model.generate_content(prompt)
                    response_text = response.text if hasattr(response, 'text') else str(response)
                except AttributeError:
                    # Alternative API formats
                    try:
                        response = model.predict(prompt)
                        response_text = response
                    except:
                        # One more attempt with different method naming
                        response = model.generate(prompt)
                        response_text = response.result if hasattr(response, 'result') else str(response)
                
                # Process the response
                challenge = extract_challenge_from_response(response_text)
                
                # Store in cache for future use
                store_in_cache(cache_key, [challenge])
                
                return challenge
            except Exception as e:
                print(f"Error generating AI content: {str(e)}")
                # Will fall through to the fallback return
        
        # Fallback if model is invalid or response failed
        return {
            "id": f"ai_fallback_{random.randint(1000, 9999)}",
            "title": "Connection Exercise",
            "description": f"Take 15 minutes today to share three things you appreciate about each other. Start with '{user_profile.get('partner1_name', 'Partner 1')}, one thing I really appreciate about you is...'",
            "category": category or "Communication Boosters",
            "difficulty": "easy"
        }
            
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error generating AI challenge: {str(e)}")
        
        # Return a fallback challenge
        return {
            "id": f"ai_error_{random.randint(1000, 9999)}",
            "title": "Connection Exercise",
            "description": f"Take 15 minutes today to share three things you appreciate about each other. Start with '{user_profile.get('partner1_name', 'Partner 1')}, one thing I really appreciate about you is...'",
            "category": category or "Communication Boosters",
            "difficulty": "easy"
        }

def batch_generate_challenges(user_profile: Dict[str, Any], count: int = 5, 
                             categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Generate multiple challenges in batch to reduce API calls.
    This is meant for background generation during off-peak hours.
    """
    categories = categories or CATEGORIES
    challenges = []
    
    try:
        # Create the AI model
        def create_model():
            """Helper function to create the AI model with version compatibility"""
            try:
                # Try different approaches based on API version
                try:
                    return genai.GenerativeModel('gemini-1.5-pro')
                except AttributeError:
                    try:
                        return genai.get_model('gemini-1.5-pro')
                    except AttributeError:
                        return genai.models.get_model('gemini-1.5-pro')
            except Exception as e:
                print(f"Error creating model: {str(e)}")
                return None
                
        model = create_model()
        
        # Generate a batch prompt
        prompt = f"""Generate {count} unique relationship challenges for a couple.
        
Relationship Context:
- Partner names: {user_profile.get('partner1_name', 'Partner 1')} and {user_profile.get('partner2_name', 'Partner 2')}
- Relationship status: {user_profile.get('relationship_status', 'dating')}
- Relationship duration: {user_profile.get('relationship_duration', '')}

Please provide challenges across these categories: {', '.join(categories)}

Provide the response as a JSON array of challenges, each with this structure:
```json
[
  {{
    "id": "unique_id_1",
    "title": "Challenge Title",
    "description": "Detailed challenge description",
    "category": "One of the categories listed above",
    "difficulty": "easy|medium|hard"
  }},
  ...
]
```

Ensure each challenge is unique, actionable, appropriate for their relationship, and respectful.
"""
        
        # Only proceed if we have a valid model
        if model:
            try:
                # Get the response using appropriate method based on API version
                try:
                    response = model.generate_content(prompt)
                    response_text = response.text if hasattr(response, 'text') else str(response)
                except AttributeError:
                    try:
                        response = model.predict(prompt)
                        response_text = response
                    except:
                        response = model.generate(prompt)
                        response_text = response.result if hasattr(response, 'result') else str(response)
                
                # Try to extract the JSON array
                if "```json" in response_text and "```" in response_text.split("```json")[1]:
                    json_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    json_text = response_text.split("```")[1].split("```")[0].strip()
                else:
                    json_text = response_text.strip()
                    
                # Parse challenges
                try:
                    parsed_challenges = json.loads(json_text)
                    if isinstance(parsed_challenges, list):
                        challenges = parsed_challenges
                except json.JSONDecodeError:
                    # If we can't parse as JSON, create a fallback challenge
                    fallback_challenge = {
                        "id": f"ai_batch_fallback_{random.randint(1000, 9999)}",
                        "title": "Connection Time",
                        "description": "Take turns sharing three things you appreciate about each other.",
                        "category": categories[0] if categories else "Communication Boosters",
                        "difficulty": "easy"
                    }
                    challenges = [fallback_challenge]
            except Exception as e:
                print(f"Error in batch challenge generation: {str(e)}")
                
                # Store challenges by category in cache
                for challenge in challenges:
                    category = challenge.get("category")
                    if category:
                        cache_key = get_cache_key(user_profile, category)
                        existing = check_cache(cache_key)
                        if existing:
                            # Append to existing cache
                            existing.append(challenge)
                            store_in_cache(cache_key, existing)
                        else:
                            # Create new cache entry
                            store_in_cache(cache_key, [challenge])
    
    except Exception as e:
        # Log error (use proper logging in production)
        print(f"Error batch generating challenges: {str(e)}")
        # We'll return whatever challenges we managed to generate
    
    return challenges