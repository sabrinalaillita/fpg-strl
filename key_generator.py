import streamlit_authenticator as stauth

# Passwords that need to be hashed
passwords = ['admin', 'ceo']

# Generate hashed passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# Print out the hashed passwords
for pwd in hashed_passwords:
    print(pwd)