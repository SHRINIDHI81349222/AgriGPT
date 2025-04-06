import streamlit_authenticator as stauth

# Replace with real passwords
passwords = ['test123', 'admin123']
hashed_passwords = stauth.Hasher(passwords).generate()
print(hashed_passwords)
