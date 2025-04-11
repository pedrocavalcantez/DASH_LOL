from database.players import (
    get_player_stats,
    get_player_match_history,
    get_most_picked_champions,
)
from database.teams import (
    get_team_stats,
    get_team_match_history,
    get_team_most_picked_champions,
)
from database.champions import get_champion_stats, get_champion_match_history
from database.shared import (
    get_all_dates,
    get_all_columns,
    get_all_leagues,
    get_all_patches,
    get_all_players,
    get_all_teams,
)
from database.patch import get_patch_champion_stats
from database.champions_sinergys_counters import (
    get_best_allies,
    get_best_against,
    get_worst_against,
)
from database.head2head_players import (
    get_player_stats_in_period,
    get_head2head_stats,
    get_head2head_match_history,
)
from database.head2head_teams import (
    get_team_stats_in_period,
    get_head2head_stats_teams,
    get_head2head_match_history_teams,
)
from database.head2head_champions import (
    get_champion_stats_in_period,
    get_head2head_stats_champions,
    get_head2head_match_history_champions,
)


class DataProcessor:
    def get_player_stats(self, player_name=None, start_date=None, end_date=None):
        return get_player_stats(player_name, start_date, end_date)

    def get_player_match_history(self, player_name, start_date=None, end_date=None):
        return get_player_match_history(player_name, start_date, end_date)

    def get_team_stats(self, team_name=None, start_date=None, end_date=None):
        return get_team_stats(team_name, start_date, end_date)

    def get_team_match_history(self, team_name, start_date=None, end_date=None):
        return get_team_match_history(team_name, start_date, end_date)

    def get_team_most_picked_champions(
        self, team_name=None, start_date=None, end_date=None
    ):
        return get_team_most_picked_champions(team_name, start_date, end_date)

    def get_champion_stats(self, champion_name=None, start_date=None, end_date=None):
        return get_champion_stats(champion_name, start_date, end_date)

    def get_all_dates(self):
        return get_all_dates()

    def get_all_columns(self):
        return get_all_columns()

    def get_most_picked_champions(self, player_name, start_date=None, end_date=None):
        return get_most_picked_champions(player_name, start_date, end_date)

    def get_champion_stats(
        self, champion_name=None, start_date=None, end_date=None, leagues=None
    ):
        return get_champion_stats(champion_name, start_date, end_date, leagues)

    def get_all_leagues(self):
        return get_all_leagues()

    def get_champion_match_history(
        self, champion_name, start_date=None, end_date=None, leagues=None
    ):
        return get_champion_match_history(champion_name, start_date, end_date, leagues)

    def get_patch_champion_stats(self, patch, start_date, end_date, leagues=None):
        return get_patch_champion_stats(patch, start_date, end_date, leagues)

    def get_all_patches(self):
        return get_all_patches()

    def get_best_allies(self, champion, start_date, end_date, leagues=None):
        return get_best_allies(champion, start_date, end_date, leagues)

    def get_best_against(self, champion, start_date, end_date, leagues=None):
        return get_best_against(champion, start_date, end_date, leagues)

    def get_worst_against(self, champion, start_date, end_date, leagues=None):
        return get_worst_against(champion, start_date, end_date, leagues)

    def get_player_stats_in_period(self, player_name, start_date, end_date):
        return get_player_stats_in_period(player_name, start_date, end_date)

    def get_head2head_stats(self, player1, player2, start_date, end_date):
        return get_head2head_stats(player1, player2, start_date, end_date)

    def get_head2head_match_history(self, player1, player2, start_date, end_date):
        return get_head2head_match_history(player1, player2, start_date, end_date)

    def get_head2head_match_history_teams(self, team1, team2, start_date, end_date):
        return get_head2head_match_history_teams(team1, team2, start_date, end_date)

    def get_team_stats_in_period(self, team_name, start_date, end_date):
        return get_team_stats_in_period(team_name, start_date, end_date)

    def get_head2head_stats_teams(self, team1, team2, start_date, end_date):
        return get_head2head_stats_teams(team1, team2, start_date, end_date)

    def get_head2head_match_history_teams(self, team1, team2, start_date, end_date):
        return get_head2head_match_history_teams(team1, team2, start_date, end_date)

    def get_champion_stats_in_period(self, champion_name, start_date, end_date):
        return get_champion_stats_in_period(champion_name, start_date, end_date)

    def get_champion_stats_in_period(
        self, champion, start_date, end_date, leagues=None
    ):
        return get_champion_stats_in_period(champion, start_date, end_date, leagues)

    def get_head2head_stats_champions(
        self, champ1, champ2, start_date, end_date, leagues=None
    ):
        return get_head2head_stats_champions(
            champ1, champ2, start_date, end_date, leagues
        )

    def get_head2head_match_history_champions(
        self, champ1, champ2, start_date, end_date, leagues=None
    ):
        return get_head2head_match_history_champions(
            champ1, champ2, start_date, end_date, leagues
        )

    def get_all_players(self, league=None):
        return get_all_players(league)

    def get_all_teams(self, league=None):
        return get_all_teams(league)
