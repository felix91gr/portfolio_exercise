# Instructions
# ------------
# Construct a simple Portfolio class that has
# - A collection of Stocks.
#
# Assume each Stock has
# - A “Current Price” method that
#   - Receives the last available price.
#
# Also, the Portfolio class has
# - A collection of “allocated” Stocks that
#   - Represents the distribution of the Stocks
#     the Portfolio is aiming (i.e. 40% META, 60% APPL)
#
# Provide
# A portfolio rebalance method, to
# - Know which Stocks should be sold and
# - Which ones should be bought,
# to have a balanced Portfolio; based on the portfolio’s allocation.
# Add documentation/comments to understand your thinking process and solution

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
#   Let's say each price is a positive floating point value,
#   representing a proportional quantity of money.
#   We'll say then, that these prices are represented by a
#   dictionary / hashmap of the following form:
#
#           Prices: StockID -> float
#
# - An amount we own, for each one of those Stocks.
#   Let's say that similarly to the prices, we'll represent these
#   quantities in terms of positive floating point values.
#   So, just like the prices, the amounts we own will be a dictionary:
#
#           Collection: StockID -> float
#
# - An aim for the Portfolio, which represents what percentage of our assets
#   should be allocated to each Stock.
#   We will represent this as a dictionary, i.e. a mapping from StockID to
#   percentages. Just like for the other two dictionaries, these quantities
#   must be positive. However, there are two more restrictions that must
#   be in place:
#   - Percentages must be between 0% and 100%, i.e. between 0 and 1.
#   - The Allocation Percentages must add to 100%, i.e. to 1.
#
#   In order to reliably check that they add to 100%, we'll represent
#   the Allocation Percentages as Fraction values:
#
#           Allocation: StockID -> Fraction
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
# III) Implementation


## Notes for me, on formatting:
## https://peps.python.org/pep-0008/#function-and-variable-names
## Fn names should be lowercase, words separated by underscores.
## Variable names should follow the same convention

