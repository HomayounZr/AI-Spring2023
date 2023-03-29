import copy
import math
import random


class Player:
    def __init__(self, name, start_cell, wallet):
        self.name = name
        self.cell = start_cell
        self.wallet = wallet
        self.cell_no = 0

    def check_balance(self, amount):
        if self.wallet < amount:
            return False
        return True

    def pay(self, amount):
        self.wallet -= amount

    def increase(self, amount):
        self.wallet += amount

    def clone(self):
        player = Player(self.name, self.cell, self.wallet)
        player.cell_no = self.cell_no
        return player


class Cell:
    def __init__(self, cell_type, title, color, price):
        self.title = title
        self.color = color
        self.type = cell_type
        self.price = price
        self.owner: Player = None
        self.buildings = 0
        if self.type == 'PLACE':
            self.buildings = 0

    def can_purchase(self, player: Player):
        return player.check_balance(CELLS_INFO[self.title]['PRICE'])

    def purchase(self, player: Player):
        player.pay(CELLS_INFO[self.title]['PRICE'])
        self.owner = player

    def pay_rent(self, player: Player):
        amount = get_rent_property(CELLS_INFO[self.title], self.buildings)
        player.pay(amount)
        self.owner.increase(amount)

    def get_rent_price(self):
        if self.type == 'PLACE':
            return get_rent_property(CELLS_INFO[self.title], self.buildings)
        return self.price

    def is_upgradable(self, player: Player):
        if self.type == 'PLACE' and self.buildings < 5 and self.owner.name == player.name:
            if self.owner.check_balance(CELLS_INFO[self.title]['PRICE_PER_HOUSE']):
                return True
        return False

    def upgrade(self):
        self.owner.pay(CELLS_INFO[self.title]['PRICE_PER_HOUSE'])
        self.buildings += 1


class GameState:
    def __init__(self, board, players, player_turn):
        self.board = board
        self.players = players
        self.player_turn = player_turn

    def is_terminal(self):
        empty_players = 0
        for player in self.players:
            if player.wallet <= 0:
                empty_players += 1
        if empty_players == len(self.players) - 1:
            return True
        return False

    def utility(self):
        scores = []
        for player in self.players:
            scores.append(player.wallet)
        return scores

    def eval(self):
        evals = []
        for player in self.players:
            value = player.wallet
            for cell_no, cell in enumerate(self.board):
                cell: Cell = cell
                if cell.owner.name == player.name:
                    value += get_rent_property(CELLS_INFO[cell.title], cell.buildings)
                elif cell_no == player.cell_no:
                    value -= get_rent_property(CELLS_INFO[cell.title], cell.buildings)
            evals.append(value)
        return evals

    def get_player(self):
        if self.player_turn == 'MAX':
            return self.players[0]
        elif self.player_turn == 'MIN':
            return self.players[1]
        else:
            return None

    def get_actions(self, cell: Cell, player: Player):
        if cell.type == 'PASS':
            return ['PASS']
        elif cell.type == 'TAX':
            return ['TAX']
        elif cell.type == 'GOTO_JAIL':
            return ['JAIL']
        elif cell.type == 'JAIL':
            return ['']
        elif cell.type == 'SERVICE' or cell.type == 'RAILROAD':
            if cell.owner is None:
                return ['BUY', '']
            elif cell.owner.name == player.name:
                return ['']
            else:
                return ['PAY']
        elif cell.type == 'PLACE':
            if cell.owner is None:
                return ['BUY', '']
            elif cell.owner.name == player.name:
                return ['UPGRADE', '']
            else:
                return ['PAY']

    def result(self, player_index, cell_no, action):
        board = copy.deepcopy(self.board)
        players = copy.deepcopy(self.players)
        player = players[player_index]

        player_turn = 'MAX'
        if self.player_turn == 'MAX' or self.player_turn == 'MIN':
            player_turn = 'CHANCE'
        else:
            opponent_index = 1 - player_index
            if opponent_index == 1:
                player_turn = 'MAX'
            else:
                player_turn = 'MIN'

        player.cell_no = cell_no

        if action == 'PASS':
            player.increase(200)
        elif action == 'TAX':
            player.pay(200)
        elif action == 'GOTO_JAIL':
            player.pay(100)
            player.cell_no = 9 # index of jail in board
        elif action == 'PAY':
            player.pay(100)
        elif action == 'UPGRADE':
            cell = board[cell_no]
            if cell.is_upgradable(player):
                cell.upgrade()
        elif action == 'BUY':
            cell = board[cell_no]
            if cell.can_purchase(player):
                cell.purchase(player)
        else:
            pass

        return GameState(board, players, player_turn)


