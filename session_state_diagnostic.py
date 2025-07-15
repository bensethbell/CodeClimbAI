"""
DIAGNOSTIC SCRIPT: Complete Session State Analysis
Run this to trace exactly why coaching objects are being recreated.

CRITICAL DISCOVERY: The issue is likely in how Streamlit handles session_state
keys during component reruns, causing the persistent keys to be lost.
"""

def trace_session_state_keys():
    """Trace which session state keys exist and their stability."""
    print("🔍 SESSION STATE KEY ANALYSIS")
    print("=" * 50)
    
    import streamlit as st
    
    # Check all session state keys
    all_keys = list(st.session_state.keys())
    print(f"📊 Total session state keys: {len(all_keys)}")
    
    # Group keys by category
    coaching_keys = [k for k in all_keys if 'coaching' in k.lower()]
    persistent_keys = [k for k in all_keys if 'persistent' in k.lower()]
    session_keys = [k for k in all_keys if 'session' in k.lower()]
    
    print(f"\n🎯 Coaching-related keys: {coaching_keys}")
    print(f"🔒 Persistent keys: {persistent_keys}")
    print(f"📋 Session keys: {session_keys}")
    
    # Check for the specific problem keys
    problem_indicators = []
    
    if 'persistent_coaching_state' not in all_keys:
        problem_indicators.append("❌ persistent_coaching_state MISSING")
    else:
        state_obj = st.session_state.persistent_coaching_state
        problem_indicators.append(f"✅ persistent_coaching_state EXISTS (ID: {id(state_obj)})")
    
    if 'persistent_adaptive_coach' not in all_keys:
        problem_indicators.append("❌ persistent_adaptive_coach MISSING")
    else:
        coach_obj = st.session_state.persistent_adaptive_coach
        problem_indicators.append(f"✅ persistent_adaptive_coach EXISTS (ID: {id(coach_obj)})")
    
    # Check session coaching state consistency
    if hasattr(st.session_state, 'session') and st.session_state.session:
        session = st.session_state.session
        if hasattr(session, 'coaching_state') and session.coaching_state:
            session_state_id = id(session.coaching_state)
            
            if 'persistent_coaching_state' in all_keys:
                persistent_state_id = id(st.session_state.persistent_coaching_state)
                if session_state_id == persistent_state_id:
                    problem_indicators.append("✅ Session and persistent coaching states MATCH")
                else:
                    problem_indicators.append(f"🚨 Session coaching state ({session_state_id}) != persistent ({persistent_state_id})")
            else:
                problem_indicators.append("🚨 Session has coaching state but no persistent state exists")
        else:
            problem_indicators.append("⚠️ Session exists but has no coaching_state")
    else:
        problem_indicators.append("⚠️ No session object found")
    
    print(f"\n🚨 PROBLEM ANALYSIS:")
    for indicator in problem_indicators:
        print(f"  {indicator}")
    
    return problem_indicators

def trace_coaching_integration_calls():
    """Trace calls to CoachingIntegration methods."""
    print("\n🔧 COACHING INTEGRATION ANALYSIS")
    print("=" * 50)
    
    try:
        from core.coaching_integration import CoachingIntegration
        
        # Test the persistent system
        print("🧪 Testing get_existing_coaching_system()...")
        state1, coach1 = CoachingIntegration.get_existing_coaching_system()
        state1_id, coach1_id = id(state1), id(coach1)
        
        print(f"  First call: State ID {state1_id}, Coach ID {coach1_id}")
        
        # Call again to see if we get the same objects
        state2, coach2 = CoachingIntegration.get_existing_coaching_system()
        state2_id, coach2_id = id(state2), id(coach2)
        
        print(f"  Second call: State ID {state2_id}, Coach ID {coach2_id}")
        
        # Check consistency
        if state1_id == state2_id and coach1_id == coach2_id:
            print("  ✅ CONSISTENT: Same objects returned")
        else:
            print("  🚨 INCONSISTENT: Different objects returned!")
            print("  🚨 This confirms the coaching object recreation bug!")
            
        return state1_id == state2_id and coach1_id == coach2_id
        
    except Exception as e:
        print(f"  ❌ Error testing coaching integration: {e}")
        return False

