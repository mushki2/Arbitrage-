import os
import google.generativeai as genai

# It's highly recommended to use environment variables for API keys.
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY')
if GEMINI_API_KEY != 'YOUR_GEMINI_API_KEY':
    genai.configure(api_key=GEMINI_API_KEY)

def _format_prompt(home_team, away_team, odds_data, sentiment_data, historical_data):
    """Formats the input data into a structured prompt for the Gemini model."""

    prompt = f"""
    Analyze the upcoming match between {home_team} and {away_team}.
    Based on the data provided below, please provide a confident prediction for the winner and the key reasoning behind your conclusion.

    **Match Data:**

    1.  **Vegas Odds:**
        *   Home Team ({home_team}): {odds_data.get('home_team_odds', 'N/A')}
        *   Away Team ({away_team}): {odds_data.get('away_team_odds', 'N/A')}

    2.  **Public Sentiment (from Twitter):**
        *   Positive Sentiment: {sentiment_data.get('positive_ratio', 0) * 100:.1f}%
        *   Neutral Sentiment: {sentiment_data.get('neutral_ratio', 0) * 100:.1f}%
        *   Negative Sentiment: {sentiment_data.get('negative_ratio', 0) * 100:.1f}%
        *   Total Tweets Analyzed: {sentiment_data.get('tweet_count', 0)}

    3.  **Historical Context (from Wikipedia):**
        *   {home_team} Summary: {historical_data.get('home_team_history', 'No data available.')}
        *   {away_team} Summary: {historical_data.get('away_team_history', 'No data available.')}

    **Your Task:**

    Return a short, confident prediction and a summary of your reasoning.
    """
    return prompt

def get_ai_prediction(home_team, away_team, odds_data, sentiment_data, historical_data):
    """
    Queries the Gemini AI model to get a prediction for a match.

    Returns:
        A string containing the AI's prediction and reasoning, or a mock response if the API key is not configured.
    """
    if GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY':
        # Return a mock response if the API key is not set
        print("INFO: Gemini API key not found. Returning a mock prediction.")
        mock_reasoning = f"The analysis suggests that the {home_team} have a slight edge due to stronger recent performance and more positive public sentiment. However, the {away_team}'s solid historical record makes them a formidable opponent."
        return f"**Prediction:** {home_team} to win.\n\n**Reasoning:**\n{mock_reasoning}"

    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = _format_prompt(home_team, away_team, odds_data, sentiment_data, historical_data)

        response = model.generate_content(prompt)

        return response.text
    except Exception as e:
        print(f"An error occurred while querying the Gemini API: {e}")
        return "Could not retrieve an AI prediction at this time."

if __name__ == '__main__':
    # Example usage for local testing
    home = "Boston Celtics"
    away = "Los Angeles Lakers"

    # Mock data for the prompt
    mock_odds = {'home_team_odds': 1.85, 'away_team_odds': 2.05}
    mock_sentiment = {'positive_ratio': 0.65, 'neutral_ratio': 0.20, 'negative_ratio': 0.15, 'tweet_count': 150}
    mock_history = {
        'home_team_history': 'The Boston Celtics are one of the most successful teams in NBA history, with 17 championships.',
        'away_team_history': 'The Los Angeles Lakers are a professional basketball team with a storied history, including 17 NBA championships.'
    }

    print(f"--- Generating AI Prediction for {home} vs {away} ---")
    prediction = get_ai_prediction(home, away, mock_odds, mock_sentiment, mock_history)
    print(prediction)