class Monopoly:
    def __init__(self, max_depth):
        self.max_depth = max_depth

    def get_chance(self, dice_sum):
        if dice_sum == 2:
            return 1/36
        elif dice_sum == 3:
            return 1/18
        elif dice_sum == 4:
            return 1/12
        elif dice_sum == 5:
            return 1/9
        elif dice_sum == 6:
            return 5/36
        elif dice_sum == 7:
            return 1/6
        elif dice_sum == 8:
            return 5/36
        elif dice_sum == 9:
            return 1/9
        elif dice_sum == 10:
            return 1/12
        elif dice_sum == 11:
            return 1/18
        elif dice_sum == 12:
            return 1/36
        else:
            return 0

    def expecti_minimax(self, state: GameState, to_move, depth):
        if state.is_terminal():
            return state.utility(), None

        if depth >= self.max_depth:
            return state.eval(), None

        if state.player_turn == 'MAX':
            v, m = -1 * math.inf, None
            for i in range(2, 13):
                total_value = 0
                # after rolling the dice we are in the change node
                new_cell = (state.players[0].cell_no + i) % len(state.board)
                new_players = copy.deepcopy(state.players)
                new_board = copy.deepcopy(state.board)
                new_players[0].cell_no = new_cell

                chance_state = GameState(new_board, new_players, 'CHANCE')

                # we compute value for every possible chance node
                value, move = self.expecti_minimax(chance_state, 'MIN', depth + 1)
                total_value += value * self.get_chance(i)
                if total_value > v:
                    v = total_value
                    m = chance_state

            return v, m

        if state.player_turn == 'MIN':
            v, m = math.inf, None
            for i in range(2, 13):
                total_value = 0
                # after rolling the dice we are in the change node
                new_cell = (state.players[1].cell_no + i) % len(state.board)
                new_players = copy.deepcopy(state.players)
                new_board = copy.deepcopy(state.board)
                new_players[1].cell_no = new_cell

                chance_state = GameState(new_board, new_players, 'CHANCE')

                # we compute value for every possible chance node
                value, move = self.expecti_minimax(chance_state, 'MAX', depth + 1)
                total_value += value * self.get_chance(i)
                if total_value < v:
                    v = total_value
                    m = chance_state

            return v, m

        if state.player_turn == 'CHANCE':
            if to_move == 'MAX':
                value, move = -1 * math.inf, None
                for action in state.get_actions(state.board[state.players[0].cell_no], state.players[0]):
                    v, m = self.expecti_minimax(state.result(0, state.players[0].cell_no, action), 'CHANCE', depth + 1)
                    if v > value:
                        value = v
                        move = m
                return value, move
            else:
                value, move = math.inf, None
                for action in state.get_actions(state.board[state.players[1].cell_no], state.players[1]):
                    v, m = self.expecti_minimax(state.result(1, state.players[1].cell_no, action), 'CHANCE', depth + 1)
                    if v < value:
                        value = v
                        move = m
                return value, move


