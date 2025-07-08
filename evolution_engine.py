#!/usr/bin/env python3
"""
Evolution Engine - Core personality adaptation logic
Handles real-time personality evolution based on user interactions
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import numpy as np
from textblob import TextBlob

logger = logging.getLogger(__name__)

class EvolutionEngine:
    """
    Core evolution engine that adapts agent personality based on user interactions
    
    Features:
    - Real-time personality vector adaptation
    - Sentiment analysis integration
    - Communication style detection
    - Progressive learning with memory persistence
    """
    
    def __init__(self, memory_manager):
        """Initialize evolution engine with memory manager"""
        self.memory_manager = memory_manager
        
        # Evolution configuration
        self.evolution_config = {
            'learning_rate': 0.1,           # How fast personality adapts
            'sentiment_weight': 0.3,        # Impact of sentiment on evolution
            'style_weight': 0.4,           # Impact of communication style
            'consistency_weight': 0.3,      # Importance of maintaining consistency
            'max_evolution_per_turn': 0.2,  # Maximum change per interaction
        }
        
        # Personality dimensions
        self.personality_dimensions = {
            'formality': {'min': 0.0, 'max': 1.0, 'default': 0.5},
            'enthusiasm': {'min': 0.0, 'max': 1.0, 'default': 0.7},
            'humor': {'min': 0.0, 'max': 1.0, 'default': 0.4},
            'technical_depth': {'min': 0.0, 'max': 1.0, 'default': 0.5},
            'empathy': {'min': 0.0, 'max': 1.0, 'default': 0.6},
            'verbosity': {'min': 0.0, 'max': 1.0, 'default': 0.5},
        }
        
        logger.info("🧠 Evolution Engine initialized")
    
    async def process_message(self, user_id: str, user_message: str) -> Dict[str, Any]:
        """
        Process user message and evolve personality accordingly
        
        Args:
            user_id: Unique user identifier
            user_message: User's input message
            
        Returns:
            Dict with evolved response and evolution metrics
        """
        start_time = time.time()
        
        try:
            # Get current user profile
            user_profile = self.memory_manager.get_user_profile(user_id)
            current_personality = user_profile.get('personality_vector', {})
            
            # Initialize personality if new user
            if not current_personality:
                current_personality = self._initialize_personality()
                logger.info(f"🆕 Initialized new personality for user {user_id}")
            
            # Analyze user message
            message_analysis = await self._analyze_message(user_message)
            
            # Calculate personality evolution
            evolution_changes = await self._calculate_evolution(
                current_personality, message_analysis
            )
            
            # Apply evolution changes
            new_personality = self._apply_evolution_changes(
                current_personality, evolution_changes
            )
            
            # Generate response based on evolved personality
            agent_response = await self._generate_evolved_response(
                user_message, new_personality, message_analysis
            )
            
            # Update user profile with new personality
            await self._update_user_profile(user_id, new_personality, message_analysis)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            result = {
                'user_id': user_id,
                'user_message': user_message,
                'agent_response': agent_response,
                'evolution_changes': evolution_changes,
                'new_personality': new_personality,
                'message_analysis': message_analysis,
                'sentiment': message_analysis.get('sentiment', 0.5),
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"🔄 Evolution completed for {user_id} in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Evolution error for user {user_id}: {e}")
            return {
                'user_id': user_id,
                'agent_response': "I understand. Let me adapt to your communication style.",
                'evolution_changes': {},
                'error': str(e)
            }
    
    async def _analyze_message(self, message: str) -> Dict[str, Any]:
        """Analyze user message for evolution signals"""
        
        # Sentiment analysis
        blob = TextBlob(message)
        sentiment = float(blob.sentiment.polarity)  # -1 to 1
        sentiment_normalized = (sentiment + 1) / 2  # 0 to 1
        
        # Communication style analysis
        style_signals = {
            'formality': self._detect_formality(message),
            'enthusiasm': self._detect_enthusiasm(message),
            'humor': self._detect_humor(message),
            'technical': self._detect_technical_language(message),
            'emotional': self._detect_emotional_language(message),
            'verbosity': len(message.split()) / 20.0  # Normalize by typical length
        }
        
        # Length and complexity
        word_count = len(message.split())
        avg_word_length = np.mean([len(word) for word in message.split()])
        
        return {
            'sentiment': sentiment_normalized,
            'sentiment_raw': sentiment,
            'style_signals': style_signals,
            'word_count': word_count,
            'avg_word_length': avg_word_length,
            'message_length': len(message),
            'complexity_score': avg_word_length / 10.0,  # Normalize
            'timestamp': datetime.now().isoformat()
        }
    
    def _detect_formality(self, message: str) -> float:
        """Detect formality level in message"""
        formal_indicators = [
            'please', 'thank you', 'could you', 'would you', 'may i',
            'certainly', 'indeed', 'furthermore', 'moreover', 'however'
        ]
        casual_indicators = [
            'hey', 'yeah', 'cool', 'awesome', 'lol', 'btw',
            'gonna', 'wanna', 'gotta', 'yep', 'nope'
        ]
        
        msg_lower = message.lower()
        formal_count = sum(1 for indicator in formal_indicators if indicator in msg_lower)
        casual_count = sum(1 for indicator in casual_indicators if indicator in msg_lower)
        
        if formal_count + casual_count == 0:
            return 0.5  # Neutral
        
        formality = formal_count / (formal_count + casual_count)
        return formality
    
    def _detect_enthusiasm(self, message: str) -> float:
        """Detect enthusiasm level in message"""
        enthusiasm_indicators = [
            '!', 'amazing', 'awesome', 'fantastic', 'excellent', 'brilliant',
            'love', 'excited', 'wonderful', 'incredible', 'great'
        ]
        
        msg_lower = message.lower()
        exclamation_count = message.count('!')
        caps_ratio = sum(1 for c in message if c.isupper()) / len(message) if message else 0
        
        enthusiasm_words = sum(1 for indicator in enthusiasm_indicators if indicator in msg_lower)
        
        # Combine signals
        enthusiasm_score = (
            min(exclamation_count / 3.0, 1.0) * 0.4 +
            min(caps_ratio * 5, 1.0) * 0.3 +
            min(enthusiasm_words / 5.0, 1.0) * 0.3
        )
        
        return min(enthusiasm_score, 1.0)
    
    def _detect_humor(self, message: str) -> float:
        """Detect humor/playfulness in message"""
        humor_indicators = [
            'lol', 'haha', 'funny', 'joke', 'kidding', 'just joking',
            '😂', '😄', '😊', ':)', ':D', 'lmao'
        ]
        
        msg_lower = message.lower()
        humor_count = sum(1 for indicator in humor_indicators if indicator in msg_lower)
        
        return min(humor_count / 3.0, 1.0)
    
    def _detect_technical_language(self, message: str) -> float:
        """Detect technical language complexity"""
        technical_indicators = [
            'algorithm', 'implementation', 'architecture', 'framework',
            'api', 'database', 'optimization', 'analysis', 'system',
            'function', 'method', 'class', 'variable', 'parameter'
        ]
        
        msg_lower = message.lower()
        technical_count = sum(1 for indicator in technical_indicators if indicator in msg_lower)
        
        # Also consider average word length as technical indicator
        avg_word_length = np.mean([len(word) for word in message.split()]) if message.split() else 0
        length_score = min((avg_word_length - 4) / 6.0, 1.0) if avg_word_length > 4 else 0
        
        technical_score = min(technical_count / 5.0, 1.0) * 0.7 + length_score * 0.3
        return min(technical_score, 1.0)
    
    def _detect_emotional_language(self, message: str) -> float:
        """Detect emotional language"""
        emotional_indicators = [
            'feel', 'feeling', 'emotion', 'happy', 'sad', 'frustrated',
            'excited', 'worried', 'concerned', 'grateful', 'appreciate',
            'love', 'hate', 'angry', 'disappointed', 'thrilled'
        ]
        
        msg_lower = message.lower()
        emotional_count = sum(1 for indicator in emotional_indicators if indicator in msg_lower)
        
        return min(emotional_count / 3.0, 1.0)
    
    async def _calculate_evolution(self, current_personality: Dict[str, float], 
                                 message_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate how personality should evolve based on message analysis"""
        
        evolution_changes = {}
        style_signals = message_analysis['style_signals']
        sentiment = message_analysis['sentiment']
        learning_rate = self.evolution_config['learning_rate']
        
        # Calculate target personality adjustments
        targets = {
            'formality': style_signals['formality'],
            'enthusiasm': style_signals['enthusiasm'] * sentiment,  # Positive sentiment reinforces enthusiasm
            'humor': style_signals['humor'],
            'technical_depth': style_signals['technical'],
            'empathy': style_signals['emotional'],
            'verbosity': min(style_signals['verbosity'], 1.0)
        }
        
        # Calculate evolution for each dimension
        for dimension, target in targets.items():
            current_value = current_personality.get(dimension, 0.5)
            
            # Calculate desired change
            desired_change = (target - current_value) * learning_rate
            
            # Apply maximum change limit
            max_change = self.evolution_config['max_evolution_per_turn']
            actual_change = np.clip(desired_change, -max_change, max_change)
            
            # Store the change
            if abs(actual_change) > 0.01:  # Only store significant changes
                evolution_changes[dimension] = actual_change
        
        return evolution_changes
    
    def _apply_evolution_changes(self, current_personality: Dict[str, float], 
                               evolution_changes: Dict[str, float]) -> Dict[str, float]:
        """Apply evolution changes to personality vector"""
        
        new_personality = current_personality.copy()
        
        for dimension, change in evolution_changes.items():
            current_value = new_personality.get(dimension, 0.5)
            new_value = current_value + change
            
            # Ensure value stays within bounds
            bounds = self.personality_dimensions.get(dimension, {'min': 0.0, 'max': 1.0})
            new_value = np.clip(new_value, bounds['min'], bounds['max'])
            
            new_personality[dimension] = new_value
        
        return new_personality
    
    async def _generate_evolved_response(self, user_message: str, 
                                       personality: Dict[str, float],
                                       message_analysis: Dict[str, Any]) -> str:
        """Generate response based on evolved personality"""
        
        # Extract personality values
        formality = personality.get('formality', 0.5)
        enthusiasm = personality.get('enthusiasm', 0.7)
        humor = personality.get('humor', 0.4)
        technical_depth = personality.get('technical_depth', 0.5)
        empathy = personality.get('empathy', 0.6)
        verbosity = personality.get('verbosity', 0.5)
        
        # Generate response based on personality
        response_parts = []
        
        # Greeting/acknowledgment based on formality
        if formality > 0.7:
            acknowledgments = ["Certainly,", "Indeed,", "I understand,", "Thank you for sharing,"]
        elif formality < 0.3:
            acknowledgments = ["Got it!", "Cool,", "Right,", "Yeah,"]
        else:
            acknowledgments = ["I see,", "That's interesting,", "I understand,", "Thanks,"]
        
        # Add enthusiasm markers
        if enthusiasm > 0.7:
            enthusiasm_markers = ["That's fantastic!", "How exciting!", "Amazing!", "Wonderful!"]
            if np.random.random() < 0.6:  # 60% chance to add enthusiasm
                response_parts.append(np.random.choice(enthusiasm_markers))
        
        # Main response content
        if 'question' in user_message.lower() or '?' in user_message:
            if technical_depth > 0.6:
                response_parts.append("Let me provide a comprehensive analysis of this topic.")
            else:
                response_parts.append("I'd be happy to help with that.")
        else:
            response_parts.append(np.random.choice(acknowledgments))
        
        # Add empathy if emotional content detected
        if empathy > 0.6 and message_analysis['style_signals']['emotional'] > 0.3:
            empathy_responses = [
                "I can understand how you might feel about that.",
                "That sounds really important to you.",
                "I appreciate you sharing that with me."
            ]
            response_parts.append(np.random.choice(empathy_responses))
        
        # Add humor if appropriate
        if humor > 0.6 and message_analysis['style_signals']['humor'] > 0.2:
            humor_additions = [
                "And hey, at least we're having fun with this!",
                "Always good to keep things light!",
                "I do enjoy our conversations!"
            ]
            if np.random.random() < 0.4:  # 40% chance
                response_parts.append(np.random.choice(humor_additions))
        
        # Adjust verbosity
        if verbosity < 0.3:
            # Keep it short
            response = response_parts[0] if response_parts else "I understand."
        elif verbosity > 0.7:
            # Make it more detailed
            response_parts.append("I'm continuously learning from our conversation to better match your communication style.")
            response = " ".join(response_parts)
        else:
            # Medium length
            response = " ".join(response_parts[:2])
        
        # Ensure we have a valid response
        if not response.strip():
            response = "I understand and I'm adapting to your communication style."
        
        return response
    
    async def _update_user_profile(self, user_id: str, new_personality: Dict[str, float],
                                 message_analysis: Dict[str, Any]):
        """Update user profile with evolved personality"""
        
        try:
            # Get current profile
            profile = self.memory_manager.get_user_profile(user_id)
            
            # Update with new data
            profile['personality_vector'] = new_personality
            profile['last_updated'] = datetime.now().isoformat()
            profile['conversation_count'] = profile.get('conversation_count', 0) + 1
            
            # Add conversation history (keep last 10)
            if 'conversation_history' not in profile:
                profile['conversation_history'] = []
            
            profile['conversation_history'].append({
                'timestamp': datetime.now().isoformat(),
                'message_analysis': message_analysis,
                'personality_snapshot': new_personality.copy()
            })
            
            # Keep only last 10 conversations
            profile['conversation_history'] = profile['conversation_history'][-10:]
            
            # Update in memory manager
            await self.memory_manager.update_user_profile(user_id, profile)
            
            logger.info(f"✅ Updated profile for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update profile for user {user_id}: {e}")
    
    def _initialize_personality(self) -> Dict[str, float]:
        """Initialize default personality for new user"""
        return {
            dimension: config['default']
            for dimension, config in self.personality_dimensions.items()
        }
    
    def get_personality_summary(self, user_id: str) -> Dict[str, Any]:
        """Get human-readable personality summary"""
        try:
            profile = self.memory_manager.get_user_profile(user_id)
            personality = profile.get('personality_vector', {})
            
            # Convert to readable descriptions
            summary = {}
            for dimension, value in personality.items():
                if dimension == 'formality':
                    if value > 0.7:
                        summary[dimension] = "Very formal and professional"
                    elif value < 0.3:
                        summary[dimension] = "Casual and relaxed"
                    else:
                        summary[dimension] = "Balanced formality"
                
                elif dimension == 'enthusiasm':
                    if value > 0.7:
                        summary[dimension] = "Highly enthusiastic and energetic"
                    elif value < 0.3:
                        summary[dimension] = "Calm and measured"
                    else:
                        summary[dimension] = "Moderately enthusiastic"
                
                elif dimension == 'humor':
                    if value > 0.6:
                        summary[dimension] = "Playful and humorous"
                    elif value < 0.3:
                        summary[dimension] = "Serious and focused"
                    else:
                        summary[dimension] = "Occasionally playful"
                
                elif dimension == 'technical_depth':
                    if value > 0.7:
                        summary[dimension] = "Highly technical and detailed"
                    elif value < 0.3:
                        summary[dimension] = "Simple and accessible"
                    else:
                        summary[dimension] = "Balanced technical depth"
                
                elif dimension == 'empathy':
                    if value > 0.7:
                        summary[dimension] = "Very empathetic and understanding"
                    elif value < 0.3:
                        summary[dimension] = "Analytical and objective"
                    else:
                        summary[dimension] = "Caring but balanced"
                
                elif dimension == 'verbosity':
                    if value > 0.7:
                        summary[dimension] = "Detailed and comprehensive"
                    elif value < 0.3:
                        summary[dimension] = "Concise and brief"
                    else:
                        summary[dimension] = "Balanced length responses"
            
            return {
                'user_id': user_id,
                'personality_summary': summary,
                'conversation_count': profile.get('conversation_count', 0),
                'last_updated': profile.get('last_updated', 'Never')
            }
            
        except Exception as e:
            logger.error(f"Error getting personality summary for {user_id}: {e}")
            return {'error': str(e)}