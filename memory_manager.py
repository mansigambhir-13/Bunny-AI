#!/usr/bin/env python3
"""
User Memory Manager - Persistent storage for user profiles and evolution data
Handles multiple users with distinct memory profiles
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

class UserMemoryManager:
    """
    Manages persistent user memory and personality profiles
    
    Features:
    - Per-user personality vector storage
    - Conversation history tracking
    - Evolution metrics persistence
    - JSON-based storage with backup
    - Async-safe file operations
    """
    
    def __init__(self, storage_dir: str = "./user_profiles"):
        """Initialize memory manager with storage directory"""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # In-memory cache for performance
        self.user_cache = {}
        
        # File locks for thread safety
        self.file_locks = {}
        
        logger.info(f"📁 User memory manager initialized: {self.storage_dir}")
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile with personality vector and history
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Dict containing user profile data
        """
        try:
            # Check cache first
            if user_id in self.user_cache:
                return self.user_cache[user_id].copy()
            
            # Load from file
            profile_path = self.storage_dir / f"{user_id}.json"
            
            if profile_path.exists():
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                
                # Update cache
                self.user_cache[user_id] = profile.copy()
                
                logger.info(f"📥 Loaded profile for user {user_id}")
                return profile.copy()
            else:
                # Create new user profile
                profile = self._create_new_user_profile(user_id)
                self.user_cache[user_id] = profile.copy()
                
                logger.info(f"🆕 Created new profile for user {user_id}")
                return profile.copy()
                
        except Exception as e:
            logger.error(f"❌ Error loading profile for user {user_id}: {e}")
            # Return default profile on error
            return self._create_new_user_profile(user_id)
    
    async def update_user_profile(self, user_id: str, profile: Dict[str, Any]):
        """
        Update user profile with new data
        
        Args:
            user_id: Unique user identifier
            profile: Updated profile data
        """
        try:
            # Update cache
            self.user_cache[user_id] = profile.copy()
            
            # Save to file asynchronously
            await self._save_profile_async(user_id, profile)
            
            logger.info(f"💾 Updated profile for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error updating profile for user {user_id}: {e}")
    
    async def _save_profile_async(self, user_id: str, profile: Dict[str, Any]):
        """Save profile to file asynchronously"""
        
        # Get or create file lock for this user
        if user_id not in self.file_locks:
            self.file_locks[user_id] = asyncio.Lock()
        
        async with self.file_locks[user_id]:
            profile_path = self.storage_dir / f"{user_id}.json"
            backup_path = self.storage_dir / f"{user_id}.json.backup"
            
            try:
                # Create backup of existing file
                if profile_path.exists():
                    import shutil
                    shutil.copy2(profile_path, backup_path)
                
                # Save new profile
                with open(profile_path, 'w', encoding='utf-8') as f:
                    json.dump(profile, f, indent=2, ensure_ascii=False)
                
                # Remove backup if save successful
                if backup_path.exists():
                    backup_path.unlink()
                    
            except Exception as e:
                # Restore from backup if save failed
                if backup_path.exists():
                    import shutil
                    shutil.move(backup_path, profile_path)
                raise e
    
    def _create_new_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Create a new user profile with default values"""
        
        profile = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'conversation_count': 0,
            
            # Default personality vector
            'personality_vector': {
                'formality': 0.5,
                'enthusiasm': 0.7,
                'humor': 0.4,
                'technical_depth': 0.5,
                'empathy': 0.6,
                'verbosity': 0.5,
            },
            
            # Conversation history
            'conversation_history': [],
            
            # Evolution metrics
            'evolution_metrics': {
                'total_adaptations': 0,
                'largest_personality_change': 0.0,
                'stability_score': 1.0,
                'learning_progression': []
            },
            
            # User preferences inferred over time
            'inferred_preferences': {
                'preferred_response_length': 'medium',
                'preferred_tone': 'balanced',
                'topics_of_interest': [],
                'communication_patterns': {}
            },
            
            # Quality metrics
            'quality_metrics': {
                'average_engagement': 0.0,
                'response_satisfaction': 0.0,
                'conversation_flow': 0.0,
                'total_evaluations': 0
            }
        }
        
        return profile
    
    def get_all_user_ids(self) -> List[str]:
        """Get list of all user IDs with profiles"""
        try:
            user_files = list(self.storage_dir.glob("*.json"))
            user_ids = [f.stem for f in user_files if not f.name.endswith('.backup')]
            return user_ids
        except Exception as e:
            logger.error(f"Error getting user IDs: {e}")
            return []
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistical summary for a user"""
        try:
            profile = self.get_user_profile(user_id)
            
            stats = {
                'user_id': user_id,
                'total_conversations': profile.get('conversation_count', 0),
                'created_at': profile.get('created_at'),
                'last_active': profile.get('last_updated'),
                'personality_vector': profile.get('personality_vector', {}),
                'evolution_metrics': profile.get('evolution_metrics', {}),
                'quality_metrics': profile.get('quality_metrics', {})
            }
            
            # Calculate days since creation
            if stats['created_at']:
                try:
                    created = datetime.fromisoformat(stats['created_at'].replace('Z', '+00:00'))
                    days_active = (datetime.now() - created).days
                    stats['days_active'] = days_active
                except:
                    stats['days_active'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats for user {user_id}: {e}")
            return {'error': str(e)}
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global statistics across all users"""
        try:
            user_ids = self.get_all_user_ids()
            total_users = len(user_ids)
            
            if total_users == 0:
                return {
                    'total_users': 0,
                    'total_conversations': 0,
                    'average_conversations_per_user': 0.0
                }
            
            total_conversations = 0
            active_users_week = 0
            personality_distributions = {}
            
            # Aggregate stats from all users
            for user_id in user_ids:
                try:
                    profile = self.get_user_profile(user_id)
                    total_conversations += profile.get('conversation_count', 0)
                    
                    # Check if active in last week
                    last_updated = profile.get('last_updated')
                    if last_updated:
                        try:
                            last_update = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                            days_since_update = (datetime.now() - last_update).days
                            if days_since_update <= 7:
                                active_users_week += 1
                        except:
                            pass
                    
                    # Aggregate personality distributions
                    personality = profile.get('personality_vector', {})
                    for dimension, value in personality.items():
                        if dimension not in personality_distributions:
                            personality_distributions[dimension] = []
                        personality_distributions[dimension].append(value)
                        
                except Exception as e:
                    logger.warning(f"Error processing user {user_id} for global stats: {e}")
                    continue
            
            # Calculate averages
            avg_conversations = total_conversations / total_users if total_users > 0 else 0
            
            # Calculate personality averages
            personality_averages = {}
            for dimension, values in personality_distributions.items():
                if values:
                    personality_averages[dimension] = sum(values) / len(values)
            
            return {
                'total_users': total_users,
                'total_conversations': total_conversations,
                'average_conversations_per_user': avg_conversations,
                'active_users_last_week': active_users_week,
                'personality_averages': personality_averages,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating global stats: {e}")
            return {'error': str(e)}
    
    async def add_conversation_entry(self, user_id: str, entry: Dict[str, Any]):
        """Add a new conversation entry to user history"""
        try:
            profile = self.get_user_profile(user_id)
            
            # Ensure conversation_history exists
            if 'conversation_history' not in profile:
                profile['conversation_history'] = []
            
            # Add new entry with timestamp
            entry['timestamp'] = datetime.now().isoformat()
            profile['conversation_history'].append(entry)
            
            # Keep only last 50 conversations for performance
            profile['conversation_history'] = profile['conversation_history'][-50:]
            
            # Update conversation count
            profile['conversation_count'] = profile.get('conversation_count', 0) + 1
            profile['last_updated'] = datetime.now().isoformat()
            
            # Save updated profile
            await self.update_user_profile(user_id, profile)
            
            logger.info(f"📝 Added conversation entry for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error adding conversation entry for user {user_id}: {e}")
    
    async def update_evolution_metrics(self, user_id: str, evolution_data: Dict[str, Any]):
        """Update evolution metrics for a user"""
        try:
            profile = self.get_user_profile(user_id)
            
            # Ensure evolution_metrics exists
            if 'evolution_metrics' not in profile:
                profile['evolution_metrics'] = {
                    'total_adaptations': 0,
                    'largest_personality_change': 0.0,
                    'stability_score': 1.0,
                    'learning_progression': []
                }
            
            metrics = profile['evolution_metrics']
            
            # Update metrics
            if 'evolution_changes' in evolution_data:
                changes = evolution_data['evolution_changes']
                if changes:
                    metrics['total_adaptations'] += 1
                    
                    # Calculate magnitude of change
                    change_magnitude = sum(abs(v) for v in changes.values() if isinstance(v, (int, float)))
                    if change_magnitude > metrics['largest_personality_change']:
                        metrics['largest_personality_change'] = change_magnitude
                    
                    # Add to learning progression
                    metrics['learning_progression'].append({
                        'timestamp': datetime.now().isoformat(),
                        'change_magnitude': change_magnitude,
                        'changes': changes.copy()
                    })
                    
                    # Keep only last 100 progression entries
                    metrics['learning_progression'] = metrics['learning_progression'][-100:]
            
            # Update stability score (how consistent personality is)
            if len(metrics['learning_progression']) > 5:
                recent_changes = metrics['learning_progression'][-5:]
                avg_change = sum(entry['change_magnitude'] for entry in recent_changes) / 5
                metrics['stability_score'] = max(0.0, 1.0 - avg_change)
            
            profile['evolution_metrics'] = metrics
            profile['last_updated'] = datetime.now().isoformat()
            
            # Save updated profile
            await self.update_user_profile(user_id, profile)
            
        except Exception as e:
            logger.error(f"❌ Error updating evolution metrics for user {user_id}: {e}")
    
    async def backup_all_profiles(self, backup_dir: str = None):
        """Create backup of all user profiles"""
        try:
            if backup_dir is None:
                backup_dir = f"./backups/profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            user_ids = self.get_all_user_ids()
            
            for user_id in user_ids:
                try:
                    profile = self.get_user_profile(user_id)
                    backup_file = backup_path / f"{user_id}.json"
                    
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        json.dump(profile, f, indent=2, ensure_ascii=False)
                        
                except Exception as e:
                    logger.error(f"Error backing up user {user_id}: {e}")
                    continue
            
            logger.info(f"💾 Backed up {len(user_ids)} profiles to {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"❌ Error creating backup: {e}")
            return None
    
    def clear_user_cache(self):
        """Clear in-memory cache"""
        self.user_cache.clear()
        logger.info("🗑️ User cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cached_users': len(self.user_cache),
            'cache_memory_estimate': len(str(self.user_cache)) * 2,  # Rough estimate in bytes
            'file_locks': len(self.file_locks)
        }