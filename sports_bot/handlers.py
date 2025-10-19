from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from odds_api import get_sports, get_odds
from wikipedia_data import get_team_history
from sentiment_scraper import get_twitter_sentiment
from gemini_brain import get_ai_prediction
from arbitrage_engine import find_arbitrage_opportunities

# --- Main Menu ---
def get_main_menu():
    """Returns the main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("⚽ Sports", callback_data='sports'), InlineKeyboardButton("📊 Arbitrage", callback_data='arbitrage')],
        [InlineKeyboardButton("🏠 Home", callback_data='home')]
    ]
    return InlineKeyboardMarkup(keyboard)

def start(update: Update, context):
    """Sends a welcome message and the main menu."""
    update.message.reply_text(
        'Welcome to the Sports Betting Bot! Please choose an option:',
        reply_markup=get_main_menu()
    )

def handle_home(update: Update, context):
    """Handles the 'Home' button click."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Welcome back! Please choose an option:',
        reply_markup=get_main_menu()
    )

# --- Feature Handlers ---

def handle_sports(update: Update, context):
    """Fetches and displays a list of available sports."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Fetching sports list...")

    sports = get_sports()
    if sports:
        keyboard = []
        for sport in sports[:10]:  # Limit to 10 sports for readability
            keyboard.append([InlineKeyboardButton(sport['title'], callback_data=f"sport_{sport['key']}")])
        keyboard.append([InlineKeyboardButton("« Back to Home", callback_data='home')])
        query.edit_message_text(text="Please select a sport:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        query.edit_message_text(text="Could not fetch sports list. Please try again later.", reply_markup=get_main_menu())

def handle_arbitrage(update: Update, context):
    """Fetches odds for multiple popular sports and finds arbitrage opportunities."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Analyzing odds for arbitrage opportunities across popular sports...")

    popular_sports = ['americanfootball_nfl', 'basketball_nba', 'soccer_epl']
    all_opportunities = []

    for sport in popular_sports:
        events = get_odds(sport)
        if events:
            all_opportunities.extend(find_arbitrage_opportunities(events))

    if not all_opportunities:
        query.edit_message_text(text="No arbitrage opportunities found at the moment.", reply_markup=get_main_menu())
        return

    response = "Arbitrage Opportunities Found!\n\n"
    for op in all_opportunities:
        response += f"**Match:** {op['match']} ({op['sport']})\n"
        response += f"**Profit:** {op['profit_margin_percent']}% \n"
        for bet in op['bets']:
            response += f"- Bet on **{bet['team']}** at **{bet['odds']}** with **{bet['bookmaker']}**\n"
        response += "\n"

    query.edit_message_text(text=response, reply_markup=get_main_menu())

def handle_sport_selection(update: Update, context):
    """Handles the selection of a sport, then shows upcoming events as buttons."""
    query = update.callback_query
    sport_key = query.data.split('_')[1]
    context.user_data['selected_sport'] = sport_key  # Store sport for later
    query.answer()
    query.edit_message_text(text=f"Fetching upcoming events for {sport_key}...")

    events = get_odds(sport_key)
    if not events:
        query.edit_message_text(text=f"No upcoming events found for {sport_key}.", reply_markup=get_main_menu())
        return

    keyboard = []
    for event in events[:5]:  # Limit to 5 events for readability
        event_id = event['id']
        button_text = f"{event['home_team']} vs {event['away_team']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"event_{event_id}")])

    keyboard.append([InlineKeyboardButton("« Back to Sports", callback_data='sports')])
    query.edit_message_text(text="Please select a match:", reply_markup=InlineKeyboardMarkup(keyboard))