def trace_streamlit_rerun_behavior():
    """Analyze how Streamlit reruns affect session state."""
    print("\n🔄 STREAMLIT RERUN BEHAVIOR ANALYSIS")
    print("=" * 50)
    
    import streamlit as st
    
    # Check if we're in a rerun
    if 'rerun_counter' not in st.session_state:
        st.session_state.rerun_counter = 0
    
    st.session_state.rerun_counter += 1
    current_run = st.session_state.rerun_counter
    
    print(f"📊 Current run number: {current_run}")
    
    # Track when persistent keys get lost
    if 'persistent_key_history' not in st.session_state:
        st.session_state.persistent_key_history = []
    
    current_persistent_keys = [k for k in st.session_state.keys() if 'persistent' in k]
    st.session_state.persistent_key_history.append({
        'run': current_run,
        'keys': current_persistent_keys.copy()
    })
    
    print(f"🔑 Persistent keys this run: {current_persistent_keys}")
    
    # Check for key loss across runs
    if len(st.session_state.persistent_key_history) > 1:
        previous_run = st.session_state.persistent_key_history[-2]
        current_run_data = st.session_state.persistent_key_history[-1]
        
        lost_keys = set(previous_run['keys']) - set(current_run_data['keys'])
        gained_keys = set(current_run_data['keys']) - set(previous_run['keys'])
        
        if lost_keys:
            print(f"  🚨 LOST persistent keys: {lost_keys}")
        if gained_keys:
            print(f"  ✅ GAINED persistent keys: {gained_keys}")
        if not lost_keys and not gained_keys:
            print(f"  ✅ Persistent keys stable across reruns")

def recommend_fix():
    """Provide specific fix recommendations based on analysis."""
    print("\n💡 FIX RECOMMENDATIONS")
    print("=" * 50)
    
    print("Based on the analysis, the fix strategy should be:")
    print()
    print("1. 🔒 STRENGTHEN session state persistence")
    print("   - Use more robust session state keys")
    print("   - Add defensive key recreation")
    print("   - Implement session state validation")
    print()
    print("2. 🔧 FIX coaching integration robustness")
    print("   - Always check key existence before access")
    print("   - Implement fallback recreation logic")
    print("   - Add coaching state synchronization validation")
    print()
    print("3. 🚨 CRITICAL: Add coaching object ID tracking")
    print("   - Log coaching object IDs at creation and use")
    print("   - Detect when different objects are being used")
    print("   - Force session state refresh when inconsistency detected")

def main():
    """Run complete diagnostic analysis."""
    print("🚨 CodeClimbAI MCQ Bug Diagnostic Analysis")
    print("=" * 60)
    print("This script analyzes why MCQ input is ignored for selenium code.")
    print("=" * 60)
    
    # Run all diagnostic checks
    session_indicators = trace_session_state_keys()
    integration_consistent = trace_coaching_integration_calls()
    trace_streamlit_rerun_behavior()
    recommend_fix()
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    # Determine the most likely root cause
    has_persistent_keys = any("persistent_coaching_state EXISTS" in ind for ind in session_indicators)
    has_key_mismatch = any("!=" in ind for ind in session_indicators)
    
    if not has_persistent_keys:
        print("🚨 ROOT CAUSE: Persistent session state keys are not being created")
        print("🔧 FIX: Check CoachingIntegration.get_existing_coaching_system() implementation")
    elif has_key_mismatch:
        print("🚨 ROOT CAUSE: Session and persistent coaching states are out of sync")
        print("🔧 FIX: Add coaching state synchronization in session_manager.py")
    elif not integration_consistent:
        print("🚨 ROOT CAUSE: CoachingIntegration returns different objects on each call")
        print("🔧 FIX: Fix coaching_integration.py persistent object management")
    else:
        print("🤔 ROOT CAUSE: Unknown - further investigation needed")
        print("🔧 NEXT: Add detailed logging to identify coaching object recreation points")
    
    print("\n📋 Copy this entire output and send to Claude for specific fix implementation!")

if __name__ == "__main__":
    main()