class Main:
    def __init__(self):
        self.cells = self.init_cells()
        self.players = self.init_players()

    def init_players(self):
        players = []
        for i in range(2):
            players.append(Player(f'Player {i}', self.cells[0], 1500))
        return players

    def init_cells(self):
        cells = [Cell('PASS', 'COLLECT_200', '', None), Cell('PLACE', 'MEDITERRANEAN_AVENUE', 'BROWN', None),
                 Cell('PLACE', 'BALTIC_AVENUE', 'BROWN', None), Cell('TAX', 'INCOME_TAX', '', 200),
                 Cell('RAILROAD', 'READING_RAILROAD', '', 200), Cell('PLACE', 'ORIENTAL_AVENUE', 'BLUE', None),
                 Cell('PLACE', 'VERMONT_AVENUE', 'BLUE', None), Cell('PLACE', 'CONNECTICUT_AVENUE', 'BLUE', None),
                 Cell('JAIL', 'JAIL_OR_VISIT', '', 50), Cell('PLACE', 'STCHARLES_PLACE', 'PINK', None),
                 Cell('SERVICE', 'ELECTRIC_COMPANY', '', 150), Cell('PLACE', 'STATES_AVENUE', 'PINK', None),
                 Cell('PLACE', 'VIRGINIA_AVENUE', 'PINK', None), Cell('RAILROAD', 'PENNSYLVANIA_RAILROAD', '', 200),
                 Cell('PLACE', 'STJAMES_PLACE', 'ORANGE', None), Cell('PLACE', 'TENNESSEE_AVENUE', 'ORANGE', None),
                 Cell('PLACE', 'NEWYORK_AVENUE', 'ORANGE', None), Cell('PLACE', 'KENTUCKY_AVENUE', 'RED', None),
                 Cell('PLACE', 'IDIANA_AVENUE', 'RED', None), Cell('PLACE', 'ILLINOIS_AVENUE', 'RED', None),
                 Cell('RAILROAD', 'RO_RAILROAD', '', 200), Cell('PLACE', 'ATLANTIC_AVENUE', '', None),
                 Cell('PLACE', 'VENTNOR_AVENUE', '', None), Cell('PLACE', 'Collect 200 and pass', '', None),
                 Cell('SERVICE', 'WATER_WORKS', '', 150), Cell('PLACE', 'MARVIN_GARDENS', '', None),
                 Cell('GOTO_JAIL', 'GO_TO_JAIL', '', None), Cell('PLACE', 'PACIFIC_AVENUE', 'GREEN', None),
                 Cell('PLACE', 'NORTH_CAROLINA_AVENUE', 'GREEN', None),
                 Cell('PLACE', 'PENNSYLVANIA_AVENUE', 'GREEN', None),
                 Cell('RAILROAD', 'SHORT_LINE', '', 150), Cell('PLACE', 'PARK_PLACE', 'DARK_BLUE', None),
                 Cell('TAX', 'LUXURY_TAX', '', 100), Cell('PLACE', 'BOARD_WALK', '', None)]
        # cells[0] = Cell('COMMUNITY', 'COMMUNITY CHEST', '', 200)
        # cells[0] = Cell('CHANCE', 'Collect 200 and pass', '', 200)
        # cells[0] = Cell('COMMUNITY', 'Collect 200 and pass', '', 200)
        # cells[0] = Cell('PARKING', 'Collect 200 and pass', '', 200)
        # cells[0] = Cell('CHANCE', 'Collect 200 and pass', '', 200)
        # cells[0] = Cell('COMMUNITY', 'Collect 200 and pass', '', 200)
        # cells[0] = Cell('CHANCE', 'Collect 200 and pass', '', 200)

        return cells

    def run(self):
        print("===== Homayoun Zarei - 9822019 =====")
        print("===== Monopoly using Adversarial Search =====")

        player_turn = 0
        # state = GameState(self.cells, self.players, 'MAX')
        monopoly = Monopoly(4)
        while True:
            dice = random.randint(1, 6) + random.randint(1, 6)

            # after rolling the dice we are in the change node
            new_cell = (self.players[player_turn].cell_no + dice) % len(self.cells)
            self.players[player_turn].cell_no = new_cell

            state = GameState(self.cells, self.players, 'CHANCE')

            value, state = monopoly.expecti_minimax(state, 'MIN', 0)

            if state.is_terminal():
                print()
                print("===========================================")
                print("Game ended")
                print(value)
                break

            player_turn = (player_turn + 1) % 2


Main().run()


def get_rent_property(cell_info, buildings):
    if buildings == 0:
        return cell_info['RENT']
    elif buildings == 1:
        return cell_info['RENT_ONE_HOUSE']
    elif buildings == 2:
        return cell_info['RENT_TWO_HOUSES']
    elif buildings == 3:
        return cell_info['RENT_THREE_HOUSES']
    elif buildings == 4:
        return cell_info['RENT_FOUR_HOUSES']
    elif buildings == 5:
        return cell_info['RENT_HOTEL']
    else:
        return cell_info['RENT']


