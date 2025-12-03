def prediction(prices: list):
    """
    Simple AI prediction engine using python
    Input: last N prices
    Output: 'buy', 'hold', 'sell'
    """

    if len(prices) < 3:
        return "not enough data"

    # calculate  momentum-trend
    current = prices[-1]
    previous = prices[-2]
    older = prices[-3]

    # %change
    change1 = (current - previous) / previous * 100
    change2 = (previous- older) / older * 100

    avg_change = (change1 + change2) / 2 

    # logic

    if avg_change > 2 :
        return "buy"
    elif avg_change < -2:
        return "sell"
    else: return "hold"