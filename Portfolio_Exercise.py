###############################################################################
# Instructions
# ------------
# Construct a simple Portfolio class that has
# - A collection of Stocks.
#
# Assume each Stock has
# - A “Current Price” method that
#   -> Receives the last available price.
#
# Also, the Portfolio class has
# - A collection of “allocated” Stocks that
#   -> Represents the distribution of the Stocks
#     the Portfolio is aiming (i.e. 40% META, 60% APPL)
#
# Provide
# - A portfolio rebalance method, to
#   -> Know which Stocks should be sold and
#   -> Which ones should be bought,
#  to have a balanced Portfolio; based on the portfolio’s allocation.
#
# Add documentation/comments to understand your thinking process and solution
###############################################################################

###############################################################################
# Overarching Design
# ------------------
#
# I) Data Representation
# ----------------------
#
# Let's say our portfolio is represented in the following way:
#
# - A list of N Stocks that we care about.
#   Let's say, for simplicity, that each Stock is represented by
#   a unique ID, and that we have the IDs of the stocks we care
#   about in an array of length N:
#
#           Stocks: [id0, id1, ... , idN-1]
#
# - A price for each unit of each one of those Stocks.
#   Let's say each price is a positive Decimal value,
#   representing a proportional quantity of money.
#   We'll say then, that these prices are represented by a
#   dictionary / hashmap of the following form:
#
#           Prices: StockID -> Decimal
#
# - An amount we own, for each one of those Stocks.
#   Let's say that similarly to the prices, we'll represent these
#   quantities in terms of positive Decimal values.
#   So, just like the prices, the amounts we own will be a dictionary:
#
#           Collection: StockID -> Decimal
#
# - An aim for the Portfolio, which represents what percentage of our assets
#   should be allocated to each Stock.
#   We will represent this as a dictionary, i.e. a mapping from StockID to
#   percentages. Just like for the other two dictionaries, these quantities
#   must be positive. However, there are two more restrictions that must
#   be in place:
#   - Percentages must be between 0% and 100%, i.e. between 0 and 1.
#   - The Allocation Percentages must add to 100%, i.e. to 1.
#   Otherwise, the form is the same as for the other two maps:
#
#           Allocation: StockID -> Decimal
#
# II) Computation
# ---------------
#
# So, given all of that, what is it that we want to do?
#
# We want to rebalance our Portfolio, so that it matches its Aim / Allocation.
#
# In particular, we want to know exactly how much of every Stock should be
# bought and sold in order to do said rebalancing.
#
# Step by step, we mean to do the following:
#
# 1) Obtain the total value present in our assets:
#
#       TotalValue = Stocks.map(|ID| -> Prices[ID] x Collection[ID]).sum()
#
# 2) Obtain the new allocation (in money) for each Stock:
#
#       for each ID in Stocks:
#           NewAlloc[ID] = TotalValue x Allocation[ID]
#
# 3) Obtain the amounts we will want our collection to have after rebalancing:
#
#       for each ID in Stocks:
#           RebalancedCollection[ID] = NewAlloc[ID] / Prices[ID]
#
# 4) Find out the change that needs to happen to rebalance:
#
#       for each ID in Stocks:
#           Change[ID] = RebalancedCollection[ID] - Collection[ID]
#
#    Here, `Change[ID]` is the amount that we want to buy of `ID`. Negative
#    values mean that we actually want to sell `|Change[ID]|` units of it.
#
# III) Notes
# ----------
#
# It's important to note that we'll be using `Decimal` instead of `float` for
# our computations. This is for two reasons:
#
#   1. Percentages rarely, if ever, add to 1 in floating point. This is due to
#      the many imprecisions and lossy conversions present in the floating
#      point standard. We'll need something else to be able to represent our
#      Allocation.
#
#   2. The domain of finance demands precision, so we may as well use Decimal
#      types from the beginning.
###############################################################################

###############################################################################
# Implementation
# --------------

from decimal import Decimal


class Stock:
    # A reference to the Stock Prices' table
    # In practice, this would probably be a binding to a database through
    # an ORM. Each Stock will have a reference to its price table instead,
    # and we'll query it whenever we need to know its price.
    _price_table: dict[str, Decimal]

    # The Stock's unique ID
    _id: str

    def __init__(self, stock_id: str, price_table: dict[str, Decimal]) -> None:
        if str not in price_table.keys():
            raise KeyError("This Stock ID is not present in its price table")

        self._price_table = price_table
        self._id = stock_id

    @property
    def id(self) -> str:
        return self._id

    @property
    def price(self) -> Decimal:
        return self._price_table[self.id]

    # Note on the following overrides
    # -------------------------------
    #
    # Here we override the hash and equality functions.
    # This is because we want the dictionaries to use the Stock's ID as the
    # hashing key, and not the price_table reference that we've stored
    # within it.
    #
    # In order to get this behavior,
    # we must override the __hash__ function so that it uses the ID as key,
    def __hash__(self):
        return hash(self.id())

    # and we must also override the __eq__ function so that it equates
    # two stocks through their IDs
    def __eq__(self, value):
        return self.id() == value.id()


class Portfolio:
    # Collection of Stocks.
    # Contains: amount of that Stock present in the Portfolio
    stock_collection: dict[Stock, Decimal]

    # Allocation of Stocks.
    # Contains: target percentage of asset value for that Stock
    stock_allocation: dict[Stock, Decimal]

    def __init__(self, stock_allocation: dict[Stock, Decimal]):
        # Each allocation must be a percentage, i.e. between 0 and 1
        if any(perc < 0 for perc in stock_allocation.values()):
            raise ValueError("Allocation percentages must be positive")

        # The sum of the allocations must always be 100%
        if stock_allocation.values().sum() != Decimal("1.0"):
            raise ValueError("Allocation percentages must add to 1")

        self.stock_allocation = stock_allocation

        # Our stocks collection starts empty
        self.stock_collection = dict.fromkeys(
            stock_allocation.keys(), value=Decimal("0.0")
        )

    def add_stock_amount(self, stock: Stock, amount: Decimal):
        if amount < Decimal("0.0"):
            raise ValueError("Amount must be greater than zero")
        self.stock_collection[stock] += amount

    def rem_stock_amount(self, stock: Stock, amount: Decimal):
        if amount > self.stock_collection[stock]:
            raise ValueError("Cannot remove more stock than what we have")
        self.stock_collection[stock] -= amount

    def set_stock_to_zero(self, stock: Stock):
        self.stock_collection[stock] = Decimal("0.0")

    def rebalance(self) -> dict[Stock, Decimal]:
        stocks = self.stock_allocation.keys()

        total_asset_value: Decimal = sum(
            stock.price() * self.stock_collection[stock] for stock in stocks
        )

        rebalance_changes: dict[Stock, Decimal] = dict()

        for stock in stocks:
            new_allocation: Decimal = total_asset_value * self.stock_allocation[stock]
            rebalanced_amount: Decimal = new_allocation / stock.price()
            rebalance_changes[stock] = rebalanced_amount - self.stock_collection[stock]

        return rebalance_changes


#
###############################################################################
