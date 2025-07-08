#!/usr/bin/env python3
"""
Simple Demo Script for Testing Voice Agent Components
"""

import asyncio
from memory_manager import UserMemoryManager
from evolution_engine import EvolutionEngine
from evaluation_framework import EvaluationFramework

async def test_evolution_pipeline():
    """Test the complete evolution pipeline"""
    print("Testing Evolution Pipeline...")
    
    # Initialize components
    memory_manager = UserMemoryManager()
    evolution_engine = EvolutionEngine(memory_manager)
    evaluator = EvaluationFramework(memory_manager)
    
    # Test user
    user_id = "demo_user"
    test_message = "Hey there! Can you help me with something technical?"
    
    print(f"Processing message: '{test_message}'")
    
    # Process through evolution engine
    result = await evolution_engine.process_message(user_id, test_message)
    
    print(f"Agent Response: {result['agent_response']}")
    print(f"Evolution Changes: {result.get('evolution_changes', {})}")
    
    # Evaluate the interaction
    evaluation = await evaluator.evaluate_interaction(
        user_id, test_message, result['agent_response'], 
        result.get('processing_time', 1.0)
    )
    
    print(f"Quality Score: {evaluation.get('overall_quality_score', 0):.3f}")
    print(f"Quality Category: {evaluation.get('quality_category', 'unknown')}")
    
    print("Evolution pipeline test completed!")

if __name__ == "__main__":
    asyncio.run(test_evolution_pipeline())
