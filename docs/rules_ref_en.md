# Startups Rule Reference (Executable Mapping)

This file is a concise rule summary adapted for implementation and testing.

## 1) Basic settings

- Players: 3-7 players.
- Companies: 6 startup companies.
- Starting capital: 10 one-unit startup coins per player.
- Initial hand: 3 cards per player.
- Setup: after shuffling, remove 5 cards face down from the deck.
- Turn has two mandatory steps:
  1. Take one card (from deck or market).
  2. Play one card (to portfolio or market).
- Turn order: clockwise from P0 by default.

## 2) Market and Anti-Monopoly token

- Market is public. All market cards are visible and can be taken (with restrictions below).
- `Take from deck`: pay 1 coin for each market card, unless you already hold that company’s anti-monopoly token.
- `Take from market`: forbidden for cards of a company whose anti-monopoly token you currently own.
- Anti-monopoly token rule:
  - One token per company.
  - The player with the largest portfolio count for that company holds the token.
  - If there are multiple players tied for largest, no holder is assigned.
  - When a clear unique new leader appears, the token immediately transfers to that player.

## 3) End and scoring (implementation interpretation)

This implementation uses:

- When a player draws the final deck card and then completes the two-step turn, the game goes directly to scoring.
- Before scoring, all cards in the last player’s hand are revealed and merged into portfolio counts.
- For each company:
  - If there is a unique max holder, that holder receives payment from every player with a smaller holding.
  - Payment size from another player equals that player’s company shares.
  - Collected coins are counted at 3x value in scoring.
  - If there is no unique holder (tie), no scoring payment for that company.
- Underpayment handling:
  - If a payer lacks enough cash, pay as much as possible.
  - Unpaid amount is recorded as penalty (negative score) to keep deterministic replay.
  - This underpayment branch is an implementation-friendly extension for stable computation.
- Final score:
  - `score = one-coin cash + (three-coin flipped * 3) + penalty`
- Ties: no winner by default.

## 4) Card distribution (implementation constants)

- This project uses 45 total company cards, matching common published ranges.
- Default deck:
  - EMT: 8
  - Flaming Soft: 8
  - Hippo Powertech: 7
  - Bowwow Games: 7
  - Giraffe Beer: 5
  - Elephant Mars Travel: 10
- If needed, replace in configuration (`CompanyConfig`).

## 5) Turn machine mapping

- `TAKE`: must execute `take_deck` or `take_market`.
- `PLAY`: must execute `play_front` or `play_market`.
- If a card is taken from market, it cannot be immediately played back to market in the same `PLAY` phase.
- All actions return new immutable state + event logs.
