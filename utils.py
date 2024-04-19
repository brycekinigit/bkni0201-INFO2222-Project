def session_user(session):
    '''
    Returns the username of the currently logged in user, or None if authentication unsuccessful
    '''
    if "username" in session.keys():
        return session["username"]
    else:
        return None

def username_error(username):
    '''
    Returns an empty string if the username is valid, or an appropriate error message if not
    '''
    if len(username) < 3:
        return "Error: Username too short."
    valid_characters = "?!@#$%^&*()-_+"
    for i in username:
        if not (i.isalpha() or i.isnumeric or i in valid_characters):
            return "Error: Username contains invalid characters"
    return ""