import os
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

USER_API_BASE_URL = os.getenv("USER_API_BASE_URL")

def check_user_availability(email: str):
    """
    Checks whether a user exists based on their email.
    Returns a tuple (availability: bool, message: str)
    """
    url = f"{USER_API_BASE_URL}/user_exists_by_email?email={email}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("exists", False):
                return True, "user Available"
            else:
                return False, "user Not Available"
        else:
            return False, "user Not Available"
    except Exception:
        return False, "user Not Available"

def main():
    email = "test@gmail.com"  # Replace with desired email
    available, message = check_user_availability(email)
    print(f'{available} "{message}"')

if __name__ == "__main__":
    main()