def handle_event_selection(update: Update, context):
    """After a user selects an event, show them analysis options."""
    query = update.callback_query
    event_id = query.data.split('_')[1]

    # Fetch all events for the sport again to find the selected one
    sport_key = context.user_data.get('selected_sport')
    if not sport_key:
        query.edit_message_text("Error: Sport context lost. Please start over.", reply_markup=get_main_menu())
        return

    events = get_odds(sport_key)
    selected_event = next((e for e in events if e['id'] == event_id), None)

    if not selected_event:
        query.edit_message_text("Error: Could not find event details. Please try again.", reply_markup=get_main_menu())
        return

    context.user_data['selected_event'] = selected_event
    home_team = selected_event['home_team']
    away_team = selected_event['away_team']

    keyboard = [
        [InlineKeyboardButton("🤖 Run AI Analysis", callback_data='run_ai_analysis')],
        [InlineKeyboardButton(f"📜 Get History: {home_team}", callback_data='get_history_home')],
        [InlineKeyboardButton(f"📜 Get History: {away_team}", callback_data='get_history_away')],
        [InlineKeyboardButton("« Back to Events", callback_data=f"sport_{sport_key}")]
    ]
    query.edit_message_text(f"You selected: {home_team} vs {away_team}", reply_markup=InlineKeyboardMarkup(keyboard))


def run_ai_analysis(update: Update, context):
    """Runs the full AI analysis pipeline for the selected match."""
    query = update.callback_query
    query.answer()

    selected_event = context.user_data.get('selected_event')
    if not selected_event:
        query.edit_message_text("Error: No event selected. Please start over.", reply_markup=get_main_menu())
        return

    home_team = selected_event['home_team']
    away_team = selected_event['away_team']
    query.edit_message_text(text=f"🤖 Running AI analysis for {home_team} vs {away_team}...")

    # 1. Extract odds from the selected event (Robustly)
    best_home_odds, best_away_odds = 0, 0
    for bookie in selected_event.get('bookmakers', []):
        for market in bookie.get('markets', []):
            if market.get('key') == 'h2h':
                outcomes = market.get('outcomes', [])
                if len(outcomes) == 2:
                    if outcomes[0]['name'] == home_team and outcomes[0]['price'] > best_home_odds:
                        best_home_odds = outcomes[0]['price']
                    elif outcomes[1]['name'] == away_team and outcomes[1]['price'] > best_away_odds:
                        best_away_odds = outcomes[1]['price']

    odds_data = {'home_team_odds': best_home_odds or "N/A", 'away_team_odds': best_away_odds or "N/A"}

    # 2. Fetch historical data
    historical_data = {
        'home_team_history': get_team_history(home_team),
        'away_team_history': get_team_history(away_team)
    }

    # 3. Get sentiment analysis
    sentiment_data = get_twitter_sentiment(f"{home_team} vs {away_team}")

    # 4. Get AI prediction
    prediction = get_ai_prediction(home_team, away_team, odds_data, sentiment_data, historical_data)

    sport_key = context.user_data.get('selected_sport')
    keyboard = [[InlineKeyboardButton("« Back to Events", callback_data=f"sport_{sport_key}")]]
    query.edit_message_text(text=prediction, reply_markup=InlineKeyboardMarkup(keyboard))

def get_history(update: Update, context):
    """Fetches and displays the Wikipedia history for the selected team."""
    query = update.callback_query
    team_type = query.data.split('_')[-1] # 'home' or 'away'

    selected_event = context.user_data.get('selected_event')
    if not selected_event:
        query.edit_message_text("Error: No event selected. Please start over.", reply_markup=get_main_menu())
        return

    team_name = selected_event['home_team'] if team_type == 'home' else selected_event['away_team']
    query.answer()
    query.edit_message_text(text=f"📜 Fetching history for {team_name}...")

    history = get_team_history(team_name)

    sport_key = context.user_data.get('selected_sport')
    keyboard = [[InlineKeyboardButton("« Back to Events", callback_data=f"sport_{sport_key}")]]
    query.edit_message_text(text=history, reply_markup=InlineKeyboardMarkup(keyboard))

# Note: The handlers are now registered directly in `app.py` using the dispatcher.
# This `handle_update` function is no longer used and has been removed for clarity.