CELLS_INFO = {
    'MEDITERRANEAN_AVENUE': {
        'PRICE': 60,
        'PRICE_PER_HOUSE': 50,
        'RENT': 2,
        'RENT_ONE_HOUSE': 10,
        'RENT_TWO_HOUSES': 30,
        'RENT_THREE_HOUSES': 90,
        'RENT_FOUR_HOUSES': 160,
        'RENT_HOTEL': 250,
        'MORTGAGE': 30,
    },
    'BALTIC_AVENUE': {
        'PRICE': 60,
        'PRICE_PER_HOUSE': 50,
        'RENT': 4,
        'RENT_ONE_HOUSE': 20,
        'RENT_TWO_HOUSES': 60,
        'RENT_THREE_HOUSES': 180,
        'RENT_FOUR_HOUSES': 320,
        'RENT_HOTEL': 450,
        'MORTGAGE': 30,
    },
    'ORIENTAL_AVENUE': {
        'PRICE': 100,
        'PRICE_PER_HOUSE': 50,
        'RENT': 6,
        'RENT_ONE_HOUSE': 30,
        'RENT_TWO_HOUSES': 90,
        'RENT_THREE_HOUSES': 270,
        'RENT_FOUR_HOUSES': 400,
        'RENT_HOTEL': 550,
        'MORTGAGE': 50,
    },
    'VERMONT_AVENUE': {
        'PRICE': 100,
        'PRICE_PER_HOUSE': 50,
        'RENT': 6,
        'RENT_ONE_HOUSE': 30,
        'RENT_TWO_HOUSES': 90,
        'RENT_THREE_HOUSES': 270,
        'RENT_FOUR_HOUSES': 400,
        'RENT_HOTEL': 550,
        'MORTGAGE': 50,
    },
    'CONNECTICUT_AVENUE': {
        'PRICE': 120,
        'PRICE_PER_HOUSE': 50,
        'RENT': 8,
        'RENT_ONE_HOUSE': 40,
        'RENT_TWO_HOUSES': 100,
        'RENT_THREE_HOUSES': 300,
        'RENT_FOUR_HOUSES': 450,
        'RENT_HOTEL': 600,
        'MORTGAGE': 60,
    },
    'STCHARLES_PLACE': {
        'PRICE': 140,
        'PRICE_PER_HOUSE': 100,
        'RENT': 10,
        'RENT_ONE_HOUSE': 50,
        'RENT_TWO_HOUSES': 150,
        'RENT_THREE_HOUSES': 450,
        'RENT_FOUR_HOUSES': 625,
        'RENT_HOTEL': 750,
        'MORTGAGE': 70,
    },
    'STATES_AVENUE': {
        'PRICE': 140,
        'PRICE_PER_HOUSE': 100,
        'RENT': 10,
        'RENT_ONE_HOUSE': 50,
        'RENT_TWO_HOUSES': 150,
        'RENT_THREE_HOUSES': 450,
        'RENT_FOUR_HOUSES': 625,
        'RENT_HOTEL': 750,
        'MORTGAGE': 70,
    },
    'VIRGINIA_AVENUE': {
        'PRICE': 160,
        'PRICE_PER_HOUSE': 100,
        'RENT': 12,
        'RENT_ONE_HOUSE': 60,
        'RENT_TWO_HOUSES': 180,
        'RENT_THREE_HOUSES': 500,
        'RENT_FOUR_HOUSES': 700,
        'RENT_HOTEL': 900,
        'MORTGAGE': 80,
    },
    'STJAMES_PLACE': {
        'PRICE': 180,
        'PRICE_PER_HOUSE': 100,
        'RENT': 14,
        'RENT_ONE_HOUSE': 70,
        'RENT_TWO_HOUSES': 200,
        'RENT_THREE_HOUSES': 550,
        'RENT_FOUR_HOUSES': 750,
        'RENT_HOTEL': 950,
        'MORTGAGE': 90,
    },
    'TENNESSEE_AVENUE': {
        'PRICE': 180,
        'PRICE_PER_HOUSE': 100,
        'RENT': 14,
        'RENT_ONE_HOUSE': 70,
        'RENT_TWO_HOUSES': 200,
        'RENT_THREE_HOUSES': 550,
        'RENT_FOUR_HOUSES': 750,
        'RENT_HOTEL': 950,
        'MORTGAGE': 90,
    },
    'NEWYORK_AVENUE': {
        'PRICE': 200,
        'PRICE_PER_HOUSE': 100,
        'RENT': 16,
        'RENT_ONE_HOUSE': 80,
        'RENT_TWO_HOUSES': 220,
        'RENT_THREE_HOUSES': 600,
        'RENT_FOUR_HOUSES': 800,
        'RENT_HOTEL': 1000,
        'MORTGAGE': 100,
    },
    'KENTUCKY_AVENUE': {
        'PRICE': 220,
        'PRICE_PER_HOUSE': 150,
        'RENT': 18,
        'RENT_ONE_HOUSE': 90,
        'RENT_TWO_HOUSES': 250,
        'RENT_THREE_HOUSES': 700,
        'RENT_FOUR_HOUSES': 875,
        'RENT_HOTEL': 1050,
        'MORTGAGE': 110,
    },
    'IDIANA_AVENUE': {
        'PRICE': 220,
        'PRICE_PER_HOUSE': 150,
        'RENT': 18,
        'RENT_ONE_HOUSE': 90,
        'RENT_TWO_HOUSES': 250,
        'RENT_THREE_HOUSES': 700,
        'RENT_FOUR_HOUSES': 875,
        'RENT_HOTEL': 1050,
        'MORTGAGE': 110,
    },
    'ILLINOIS_AVENUE': {
        'PRICE': 240,
        'PRICE_PER_HOUSE': 150,
        'RENT': 20,
        'RENT_ONE_HOUSE': 100,
        'RENT_TWO_HOUSES': 300,
        'RENT_THREE_HOUSES': 750,
        'RENT_FOUR_HOUSES': 925,
        'RENT_HOTEL': 1100,
        'MORTGAGE': 120,
    },
    'ATLANTIC_AVENUE': {
        'PRICE': 260,
        'PRICE_PER_HOUSE': 150,
        'RENT': 22,
        'RENT_ONE_HOUSE': 110,
        'RENT_TWO_HOUSES': 330,
        'RENT_THREE_HOUSES': 800,
        'RENT_FOUR_HOUSES': 975,
        'RENT_HOTEL': 1150,
        'MORTGAGE': 130,
    },
    'VENTNOR_AVENUE': {
        'PRICE': 260,
        'PRICE_PER_HOUSE': 150,
        'RENT': 22,
        'RENT_ONE_HOUSE': 110,
        'RENT_TWO_HOUSES': 330,
        'RENT_THREE_HOUSES': 800,
        'RENT_FOUR_HOUSES': 975,
        'RENT_HOTEL': 1150,
        'MORTGAGE': 130,
    },
    'MARVIN_GARDENS': {
        'PRICE': 280,
        'PRICE_PER_HOUSE': 150,
        'RENT': 24,
        'RENT_ONE_HOUSE': 120,
        'RENT_TWO_HOUSES': 360,
        'RENT_THREE_HOUSES': 850,
        'RENT_FOUR_HOUSES': 1025,
        'RENT_HOTEL': 1200,
        'MORTGAGE': 140,
    },
    'PACIFIC_AVENUE': {
        'PRICE': 300,
        'PRICE_PER_HOUSE': 200,
        'RENT': 26,
        'RENT_ONE_HOUSE': 130,
        'RENT_TWO_HOUSES': 390,
        'RENT_THREE_HOUSES': 900,
        'RENT_FOUR_HOUSES': 1100,
        'RENT_HOTEL': 1275,
        'MORTGAGE': 150,
    },
    'NORTH_CAROLINA_AVENUE': {
        'PRICE': 300,
        'PRICE_PER_HOUSE': 200,
        'RENT': 26,
        'RENT_ONE_HOUSE': 130,
        'RENT_TWO_HOUSES': 390,
        'RENT_THREE_HOUSES': 900,
        'RENT_FOUR_HOUSES': 1100,
        'RENT_HOTEL': 1275,
        'MORTGAGE': 150,
    },
    'PENNSYLVANIA_AVENUE': {
        'PRICE': 320,
        'PRICE_PER_HOUSE': 200,
        'RENT': 28,
        'RENT_ONE_HOUSE': 150,
        'RENT_TWO_HOUSES': 450,
        'RENT_THREE_HOUSES': 1000,
        'RENT_FOUR_HOUSES': 1200,
        'RENT_HOTEL': 1400,
        'MORTGAGE': 160,
    },
    'PARK_PLACE': {
        'PRICE': 350,
        'PRICE_PER_HOUSE': 200,
        'RENT': 35,
        'RENT_ONE_HOUSE': 175,
        'RENT_TWO_HOUSES': 500,
        'RENT_THREE_HOUSES': 1100,
        'RENT_FOUR_HOUSES': 1300,
        'RENT_HOTEL': 1500,
        'MORTGAGE': 175,
    },
    'BOARD_WALK': {
        'PRICE': 400,
        'PRICE_PER_HOUSE': 200,
        'RENT': 50,
        'RENT_ONE_HOUSE': 200,
        'RENT_TWO_HOUSES': 600,
        'RENT_THREE_HOUSES': 1400,
        'RENT_FOUR_HOUSES': 1700,
        'RENT_HOTEL': 2000,
        'MORTGAGE': 200,
    },
}
