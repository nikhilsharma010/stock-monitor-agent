"""
AI Context Builder Module
Builds personalized investment profiles and generates tailored recommendations.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ContextBuilder:
    """Manages AI-powered investment context and personalized recommendations."""
    
    def __init__(self, groq_client, cache_db):
        """Initialize with Groq client and cache database."""
        self.client = groq_client
        self.cache = cache_db
        self.model = "llama-3.3-70b-versatile"
    
    def build_investment_profile(self, user_id):
        """
        Synthesize all user notes into a coherent investment DNA profile.
        Returns AI-generated profile summary.
        """
        if not self.client:
            return "AI Context Builder is offline."
        
        try:
            # Fetch user context
            notes = self.cache.get_user_context(user_id, limit=100)
            if not notes:
                return "No investment context found. Use `/note` to start building your profile!"
            
            # Get user risk profile
            risk = self.cache.get_user_risk(user_id)
            interests = self.cache.get_user_state(user_id).get('interests', '')
            
            # Build context string
            context_str = "\\n".join([f"- {n['note']}" for n in notes])
            
            system_prompt = (
                "You are an Investment Profile Analyst.\\n"
                "TASK: Synthesize the user's notes into a coherent 'Investment DNA' profile.\\n"
                "STRUCTURE:\\n"
                "1. **Core Thesis**: What is their overarching investment philosophy?\\n"
                "2. **Sector Focus**: Which sectors/themes do they favor?\\n"
                "3. **Risk Appetite**: How do they approach risk? (based on notes + stated risk profile)\\n"
                "4. **Key Learnings**: What have they learned from experience?\\n"
                "5. **Blind Spots**: What areas might they be overlooking?\\n"
                "RULES: Be concise but insightful. Use bold headers. Max 250 words."
            )
            
            user_prompt = (
                f"Risk Profile: {risk}\\n"
                f"Stated Interests: {interests}\\n\\n"
                f"Investment Notes:\\n{context_str}\\n\\n"
                "Generate the Investment DNA profile."
            )
            
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=500
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error building investment profile: {e}")
            return f"❌ Failed to build profile: {str(e)}"
    
    def get_personalized_recommendations(self, user_id, analyzer):
        """
        Generate stock recommendations based on user's investment context.
        Uses accumulated notes to provide highly personalized picks.
        """
        if not self.client:
            return "AI Recommendation Engine is offline."
        
        try:
            # Fetch user context
            notes = self.cache.get_user_context(user_id, limit=50)
            if not notes:
                return "Build your investment context first with `/note` to get personalized recommendations!"
            
            # Get user profile data
            risk = self.cache.get_user_risk(user_id)
            interests = self.cache.get_user_state(user_id).get('interests', '')
            watchlist = self.cache.get_user_watchlist(user_id)
            
            # Build context summary
            context_str = "\\n".join([f"- {n['note']}" for n in notes[:20]])  # Use recent 20 notes
            
            # Get sector trends for market context
            sector_trends = analyzer.get_sector_trends()
            sector_context = "\\n".join([f"- {t['name']}: {t['change']:+.2f}%" for t in sector_trends[:5]])
            
            system_prompt = (
                "You are a Personalized Investment Advisor.\\n"
                f"USER PROFILE: {risk} investor interested in {interests}.\\n"
                "TASK: Recommend 3-5 stocks that align with the user's investment thesis and context.\\n"
                "STRUCTURE:\\n"
                "For each pick:\\n"
                "1. **[TICKER]** - Company name\\n"
                "2. **Why It Fits**: Reference specific user notes that align with this pick\\n"
                "3. **Catalyst**: What makes it interesting now?\\n"
                "RULES: Be specific. Quote user notes. Use bold formatting. Max 300 words total."
            )
            
            user_prompt = (
                f"User's Investment Context (Recent Notes):\\n{context_str}\\n\\n"
                f"Current Sector Performance:\\n{sector_context}\\n\\n"
                f"User's Watchlist: {', '.join(watchlist) if watchlist else 'None'}\\n\\n"
                "Generate personalized stock recommendations."
            )
            
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.4,
                max_tokens=600
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return f"❌ Failed to generate recommendations: {str(e)}"
    
    def analyze_context_evolution(self, user_id):
        """
        Track how the user's investment philosophy has evolved over time.
        Compares early notes with recent notes.
        """
        if not self.client:
            return "AI Evolution Tracker is offline."
        
        try:
            all_notes = self.cache.get_user_context(user_id, limit=100)
            if len(all_notes) < 5:
                return "Not enough context history yet. Add more notes to track your evolution!"
            
            # Split into early and recent
            recent_notes = all_notes[:10]
            early_notes = all_notes[-10:]
            
            early_str = "\\n".join([f"- {n['note']}" for n in early_notes])
            recent_str = "\\n".join([f"- {n['note']}" for n in recent_notes])
            
            system_prompt = (
                "You are an Investment Psychology Analyst.\\n"
                "TASK: Analyze how the user's investment philosophy has evolved.\\n"
                "STRUCTURE:\\n"
                "1. **Then**: What characterized their early thinking?\\n"
                "2. **Now**: How has their approach changed?\\n"
                "3. **Growth**: What have they learned?\\n"
                "4. **Consistency**: What themes remain constant?\\n"
                "RULES: Be insightful. Highlight positive evolution. Max 200 words."
            )
            
            user_prompt = (
                f"Early Notes (First entries):\\n{early_str}\\n\\n"
                f"Recent Notes (Latest entries):\\n{recent_str}\\n\\n"
                "Analyze the evolution."
            )
            
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=400
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error analyzing evolution: {e}")
            return f"❌ Failed to analyze evolution: {str(e)}"
