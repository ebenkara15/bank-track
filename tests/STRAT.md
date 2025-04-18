# Testing strategy

## 🗂️ Tests folder layout

The folder layout should follow pretty much the same layout as the applicative code but it should be split between [unit tests](./unit/), [integration](./integration/) tests and [end-to-end](./e2e/) tests

## 🚥 Priority

1. [Adapters](../bank_track/core/adapters.py) - the core logic of interacting with data storage
    - BaseSQLService - the base adapter
    - Specific adapters
2. [API](../bank_track/api/)
    - Routes - the logic between a basic HTTP client and the API
    - Security - the logic of verifying a user and retrieving data accordingly
    -
3. [Workers](./../bank_track/workers/)
    - Integration with GoCardless (the bank data provider)
