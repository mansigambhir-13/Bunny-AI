#!/usr/bin/env python3
"""
Evaluation Framework - Measures conversation quality and evolution effectiveness
Real-time assessment of personality adaptation and conversation flow
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from textblob import TextBlob

logger = logging.getLogger(__name__)

class EvaluationFramework:
    """
    Comprehensive evaluation system for conversation quality and evolution effectiveness
    
    Metrics:
    - Response relevance and appropriateness
    - Personality adaptation success
    - Conversation flow and engagement
    - User satisfaction inference
    - Evolution stability and learning rate
    """
    
    def __init__(self, memory_manager):
        """Initialize evaluation framework"""
        self.memory_manager = memory_manager
        
        # Evaluation configuration
        self.eval_config = {
            'response_time_threshold': 3.0,  # Seconds for good response time
            'relevance_weight': 0.3,
            'engagement_weight': 0.25,
            'personality_match_weight': 0.25,
            'technical_quality_weight': 0.2,
            'min_evaluations_for_stability': 10
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 0.8,
            'good': 0.6,
            'acceptable': 0.4,
            'poor': 0.2
        }
        
        logger.info("📊 Evaluation Framework initialized")
    
    async def evaluate_interaction(self, user_id: str, user_message: str, 
                                 agent_response: str, response_time: float,
                                 additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive evaluation of a single interaction
        
        Args:
            user_id: User identifier
            user_message: User's input message
            agent_response: Agent's response
            response_time: Time taken to generate response
            additional_context: Extra context for evaluation
            
        Returns:
            Dict with detailed evaluation metrics
        """
        start_time = time.time()
        
        try:
            # Get user profile for context
            user_profile = self.memory_manager.get_user_profile(user_id)
            personality = user_profile.get('personality_vector', {})
            
            # Initialize additional context if not provided
            if additional_context is None:
                additional_context = {}
            
            # Calculate individual metrics
            relevance_score = await self._evaluate_relevance(user_message, agent_response)
            engagement_score = await self._evaluate_engagement(user_message, agent_response)
            personality_match_score = await self._evaluate_personality_match(
                user_message, agent_response, personality
            )
            technical_quality_score = await self._evaluate_technical_quality(
                agent_response, response_time
            )
            
            # Calculate overall quality score
            overall_score = (
                relevance_score * self.eval_config['relevance_weight'] +
                engagement_score * self.eval_config['engagement_weight'] +
                personality_match_score * self.eval_config['personality_match_weight'] +
                technical_quality_score * self.eval_config['technical_quality_weight']
            )
            
            # Determine quality category
            quality_category = self._categorize_quality(overall_score)
            
            # Calculate conversation flow metrics
            flow_metrics = await self._evaluate_conversation_flow(user_id, user_message, agent_response)
            
            # Evaluate evolution effectiveness
            evolution_metrics = await self._evaluate_evolution_effectiveness(user_id, additional_context)
            
            # Processing time for evaluation itself
            eval_time = time.time() - start_time
            
            evaluation_result = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                
                # Individual metric scores (0.0 to 1.0)
                'relevance_score': relevance_score,
                'engagement_score': engagement_score,
                'personality_match_score': personality_match_score,
                'technical_quality_score': technical_quality_score,
                
                # Overall quality
                'overall_quality_score': overall_score,
                'quality_category': quality_category,
                
                # Response timing
                'response_time': response_time,
                'response_time_score': self._score_response_time(response_time),
                
                # Conversation flow
                'flow_metrics': flow_metrics,
                
                # Evolution effectiveness
                'evolution_metrics': evolution_metrics,
                
                # Meta information
                'evaluation_time': eval_time,
                'user_message_length': len(user_message),
                'agent_response_length': len(agent_response),
                
                # Detailed analysis
                'detailed_analysis': {
                    'user_sentiment': self._analyze_sentiment(user_message),
                    'response_sentiment': self._analyze_sentiment(agent_response),
                    'topic_continuity': self._evaluate_topic_continuity(user_message, agent_response),
                    'response_complexity': self._evaluate_response_complexity(agent_response)
                }
            }
            
            # Update user's quality metrics
            await self._update_user_quality_metrics(user_id, evaluation_result)
            
            logger.info(f"📊 Evaluation completed for {user_id}: {quality_category} ({overall_score:.3f})")
            return evaluation_result
            
        except Exception as e:
            logger.error(f"❌ Evaluation error for user {user_id}: {e}")
            return {
                'error': str(e),
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'overall_quality_score': 0.5,  # Default neutral score
                'quality_category': 'unknown'
            }
    
    async def _evaluate_relevance(self, user_message: str, agent_response: str) -> float:
        """Evaluate how relevant the response is to the user's message"""
        try:
            # Simple keyword overlap analysis
            user_words = set(user_message.lower().split())
            response_words = set(agent_response.lower().split())
            
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                         'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were',
                         'i', 'you', 'he', 'she', 'it', 'we', 'they', 'that', 'this'}
            
            user_words -= stop_words
            response_words -= stop_words
            
            if not user_words:
                return 0.5  # Neutral if no meaningful words
            
            # Calculate overlap
            overlap = len(user_words.intersection(response_words))
            relevance = min(overlap / len(user_words), 1.0)
            
            # Boost score for question-answer patterns
            if '?' in user_message and any(word in agent_response.lower() 
                                         for word in ['yes', 'no', 'certainly', 'sure', 'definitely']):
                relevance = min(relevance + 0.2, 1.0)
            
            # Penalty for very generic responses
            generic_responses = ['i understand', 'that\'s interesting', 'i see', 'ok', 'good']
            if any(generic in agent_response.lower() for generic in generic_responses):
                if len(agent_response.split()) < 5:
                    relevance *= 0.7
            
            return max(0.0, min(1.0, relevance))
            
        except Exception as e:
            logger.warning(f"Error evaluating relevance: {e}")
            return 0.5
    
    async def _evaluate_engagement(self, user_message: str, agent_response: str) -> float:
        """Evaluate how engaging the response is"""
        try:
            score = 0.5  # Base score
            
            # Length appropriateness (not too short, not too long)
            response_length = len(agent_response.split())
            if 5 <= response_length <= 50:
                score += 0.2
            elif response_length < 3:
                score -= 0.3
            elif response_length > 100:
                score -= 0.2
            
            # Emotional engagement
            blob = TextBlob(agent_response)
            sentiment = blob.sentiment.polarity
            if abs(sentiment) > 0.1:  # Shows some emotional tone
                score += 0.1
            
            # Question asking (encourages continuation)
            if '?' in agent_response:
                score += 0.15
            
            # Personal pronouns (more engaging)
            personal_pronouns = ['you', 'your', 'we', 'us', 'our']
            pronoun_count = sum(1 for word in agent_response.lower().split() 
                              if word in personal_pronouns)
            if pronoun_count > 0:
                score += min(pronoun_count * 0.05, 0.2)
            
            # Enthusiasm markers
            enthusiasm_markers = ['!', 'great', 'wonderful', 'excellent', 'amazing']
            enthusiasm_count = sum(1 for marker in enthusiasm_markers 
                                 if marker in agent_response.lower())
            if enthusiasm_count > 0:
                score += min(enthusiasm_count * 0.05, 0.15)
            
            # Conversation continuity
            if any(phrase in agent_response.lower() for phrase in 
                   ['what do you think', 'tell me more', 'how about', 'what about']):
                score += 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.warning(f"Error evaluating engagement: {e}")
            return 0.5
    
    async def _evaluate_personality_match(self, user_message: str, agent_response: str, 
                                        personality: Dict[str, float]) -> float:
        """Evaluate how well the response matches the user's adapted personality"""
        try:
            score = 0.5  # Base score
            
            # Formality matching
            formality = personality.get('formality', 0.5)
            formal_indicators = ['please', 'thank you', 'certainly', 'indeed', 'furthermore']
            casual_indicators = ['hey', 'cool', 'yeah', 'awesome', 'gonna']
            
            formal_count = sum(1 for word in formal_indicators if word in agent_response.lower())
            casual_count = sum(1 for word in casual_indicators if word in agent_response.lower())
            
            if formality > 0.7 and formal_count > casual_count:
                score += 0.2
            elif formality < 0.3 and casual_count > formal_count:
                score += 0.2
            elif 0.3 <= formality <= 0.7 and abs(formal_count - casual_count) <= 1:
                score += 0.1
            
            # Enthusiasm matching
            enthusiasm = personality.get('enthusiasm', 0.7)
            exclamation_count = agent_response.count('!')
            enthusiasm_words = ['great', 'fantastic', 'wonderful', 'amazing', 'excellent']
            enthusiasm_word_count = sum(1 for word in enthusiasm_words 
                                      if word in agent_response.lower())
            
            if enthusiasm > 0.7 and (exclamation_count > 0 or enthusiasm_word_count > 0):
                score += 0.15
            elif enthusiasm < 0.3 and exclamation_count == 0 and enthusiasm_word_count == 0:
                score += 0.15
            
            # Technical depth matching
            technical_depth = personality.get('technical_depth', 0.5)
            technical_words = ['implementation', 'algorithm', 'analysis', 'system', 
                              'framework', 'methodology', 'optimization']
            technical_count = sum(1 for word in technical_words if word in agent_response.lower())
            
            if technical_depth > 0.6 and technical_count > 0:
                score += 0.1
            elif technical_depth < 0.4 and technical_count == 0:
                score += 0.1
            
            # Verbosity matching
            verbosity = personality.get('verbosity', 0.5)
            response_length = len(agent_response.split())
            
            if verbosity > 0.7 and response_length > 20:
                score += 0.1
            elif verbosity < 0.3 and response_length < 10:
                score += 0.1
            elif 0.3 <= verbosity <= 0.7 and 10 <= response_length <= 20:
                score += 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.warning(f"Error evaluating personality match: {e}")
            return 0.5
    
    async def _evaluate_technical_quality(self, agent_response: str, response_time: float) -> float:
        """Evaluate technical quality of the response"""
        try:
            score = 0.5  # Base score
            
            # Response time quality
            time_score = self._score_response_time(response_time)
            score += time_score * 0.3
            
            # Grammar and structure (basic checks)
            if agent_response.strip():
                # Check for proper sentence structure
                sentences = agent_response.split('.')
                if len(sentences) > 1:  # Multi-sentence response
                    score += 0.1
                
                # Check capitalization
                if agent_response[0].isupper():
                    score += 0.05
                
                # Check for complete sentences
                if agent_response.strip().endswith(('.', '!', '?')):
                    score += 0.1
                
                # No obvious errors (very basic check)
                if '  ' not in agent_response:  # No double spaces
                    score += 0.05
            
            # Response coherence (length vs content)
            words = agent_response.split()
            if len(words) > 3:  # Has meaningful content
                avg_word_length = np.mean([len(word) for word in words])
                if 3 <= avg_word_length <= 8:  # Reasonable vocabulary
                    score += 0.1
            
            # Avoid repetition
            word_counts = {}
            for word in words:
                word_lower = word.lower()
                word_counts[word_lower] = word_counts.get(word_lower, 0) + 1
            
            max_repetition = max(word_counts.values()) if word_counts else 1
            if max_repetition <= 2:  # No excessive repetition
                score += 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.warning(f"Error evaluating technical quality: {e}")
            return 0.5
    
    def _score_response_time(self, response_time: float) -> float:
        """Score response time (faster is generally better, but not instant)"""
        if response_time < 0.5:  # Too fast, might be cached/generic
            return 0.7
        elif response_time <= 2.0:  # Good response time
            return 1.0
        elif response_time <= 5.0:  # Acceptable
            return 0.8
        elif response_time <= 10.0:  # Slow but okay
            return 0.6
        else:  # Too slow
            return 0.3
    
    async def _evaluate_conversation_flow(self, user_id: str, user_message: str, 
                                        agent_response: str) -> Dict[str, float]:
        """Evaluate conversation flow and continuity"""
        try:
            # Get recent conversation history
            profile = self.memory_manager.get_user_profile(user_id)
            history = profile.get('conversation_history', [])
            
            flow_metrics = {
                'topic_continuity': 0.5,
                'response_variety': 0.5,
                'conversation_progression': 0.5
            }
            
            if len(history) >= 2:
                # Topic continuity: does the conversation stay on topic?
                recent_messages = history[-3:]  # Last 3 exchanges
                topics = []
                for entry in recent_messages:
                    if 'message_analysis' in entry:
                        # Extract key topics (simplified)
                        message = entry.get('user_message', '')
                        topics.extend(message.lower().split())
                
                if topics:
                    current_topics = user_message.lower().split()
                    overlap = len(set(topics).intersection(set(current_topics)))
                    flow_metrics['topic_continuity'] = min(overlap / len(current_topics), 1.0) if current_topics else 0.5
                
                # Response variety: are responses varied or repetitive?
                recent_responses = [entry.get('agent_response', '') for entry in recent_messages[-5:]]
                recent_responses.append(agent_response)
                
                if len(recent_responses) > 1:
                    response_similarities = []
                    for i, resp1 in enumerate(recent_responses):
                        for resp2 in recent_responses[i+1:]:
                            words1 = set(resp1.lower().split())
                            words2 = set(resp2.lower().split())
                            if words1 and words2:
                                similarity = len(words1.intersection(words2)) / len(words1.union(words2))
                                response_similarities.append(similarity)
                    
                    if response_similarities:
                        avg_similarity = np.mean(response_similarities)
                        flow_metrics['response_variety'] = max(0.0, 1.0 - avg_similarity)
                
                # Conversation progression: is the conversation moving forward?
                if len(history) > 0:
                    last_entry = history[-1]
                    last_message = last_entry.get('user_message', '')
                    
                    # Check if user is asking new questions or building on previous topics
                    if '?' in user_message and '?' not in last_message:
                        flow_metrics['conversation_progression'] = 0.8
                    elif len(user_message.split()) > len(last_message.split()):
                        flow_metrics['conversation_progression'] = 0.7
                    else:
                        flow_metrics['conversation_progression'] = 0.6
            
            return flow_metrics
            
        except Exception as e:
            logger.warning(f"Error evaluating conversation flow: {e}")
            return {'topic_continuity': 0.5, 'response_variety': 0.5, 'conversation_progression': 0.5}
    
    async def _evaluate_evolution_effectiveness(self, user_id: str, 
                                              context: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate how effective the personality evolution is"""
        try:
            profile = self.memory_manager.get_user_profile(user_id)
            evolution_metrics = profile.get('evolution_metrics', {})
            
            effectiveness = {
                'adaptation_rate': 0.5,
                'stability': 0.5,
                'learning_consistency': 0.5
            }
            
            # Adaptation rate: is the personality adapting appropriately?
            total_adaptations = evolution_metrics.get('total_adaptations', 0)
            conversation_count = profile.get('conversation_count', 1)
            
            if conversation_count > 0:
                adaptation_ratio = total_adaptations / conversation_count
                # Good adaptation rate is around 30-70%
                if 0.3 <= adaptation_ratio <= 0.7:
                    effectiveness['adaptation_rate'] = 0.8
                elif 0.1 <= adaptation_ratio <= 0.9:
                    effectiveness['adaptation_rate'] = 0.6
                else:
                    effectiveness['adaptation_rate'] = 0.4
            
            # Stability: is the personality stable over time?
            stability_score = evolution_metrics.get('stability_score', 1.0)
            effectiveness['stability'] = stability_score
            
            # Learning consistency: are adaptations consistent with user behavior?
            learning_progression = evolution_metrics.get('learning_progression', [])
            if len(learning_progression) >= 5:
                recent_changes = learning_progression[-5:]
                change_magnitudes = [entry['change_magnitude'] for entry in recent_changes]
                
                # Consistent learning should show decreasing change magnitudes over time
                if len(change_magnitudes) > 1:
                    trend = np.polyfit(range(len(change_magnitudes)), change_magnitudes, 1)[0]
                    if trend < 0:  # Decreasing trend (converging)
                        effectiveness['learning_consistency'] = 0.8
                    elif abs(trend) < 0.1:  # Stable
                        effectiveness['learning_consistency'] = 0.7
                    else:  # Increasing trend (diverging)
                        effectiveness['learning_consistency'] = 0.4
            
            return effectiveness
            
        except Exception as e:
            logger.warning(f"Error evaluating evolution effectiveness: {e}")
            return {'adaptation_rate': 0.5, 'stability': 0.5, 'learning_consistency': 0.5}
    
    def _categorize_quality(self, score: float) -> str:
        """Categorize quality score into human-readable category"""
        if score >= self.quality_thresholds['excellent']:
            return 'excellent'
        elif score >= self.quality_thresholds['good']:
            return 'good'
        elif score >= self.quality_thresholds['acceptable']:
            return 'acceptable'
        elif score >= self.quality_thresholds['poor']:
            return 'poor'
        else:
            return 'very_poor'
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text"""
        try:
            blob = TextBlob(text)
            return {
                'polarity': float(blob.sentiment.polarity),    # -1 to 1
                'subjectivity': float(blob.sentiment.subjectivity)  # 0 to 1
            }
        except:
            return {'polarity': 0.0, 'subjectivity': 0.5}
    
    def _evaluate_topic_continuity(self, user_message: str, agent_response: str) -> float:
        """Evaluate if the response stays on the same topic as the user message"""
        try:
            user_words = set(user_message.lower().split())
            response_words = set(agent_response.lower().split())
            
            # Remove stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            user_words -= stop_words
            response_words -= stop_words
            
            if not user_words:
                return 0.5
            
            overlap = len(user_words.intersection(response_words))
            return min(overlap / len(user_words), 1.0)
            
        except:
            return 0.5
    
    def _evaluate_response_complexity(self, response: str) -> Dict[str, float]:
        """Evaluate complexity metrics of the response"""
        try:
            words = response.split()
            if not words:
                return {'length_complexity': 0.0, 'vocabulary_complexity': 0.0}
            
            # Length complexity
            length_complexity = min(len(words) / 50.0, 1.0)  # Normalize to max 50 words
            
            # Vocabulary complexity (average word length)
            avg_word_length = np.mean([len(word) for word in words])
            vocabulary_complexity = min((avg_word_length - 3) / 7.0, 1.0)  # 3-10 letter range
            
            return {
                'length_complexity': max(0.0, length_complexity),
                'vocabulary_complexity': max(0.0, vocabulary_complexity)
            }
            
        except:
            return {'length_complexity': 0.0, 'vocabulary_complexity': 0.0}
    
    async def _update_user_quality_metrics(self, user_id: str, evaluation: Dict[str, Any]):
        """Update user's running quality metrics"""
        try:
            profile = self.memory_manager.get_user_profile(user_id)
            
            if 'quality_metrics' not in profile:
                profile['quality_metrics'] = {
                    'average_engagement': 0.0,
                    'average_relevance': 0.0,
                    'average_overall_quality': 0.0,
                    'total_evaluations': 0
                }
            
            metrics = profile['quality_metrics']
            total_evals = metrics['total_evaluations']
            
            # Update running averages
            metrics['average_engagement'] = (
                (metrics['average_engagement'] * total_evals + evaluation['engagement_score']) / 
                (total_evals + 1)
            )
            metrics['average_relevance'] = (
                (metrics['average_relevance'] * total_evals + evaluation['relevance_score']) / 
                (total_evals + 1)
            )
            metrics['average_overall_quality'] = (
                (metrics['average_overall_quality'] * total_evals + evaluation['overall_quality_score']) / 
                (total_evals + 1)
            )
            metrics['total_evaluations'] = total_evals + 1
            
            profile['quality_metrics'] = metrics
            profile['last_updated'] = datetime.now().isoformat()
            
            await self.memory_manager.update_user_profile(user_id, profile)
            
        except Exception as e:
            logger.error(f"Error updating quality metrics for user {user_id}: {e}")
    
    async def get_user_quality_report(self, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive quality report for a user"""
        try:
            profile = self.memory_manager.get_user_profile(user_id)
            quality_metrics = profile.get('quality_metrics', {})
            evolution_metrics = profile.get('evolution_metrics', {})
            
            report = {
                'user_id': user_id,
                'report_generated': datetime.now().isoformat(),
                'total_conversations': profile.get('conversation_count', 0),
                'total_evaluations': quality_metrics.get('total_evaluations', 0),
                
                # Quality averages
                'quality_averages': {
                    'engagement': quality_metrics.get('average_engagement', 0.0),
                    'relevance': quality_metrics.get('average_relevance', 0.0),
                    'overall_quality': quality_metrics.get('average_overall_quality', 0.0)
                },
                
                # Evolution effectiveness
                'evolution_effectiveness': {
                    'total_adaptations': evolution_metrics.get('total_adaptations', 0),
                    'stability_score': evolution_metrics.get('stability_score', 1.0),
                    'largest_change': evolution_metrics.get('largest_personality_change', 0.0)
                },
                
                # Quality category distribution (if we had historical data)
                'recommendations': []
            }
            
            # Generate recommendations based on metrics
            avg_quality = quality_metrics.get('average_overall_quality', 0.0)
            if avg_quality < 0.5:
                report['recommendations'].append("Consider adjusting evolution sensitivity for better user alignment")
            
            if evolution_metrics.get('stability_score', 1.0) < 0.7:
                report['recommendations'].append("Personality evolution may be too volatile - consider reducing learning rate")
            
            if quality_metrics.get('average_engagement', 0.0) < 0.6:
                report['recommendations'].append("Focus on improving response engagement and interactivity")
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating quality report for user {user_id}: {e}")
            return {'error': str(e), 'user_id': user_id}