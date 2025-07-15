"""
DEBUG SCRIPT: Trace coaching object creation and session state management
Run this script to identify why MCQ input is being ignored for selenium code.

INSTRUCTIONS:
1. Save this as debug_coaching_state.py in your project root
2. Run: python debug_coaching_state.py
3. Paste selenium code when prompted
4. Type "C" when MCQ appears
5. Copy ALL output and send to Claude

This will trace exactly what's happening with coaching objects.
"""
import streamlit as st
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_session_state():
    """Debug current session state for coaching objects."""
    print("\n" + "="*60)
    print("🔍 SESSION STATE ANALYSIS")
    print("="*60)
    
    # Check if we're running in Streamlit context
    try:
        # Check main session state keys
        keys_to_check = [
            'coaching_state',
            'adaptive_coach', 
            'session',
            'persistent_coaching_state',
            'persistent_adaptive_coach'
        ]
        
        print(f"📊 Session State Keys Found:")
        for key in keys_to_check:
            if hasattr(st.session_state, key) and key in st.session_state:
                obj = st.session_state[key]
                obj_id = id(obj) if obj else 'None'
                obj_type = type(obj).__name__ if obj else 'None'
                print(f"  ✅ {key}: {obj_type} (ID: {obj_id})")
            else:
                print(f"  ❌ {key}: NOT FOUND")
        
        # Check session coaching state specifically
        if hasattr(st.session_state, 'session') and st.session_state.session:
            session = st.session_state.session
            if hasattr(session, 'coaching_state') and session.coaching_state:
                session_coaching_id = id(session.coaching_state)
                print(f"  📋 session.coaching_state: {type(session.coaching_state).__name__} (ID: {session_coaching_id})")
                
                # Check if session coaching state matches global one
                if 'coaching_state' in st.session_state:
                    global_coaching_id = id(st.session_state.coaching_state)
                    match = session_coaching_id == global_coaching_id
                    print(f"  🔗 Coaching state match: {match} ({'✅' if match else '❌'})")
            else:
                print(f"  ❌ session.coaching_state: NOT FOUND")
        
    except Exception as e:
        print(f"❌ Error accessing session state: {e}")
        print("💡 This script needs to run in Streamlit context")

def debug_coaching_integration():
    """Debug the coaching integration system."""
    print("\n" + "="*60)
    print("🔍 COACHING INTEGRATION ANALYSIS")
    print("="*60)
    
    try:
        from core.coaching_integration import CoachingIntegration
        
        print("✅ CoachingIntegration imported successfully")
        
        # Test get_existing_coaching_system
        print("\n🧪 Testing get_existing_coaching_system():")
        try:
            coaching_state, adaptive_coach = CoachingIntegration.get_existing_coaching_system()
            print(f"  ✅ coaching_state: {type(coaching_state).__name__} (ID: {id(coaching_state)})")
            print(f"  ✅ adaptive_coach: {type(adaptive_coach).__name__} (ID: {id(adaptive_coach)})")
            
            # Test calling it again - should return SAME objects
            print("\n🔄 Testing persistence - calling again:")
            coaching_state2, adaptive_coach2 = CoachingIntegration.get_existing_coaching_system()
            
            state_match = id(coaching_state) == id(coaching_state2)
            coach_match = id(adaptive_coach) == id(adaptive_coach2)
            
            print(f"  🔗 coaching_state persistence: {state_match} ({'✅' if state_match else '❌'})")
            print(f"  🔗 adaptive_coach persistence: {coach_match} ({'✅' if coach_match else '❌'})")
            
            if not state_match or not coach_match:
                print("  🚨 PERSISTENCE FAILURE: New objects created each time!")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")

def debug_handlers_imports():
    """Debug what's being imported and created in handlers."""
    print("\n" + "="*60)
    print("🔍 HANDLERS.PY ANALYSIS")
    print("="*60)
    
    try:
        from ui.handlers import InputHandler
        print("✅ InputHandler imported successfully")
        
        # Check if handlers.py has any direct AdaptiveCoach imports
        import ui.handlers
        import inspect
        
        print(f"\n📄 handlers.py source analysis:")
        source = inspect.getsource(ui.handlers)
        
        # Look for problematic patterns
        problematic_patterns = [
            "AdaptiveCoach(",
            "from .adaptive_coach import AdaptiveCoach",
            "from core.adaptive_coach import AdaptiveCoach",
            "adaptive_coach = AdaptiveCoach"
        ]
        
        for pattern in problematic_patterns:
            if pattern in source:
                print(f"  🚨 FOUND: {pattern}")
            else:
                print(f"  ✅ Clean: {pattern}")
        
        # Check for coaching integration usage
        if "CoachingIntegration" in source:
            print(f"  ✅ Uses CoachingIntegration")
        else:
            print(f"  ❌ Missing CoachingIntegration usage")
            
    except Exception as e:
        print(f"❌ Error analyzing handlers: {e}")

def trace_mcq_generation_vs_input():
    """Trace the MCQ generation vs input processing flow."""
    print("\n" + "="*60)
    print("🔍 MCQ GENERATION VS INPUT PROCESSING TRACE")
    print("="*60)
    
    print("🎯 This will help identify object ID differences:")
    print("1. When MCQ is generated (session_manager.py)")
    print("2. When input is processed (ui/handlers.py)")
    print("3. Check if same coaching objects are used")
    
    # This would need to be run during actual MCQ interaction
    print("\n💡 To complete this trace:")
    print("   - Paste selenium code")
    print("   - Note coaching object IDs when MCQ appears")
    print("   - Type 'C' and note coaching object IDs during input processing")
    print("   - Compare IDs to see if they match")

def main():
    """Main debug function."""
    print("🚨 CodeClimbAI MCQ Bug Debug Script")
    print("="*60)
    print("This script will help identify why MCQ input is ignored for selenium code.")
    print("Make sure you're running this while Streamlit app is active!")
    
    # Check if we're in Streamlit context
    try:
        import streamlit as st
        if 'session_state' not in dir(st):
            print("⚠️  WARNING: Not in Streamlit context - some checks will fail")
    except:
        print("⚠️  WARNING: Streamlit not available - some checks will fail")
    
    debug_session_state()
    debug_coaching_integration() 
    debug_handlers_imports()
    trace_mcq_generation_vs_input()
    
    print("\n" + "="*60)
    print("🎯 NEXT STEPS:")
    print("="*60)
    print("1. Run the actual app with selenium code")
    print("2. When MCQ appears, check the coaching object IDs in debug messages")
    print("3. Type 'C' and check if different coaching object IDs are used")
    print("4. Send ALL output to Claude for analysis")
    print("\n📋 Copy everything above and send to Claude!")

if __name__ == "__main__":
    main()
