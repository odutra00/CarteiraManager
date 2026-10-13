from core.market_data import MarketDataService


def test_normalize_ticker():
    assert MarketDataService.normalize_ticker("VALE3") == "VALE3.SA"
    assert MarketDataService.normalize_ticker("petr4") == "PETR4.SA"
    assert MarketDataService.normalize_ticker("WEGE3.SA") == "WEGE3.SA"
    assert MarketDataService.normalize_ticker("^BVSP") == "^BVSP"
    assert MarketDataService.normalize_ticker("") == ""

