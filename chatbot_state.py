# chatbot_state.py
user_sessions = {}

def get_user_session(user_id):
    # Initialize session if not exists
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "step": "start",  # Initial step
            "data": {}        # Holds the grievance data
        }
    return user_sessions[user_id]

def reset_user_session(user_id):
    # Reset the user's session after form submission or cancellation
    if user_id in user_sessions:
        del user_sessions[user_id]
