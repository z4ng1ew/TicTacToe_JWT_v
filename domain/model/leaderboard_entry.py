from dataclasses import dataclass


@dataclass
class LeaderboardEntry:
    user_id:   str
    login:     str
    wins:      int
    losses:    int
    draws:     int
    win_ratio: float

    def to_dict(self) -> dict:
        return {
            "user_id":   self.user_id,
            "login":     self.login,
            "wins":      self.wins,
            "losses":    self.losses,
            "draws":     self.draws,
            "win_ratio": round(self.win_ratio, 3),
        }
