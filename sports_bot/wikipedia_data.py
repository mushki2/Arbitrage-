import wikipedia

def get_team_history(team_name: str) -> str:
    """
    Fetches a summary of a team's history from Wikipedia.

    Args:
        team_name: The name of the team to search for.

    Returns:
        A string containing a summary of the team's history,
        or an error message if the page is not found or is ambiguous.
    """
    try:
        # The `sentences=5` parameter limits the length of the summary.
        # `auto_suggest=False` prevents unexpected redirects.
        summary = wikipedia.summary(team_name, sentences=5, auto_suggest=False)
        return summary
    except wikipedia.exceptions.DisambiguationError:
        return f"Could not find a specific page for '{team_name}'. The name is ambiguous."
    except wikipedia.exceptions.PageError:
        return f"Could not find a Wikipedia page for '{team_name}'."
    except Exception as e:
        return f"An unexpected error occurred while fetching data from Wikipedia: {e}"

if __name__ == '__main__':
    # Example usage for local testing
    team1 = "Boston Celtics"
    team2 = "Real Madrid CF"
    invalid_team = "MadeUp Football Team 123"

    print(f"--- Fetching history for {team1} ---")
    history1 = get_team_history(team1)
    print(history1)

    print(f"\\n--- Fetching history for {team2} ---")
    history2 = get_team_history(team2)
    print(history2)

    print(f"\\n--- Fetching history for {invalid_team} ---")
    history3 = get_team_history(invalid_team)
    print(history3)
