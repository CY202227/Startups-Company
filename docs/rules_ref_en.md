# Startups Rule Guide (Current UI)

This English guide matches the current web UI labels, buttons, and state
messages. It is intended to solve two issues:
1) the rule wording did not line up with the UI; 2) the previous guide was too
short for new players.

> Recommended path: read the quick turn flow first, then the anti-monopoly
> rule, then scoring.

## What You See In The UI

### UI Terms And Rule Terms

- **Market**: the public area containing visible company cards.
- **Anti-monopoly Holder**: the player shown in the "Anti-monopoly Holder"
  section for each company.
- **Take / Play** buttons: the two phases of every turn:
  - `Take`: draw from deck or take from market.
  - `Play`: play to your portfolio or play to market.
- **Flipped** in scoring: the UI field `flipped` means 3-value coins gained
  during scoring. Each flipped coin is worth 3 points.

### Goal

Highest final score wins.
The main tension is not who collects the most cards, but who controls companies
well enough to earn payments during scoring.

## 1) Setup

- Players: 3-7.
- Starting cash: 10 one-value coins per player.
- Initial hand: 3 cards per player.
- The deck has 45 company cards across 6 companies:
  - EMT (8)
  - Flaming Soft (8)
  - Hippo Powertech (7)
  - Bowwow Games (7)
  - Giraffe Beer (5)
  - Elephant Mars Travel (10)
- After shuffling, remove 5 cards. The remaining cards form the draw deck.

## 2) Turn Flow

Each player must perform two steps in order:

1. Take
2. Play

### 1) Take Phase

- `Draw from deck`:
  - Pay 1 coin for each card in the market.
  - Exception: if a market card belongs to a company whose anti-monopoly token
    you currently hold, that market card does not cost you 1 coin.
  - Example: if the market has 5 cards and 2 of those companies are protected
    by your anti-monopoly tokens, drawing from deck costs 3 coins.
- `Take from market`:
  - You cannot take a market card from a company whose anti-monopoly token you
    currently hold.
  - Market cards may have bonus coins on them. If you take that card, you
    immediately gain those coins.

### 2) Play Phase

- Play one card from your hand to your portfolio, or play it to the market.
- If your take step took a company card from the market, you cannot immediately
  play the same company back to the market in this play step.
- After playing, your turn ends and the next player acts.

### Beginner Full-Turn Example

Assume it is P0's turn and the market has 3 cards:

- EMT, +0 coins, available.
- Giraffe Beer, +2 coins, available.
- Flaming Soft, +1 coin, but P0 currently holds Flaming Soft's anti-monopoly
  token.

P0 has two choices in the take phase:

- Draw from deck: P0 must pay for market cards. Flaming Soft does not cost
  anything because P0 holds that company's anti-monopoly token, so the total
  cost is 2 coins.
- Take from market: P0 may take EMT or Giraffe Beer. If P0 takes Giraffe Beer,
  P0 immediately gains the 2 coins on that card. P0 may not take Flaming Soft.

Suppose P0 takes Giraffe Beer from the market. The turn moves to the play phase:

- P0 may play a card to portfolio to increase their holdings.
- P0 may play a card to market for future players to take.
- If P0 also has another Giraffe Beer in hand, P0 cannot immediately play that
  Giraffe Beer back to the market this turn.

After P0 plays, the system recomputes anti-monopoly holders and the next player
takes a turn.

## 3) Anti-Monopoly Holder Rule

Each company has 1 anti-monopoly holder. This holder affects both market-taking
restrictions and draw-from-deck discounts.

- Check each player's portfolio count for that company.
- The unique highest portfolio count becomes that company's anti-monopoly
  holder.
- If players are tied for highest, there is usually no holder. However, if the
  previous holder is still tied for highest, the current UI keeps that holder
  until a new unique leader appears.
- When a new unique leader appears, the holder immediately transfers.
- In the UI, "Blocked (anti-monopoly)" means the current player holds that
  company's anti-monopoly token and cannot take that market card.

## 4) End And Scoring

### Trigger

- When a player draws the final card from the deck during the `Take` phase and
  completes that turn's `Play` phase, the game immediately goes to scoring.

### Scoring Steps

- The triggering player's remaining hand is revealed and merged into portfolio
  counts before company scoring.
- For each company:
  - If there is a unique largest holder, that player receives payment from each
    player with fewer shares.
  - Each payer pays an amount equal to their own share count in that company.
  - If there is no unique largest holder, that company pays nothing.
- If a player cannot fully pay:
  - They pay as much as possible.
  - Any unpaid amount is recorded as `penalty` so replay and scoring remain
    deterministic.
- Final score:
  - `score = cash + flipped * 3 + penalty`
- Ties: no winner is shown; the UI displays a tie.

## 5) UI Cheat Sheet

- **Deck left**: number of cards left in the draw deck.
- **Market**: visible cards that may be taken.
- **Available / Blocked (anti-monopoly)**: whether the current player may take
  that market card.
- **Anti-monopoly Holder**: who currently leads each company.
- **Table Overview**: each player's cash and portfolio counts.
- **Final Scores**: each player's score and the result.

## 6) FAQ

### Why is "Draw from deck" disabled even though I still have cash?

Because drawing from deck costs 1 coin per chargeable market card. The total
cost may exceed your current cash.

### Why does a market card show "+x"?

That is the bonus coin count currently sitting on the card. If you take the
card, those coins are added to your cash.

### Why does the game end while cards are still visible?

The game ends when the draw deck's last card is taken and that player finishes
the play step. Market cards do not keep the game running.

## 7) Implementation Mapping

- Phases: `TAKE` / `PLAY` / `FINISHED`.
- Actions: `TAKE_FROM_DECK`, `TAKE_FROM_MARKET`, `PLAY_TO_PORTFOLIO`,
  `PLAY_TO_MARKET`.
- Scoring uses `penalty` to handle unpaid debt and keep the state computable.
- This is an executable rule guide aligned with the current UI behavior.
