def find_arbitrage_opportunities(events):
    """
    Analyzes a list of sports events to find arbitrage opportunities.

    An arbitrage opportunity exists if the sum of the reciprocals of the best odds
    for all outcomes in a match is less than 1.

    Formula: (1 / best_odd_outcome_A) + (1 / best_odd_outcome_B) < 1

    Args:
        events (list): A list of event data, typically from the Odds API.
                       Each event should have a list of bookmakers, and each
                       bookmaker should offer odds for the 'h2h' (head-to-head) market.

    Returns:
        list: A list of dictionaries, where each dictionary represents a
              found arbitrage opportunity and contains details about the match,
              the profitable odds, the bookmakers, and the potential profit margin.
    """
    arbitrage_opportunities = []

    if not events:
        return arbitrage_opportunities

    for event in events:
        home_team = event.get('home_team')
        away_team = event.get('away_team')
        bookmakers = event.get('bookmakers', [])

        best_odds_home = 0
        best_odds_away = 0
        bookmaker_home = None
        bookmaker_away = None

        # Find the best odds for each outcome across all bookmakers
        for bookie in bookmakers:
            for market in bookie.get('markets', []):
                if market.get('key') == 'h2h':
                    outcomes = market.get('outcomes', [])
                    # outcomes[0] is typically the home team, outcomes[1] is the away team
                    if len(outcomes) == 2:
                        if outcomes[0]['name'] == home_team and outcomes[0]['price'] > best_odds_home:
                            best_odds_home = outcomes[0]['price']
                            bookmaker_home = bookie['title']
                        elif outcomes[1]['name'] == away_team and outcomes[1]['price'] > best_odds_away:
                            best_odds_away = outcomes[1]['price']
                            bookmaker_away = bookie['title']

        # Check for arbitrage if we found valid odds
        if best_odds_home > 0 and best_odds_away > 0:
            arbitrage_value = (1 / best_odds_home) + (1 / best_odds_away)

            if arbitrage_value < 1:
                profit_margin = (1 - arbitrage_value) * 100
                opportunity = {
                    'match': f"{home_team} vs {away_team}",
                    'sport': event.get('sport_title'),
                    'arbitrage_value': arbitrage_value,
                    'profit_margin_percent': round(profit_margin, 2),
                    'bets': [
                        {'team': home_team, 'odds': best_odds_home, 'bookmaker': bookmaker_home},
                        {'team': away_team, 'odds': best_odds_away, 'bookmaker': bookmaker_away}
                    ]
                }
                arbitrage_opportunities.append(opportunity)

    return arbitrage_opportunities

if __name__ == '__main__':
    # Example usage with mock data
    mock_events_data = [
        {
            "id": "mock_id_1",
            "sport_key": "basketball_nba",
            "sport_title": "NBA",
            "home_team": "Team A",
            "away_team": "Team B",
            "bookmakers": [
                {
                    "key": "bookie_a", "title": "Bookmaker A",
                    "markets": [{"key": "h2h", "outcomes": [{"name": "Team A", "price": 2.15}, {"name": "Team B", "price": 1.80}]}]
                },
                {
                    "key": "bookie_b", "title": "Bookmaker B",
                    "markets": [{"key": "h2h", "outcomes": [{"name": "Team A", "price": 1.95}, {"name": "Team B", "price": 1.95}]}]
                },
                {
                    "key": "bookie_c", "title": "Bookmaker C",
                    "markets": [{"key": "h2h", "outcomes": [{"name": "Team A", "price": 2.20}, {"name": "Team B", "price": 1.75}]}]
                }
            ]
        },
        {
            "id": "mock_id_2", # No arbitrage here
            "sport_key": "soccer_epl",
            "sport_title": "English Premier League",
            "home_team": "Team C",
            "away_team": "Team D",
            "bookmakers": [
                 {
                    "key": "bookie_a", "title": "Bookmaker A",
                    "markets": [{"key": "h2h", "outcomes": [{"name": "Team C", "price": 1.5}, {"name": "Team D", "price": 2.5}]}]
                },
                {
                    "key": "bookie_b", "title": "Bookmaker B",
                    "markets": [{"key": "h2h", "outcomes": [{"name": "Team C", "price": 1.55}, {"name": "Team D", "price": 2.4}]}]
                }
            ]
        }
    ]

    print("--- Searching for Arbitrage Opportunities ---")
    opportunities = find_arbitrage_opportunities(mock_events_data)

    if opportunities:
        print(f"Found {len(opportunities)} arbitrage opportunity/ies!\\n")
        for op in opportunities:
            print(f"Match: {op['match']} ({op['sport']})")
            print(f"  Profit Margin: {op['profit_margin_percent']}%")
            print("  Bets to place:")
            for bet in op['bets']:
                print(f"    - Bet on {bet['team']} at odds {bet['odds']} with {bet['bookmaker']}")
            print("-" * 20)
    else:
        print("No arbitrage opportunities found in the mock data.")

    # Manually check the math for the example: 1/2.20 + 1/1.80 = 0.4545 + 0.5555 = 1.01 (No arbitrage)
    # Let's adjust mock data to create one: Team A @ 2.20, Team B @ 1.95
    # 1/2.20 + 1/1.95 = 0.4545 + 0.5128 = 0.9673 (< 1, arbitrage!)
    mock_events_data[0]['bookmakers'][1]['markets'][0]['outcomes'][1]['price'] = 1.95 # From Bookie B
    mock_events_data[0]['bookmakers'][0]['markets'][0]['outcomes'][0]['price'] = 2.20 # From Bookie A (updated)

    print("\\n--- Searching again with modified data to force an opportunity ---")
    opportunities = find_arbitrage_opportunities(mock_events_data)
    if opportunities:
        print(f"Found {len(opportunities)} arbitrage opportunity/ies!\\n")
        for op in opportunities:
            print(f"Match: {op['match']} ({op['sport']})")
            print(f"  Profit Margin: {op['profit_margin_percent']}%")
            print("  Bets to place:")
            for bet in op['bets']:
                print(f"    - Bet on {bet['team']} at odds {bet['odds']} with {bet['bookmaker']}")
            print("-" * 20)
