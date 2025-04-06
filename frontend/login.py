import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # ✅ adds parent folder

import streamlit as st
import streamlit_authenticator as stauth
from multi_agent_system import run_agents  # ✅ now this will work


# --- Auth Setup ---
names = ["Shrinidhi", "Admin"]
usernames = ["nidhi", "admin"]
hashed_passwords = [
    '$2b$12$7GEycxJcQpq9WBe2j/UoY.0eHDwU8Dc3XjSYGfCOQxWDa6wFnA/Nu',
    '$2b$12$0WDFrOGJsoMujxWEdylBcuKq7N9cCT6I68bg92T2Es.PnFJZnVXHe'
]

authenticator = stauth.Authenticate(
    names=names,
    usernames=usernames,
    passwords=hashed_passwords,
    cookie_name="agri_dashboard",
    key="abcdef",
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", "main")

# --- Main App ---
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome, {name} 👋")

    st.title("🌾 Sustainable Farming AI Assistant")
    query = st.text_input("Ask your farming question here:")

    if st.button("Submit") and query:
        with st.spinner("Thinking..."):
            response = run_agents(query)
        st.success("Done!")
        st.markdown(f"### 🧠 Answer:\n{response}")

elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
