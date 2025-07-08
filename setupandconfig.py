#!/usr/bin/env python3
"""
Fixed Setup and Verification Script for Self-Evolving Voice Agent
Windows-compatible version without Unicode issues
"""

import os
import sys
import subprocess
import importlib
import json
from pathlib import Path
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step, description):
    """Print a step with formatting"""
    print(f"\nStep {step}: {description}")
    print("-" * 40)

def print_success(message):
    """Print success message"""
    print(f"SUCCESS: {message}")

def print_warning(message):
    """Print warning message"""
    print(f"WARNING: {message}")

def print_error(message):
    """Print error message"""
    print(f"ERROR: {message}")

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} is not compatible. Need Python 3.8+")
        return False

def install_requirements():
    """Install required packages"""
    requirements = [
        "livekit-agents>=0.8.0",
        "livekit-plugins-deepgram",
        "livekit-plugins-openai", 
        "livekit-plugins-silero",
        "textblob",
        "numpy",
        "python-dotenv"
    ]
    
    print("Installing required packages...")
    for package in requirements:
        try:
            print(f"Installing {package}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print_success(f"Installed {package}")
            else:
                print_error(f"Failed to install {package}: {result.stderr}")
                return False
        except Exception as e:
            print_error(f"Error installing {package}: {e}")
            return False
    
    return True

def check_imports():
    """Check if all required modules can be imported"""
    modules_to_check = [
        ("livekit.agents", "LiveKit Agents"),
        ("livekit.plugins.deepgram", "Deepgram Plugin"),
        ("livekit.plugins.openai", "OpenAI Plugin"),
        ("livekit.plugins.silero", "Silero Plugin"),
        ("textblob", "TextBlob"),
        ("numpy", "NumPy"),
        ("dotenv", "Python-dotenv")
    ]
    
    all_good = True
    for module_name, display_name in modules_to_check:
        try:
            importlib.import_module(module_name)
            print_success(f"{display_name} imported successfully")
        except ImportError as e:
            print_error(f"Failed to import {display_name}: {e}")
            all_good = False
    
    return all_good

def create_env_file():
    """Create or update .env file with required variables"""
    env_path = Path(".env")
    
    required_vars = {
        "LIVEKIT_URL": "wss://your-livekit-server.com",
        "LIVEKIT_API_KEY": "your-livekit-api-key",
        "LIVEKIT_API_SECRET": "your-livekit-api-secret",
        "DEEPGRAM_API_KEY": "your-deepgram-api-key",
        "OPENAI_API_KEY": "your-openai-api-key"
    }
    
    if env_path.exists():
        print_warning("Found existing .env file")
        with open(env_path, 'r') as f:
            existing_content = f.read()
        
        # Check which variables are missing
        missing_vars = []
        for var in required_vars:
            if f"{var}=" not in existing_content:
                missing_vars.append(var)
        
        if missing_vars:
            print_warning(f"Missing environment variables: {', '.join(missing_vars)}")
            print("Please add them to your .env file:")
            for var in missing_vars:
                print(f"  {var}={required_vars[var]}")
        else:
            print_success("All required environment variables found in .env")
    else:
        print("Creating .env file template...")
        with open(env_path, 'w') as f:
            f.write("# LiveKit Configuration\n")
            f.write("# Replace with your actual credentials\n\n")
            for var, example in required_vars.items():
                f.write(f"{var}={example}\n")
        
        print_success("Created .env file template")
        print_warning("Please update .env with your actual API keys and credentials!")

def verify_project_structure():
    """Verify all required files are present"""
    required_files = [
        "livekit_voice_agent.py",
        "evolution_engine.py", 
        "memory_manager.py",
        "evaluation_framework.py",
        "requirements.txt",
        ".env"
    ]
    
    all_present = True
    for file_name in required_files:
        if Path(file_name).exists():
            print_success(f"Found {file_name}")
        else:
            print_error(f"Missing {file_name}")
            all_present = False
    
    return all_present

def test_evolution_components():
    """Test that evolution components can be instantiated"""
    try:
        # Test imports
        from memory_manager import UserMemoryManager
        from evolution_engine import EvolutionEngine  
        from evaluation_framework import EvaluationFramework
        
        print_success("Evolution components imported successfully")
        
        # Test instantiation
        memory_manager = UserMemoryManager()
        evolution_engine = EvolutionEngine(memory_manager)
        evaluator = EvaluationFramework(memory_manager)
        
        print_success("Evolution components instantiated successfully")
        
        # Test basic functionality
        test_user_id = "test_user_setup"
        profile = memory_manager.get_user_profile(test_user_id)
        print_success(f"Memory manager working - created profile for {test_user_id}")
        
        return True
        
    except Exception as e:
        print_error(f"Evolution components test failed: {e}")
        return False

def create_demo_script():
    """Create a simple demo script for testing"""
    demo_script = '''#!/usr/bin/env python3
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
'''
    
    # Use UTF-8 encoding to avoid Windows encoding issues
    with open("test_evolution.py", "w", encoding='utf-8') as f:
        f.write(demo_script)
    
    print_success("Created test_evolution.py demo script")

def run_component_test():
    """Run the component test"""
    try:
        print("Running component test...")
        result = subprocess.run([sys.executable, "test_evolution.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_success("Component test passed!")
            print("Output:")
            print(result.stdout)
            return True
        else:
            print_error("Component test failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print_error("Component test timed out")
        return False
    except Exception as e:
        print_error(f"Error running component test: {e}")
        return False

def create_livekit_test_config():
    """Create a test configuration for LiveKit"""
    config = {
        "room": "test_room",
        "identity": "voice_agent",
        "user_metadata": {
            "user_id": "test_user_livekit",
            "session_type": "voice_test"
        }
    }
    
    with open("livekit_test_config.json", "w", encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print_success("Created LiveKit test configuration")

def print_next_steps():
    """Print next steps for the user"""
    print_header("SETUP COMPLETE - NEXT STEPS")
    
    print("""
1. SAVE THE MAIN VOICE AGENT FILE:
   - Copy the livekit_voice_agent.py from the artifacts above
   - Save it in your project directory

2. UPDATE YOUR .env FILE:
   - Add your actual LiveKit server URL and credentials
   - Add your Deepgram API key
   - Add your OpenAI API key

3. TEST THE COMPONENTS:
   python test_evolution.py

4. RUN THE VOICE AGENT:
   python livekit_voice_agent.py dev --room test_room

5. VERIFY EVERYTHING WORKS:
   python setup_fixed.py

6. READ THE DOCUMENTATION:
   - Check the comments in livekit_voice_agent.py
   - Review the LiveKit documentation
   - Test with different user IDs to see personality evolution
""")

def main():
    """Main setup function"""
    print_header("SELF-EVOLVING VOICE AGENT SETUP - FIXED VERSION")
    print("Setting up your LiveKit + Deepgram voice agent with personality evolution...")
    
    success = True
    
    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    if not check_python_version():
        success = False
        print("\nPlease install Python 3.8 or higher and try again.")
        return
    
    # Step 2: Install requirements
    print_step(2, "Installing Required Packages")
    if not install_requirements():
        success = False
        print_warning("Some packages failed to install. You may need to install them manually.")
    
    # Step 3: Check imports
    print_step(3, "Verifying Package Imports")
    if not check_imports():
        success = False
        print_warning("Some packages failed to import. Check the installation.")
    
    # Step 4: Create environment file
    print_step(4, "Setting Up Environment Configuration")
    create_env_file()
    
    # Step 5: Verify project structure
    print_step(5, "Verifying Project Structure")
    structure_ok = verify_project_structure()
    if not structure_ok:
        print_error("livekit_voice_agent.py is missing!")
        print("SOLUTION: Copy the livekit_voice_agent.py code from the artifacts and save it as a file.")
    
    # Step 6: Test evolution components (only if other files exist)
    if Path("evolution_engine.py").exists():
        print_step(6, "Testing Evolution Components")
        if not test_evolution_components():
            success = False
            print_warning("Evolution components test failed. Check the error messages above.")
    
    # Step 7: Create demo and test files
    print_step(7, "Creating Demo and Test Files")
    try:
        create_demo_script()
        create_livekit_test_config()
    except Exception as e:
        print_error(f"Error creating demo files: {e}")
    
    # Step 8: Run component test (only if components exist)
    if Path("evolution_engine.py").exists() and Path("test_evolution.py").exists():
        print_step(8, "Running Component Integration Test")
        if not run_component_test():
            print_warning("Component test failed, but setup may still work.")
    
    # Final status
    if success and structure_ok:
        print_header("SETUP SUCCESSFUL!")
        print("Your self-evolving voice agent is ready to use!")
    else:
        print_header("SETUP COMPLETED WITH WARNINGS")
        print("Some issues were encountered. Please review the errors above.")
        if not structure_ok:
            print("\nMAIN ISSUE: livekit_voice_agent.py is missing!")
            print("Copy the code from the artifacts above and save it as livekit_voice_agent.py")
    
    print_next_steps()

if __name__ == "__main__":
    main()