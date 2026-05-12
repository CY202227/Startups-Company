const COMPANIES = [
  { id: 0, name: "EMT", total: 8 },
  { id: 1, name: "Flaming Soft", total: 8 },
  { id: 2, name: "Hippo Powertech", total: 7 },
  { id: 3, name: "Bowwow Games", total: 7 },
  { id: 4, name: "Giraffe Beer", total: 5 },
  { id: 5, name: "Elephant Mars Travel", total: 10 },
];

const STAGE_TAKE = "TAKE";
const STAGE_PLAY = "PLAY";
const STAGE_FINISHED = "FINISHED";

function mulberry32(seed) {
  return function () {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function clone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

function companyOwner(state, companyId) {
  return state.companies[companyId].anti_monopoly_owner;
}

function companyName(companyId) {
  return COMPANIES[companyId].name;
}

function buildDeck(seed) {
  const rng = mulberry32(seed);
  const deck = [];
  for (const company of COMPANIES) {
    for (let i = 0; i < company.total; i += 1) {
      deck.push(company.id);
    }
  }
  for (let i = deck.length - 1; i > 0; i -= 1) {
    const j = Math.floor(rng() * (i + 1));
    const tmp = deck[i];
    deck[i] = deck[j];
    deck[j] = tmp;
  }
  return deck.slice(5);
}

function setupGame(playerCount, seed) {
  const players = [];
  const deck = buildDeck(seed);
  for (let i = 0; i < playerCount; i += 1) {
    players.push({
      player_id: i,
      cash: 10,
      hand: deck.slice(i * 3, i * 3 + 3),
      portfolio: new Array(6).fill(0),
      flipped_coins: 0,
      penalty: 0,
      history: [],
    });
  }
  return {
    seed,
    rules: { player_count: playerCount },
    players,
    deck: deck.slice(playerCount * 3),
    market: [],
    companies: COMPANIES.map((company) => ({
      company_id: company.id,
      anti_monopoly_owner: null,
    })),
    stage: STAGE_TAKE,
    current_player: 0,
    turn_number: 1,
    last_took_company: null,
    last_took_from_market: false,
    game_end_triggered: false,
    events: ["game_started"],
  };
}

function recomputeAntiMonopoly(state) {
  const nextCompanies = clone(state.companies);
  for (const company of nextCompanies) {
    const share = state.players.map((player) => player.portfolio[company.company_id]);
    const maxShare = Math.max(...share);
    if (maxShare <= 0) {
      company.anti_monopoly_owner = null;
      continue;
    }
    const owners = share.reduce((out, count, idx) => {
      if (count === maxShare) out.push(idx);
      return out;
    }, []);
    company.anti_monopoly_owner = owners.length === 1 ? owners[0] : null;
  }
  return nextCompanies;
}

function applyCoinToMarket(state, market) {
  return market.map((card) => {
    if (companyOwner(state, card.company_id) === state.current_player) return card;
    return { ...card, coins: card.coins + 1 };
  });
}

function marketDrawCost(state, playerId) {
  return state.market.reduce((cost, card) => {
    const owner = companyOwner(state, card.company_id);
    return owner === playerId ? cost : cost + 1;
  }, 0);
}

function canTakeFromMarket(state) {
  return state.market.filter((card) => companyOwner(state, card.company_id) !== state.current_player);
}

function finishTurn(state) {
  const next = clone(state);
  if (state.game_end_triggered) {
    const pid = state.current_player;
    const player = next.players[pid];
    for (const cardId of player.hand) player.portfolio[cardId] += 1;
    player.hand = [];
    player.history.push("auto_discard_hand");
    next.companies = recomputeAntiMonopoly(next);
    next.stage = STAGE_FINISHED;
    next.events.push("game_end");
    return next;
  }
  next.current_player = (state.current_player + 1) % state.players.length;
  next.turn_number = state.turn_number + 1;
  next.stage = STAGE_TAKE;
  next.last_took_company = null;
  next.last_took_from_market = false;
  next.events.push(`turn_end -> P${next.current_player}`);
  return next;
}

function applyAction(state, action) {
  const next = clone(state);
  const player = next.players[state.current_player];
  const pid = state.current_player;

  if (state.stage === STAGE_FINISHED) {
    return { state, accepted: false, message: "游戏已结束" };
  }

  if (action.type === "TAKE_FROM_DECK") {
    if (state.stage !== STAGE_TAKE) {
      return { state, accepted: false, message: "当前不是 TAKE 阶段" };
    }
    if (!state.deck.length) {
      return { state, accepted: false, message: "抽牌堆已空" };
    }
    const cost = marketDrawCost(state, pid);
    if (player.cash < cost) {
      return { state, accepted: false, message: `现金不足，需 ${cost} 金币` };
    }
    const card = state.deck[0];
    next.deck = state.deck.slice(1);
    next.market = applyCoinToMarket(state, state.market);
    player.cash -= cost;
    player.hand = [...player.hand, card];
    player.history.push(`take_deck:${card}`);
    next.last_took_company = card;
    next.last_took_from_market = false;
    next.game_end_triggered = next.deck.length === 0;
    next.stage = STAGE_PLAY;
    next.events.push(`P${pid} TAKE_FROM_DECK`);
    return { state: next, accepted: true };
  }

  if (action.type === "TAKE_FROM_MARKET") {
    if (state.stage !== STAGE_TAKE) {
      return { state, accepted: false, message: "当前不是 TAKE 阶段" };
    }
    const idx = action.index;
    if (idx < 0 || idx >= state.market.length) {
      return { state, accepted: false, message: "市场索引越界" };
    }
    const card = state.market[idx];
    if (companyOwner(state, card.company_id) === pid) {
      return { state, accepted: false, message: "反垄断限制，不可拿该牌" };
    }
    next.market = state.market.filter((_, i) => i !== idx);
    player.hand = [...player.hand, card.company_id];
    player.cash += card.coins;
    player.history.push(`take_market:${card.company_id}:${card.coins}`);
    next.last_took_company = card.company_id;
    next.last_took_from_market = true;
    next.stage = STAGE_PLAY;
    next.events.push(`P${pid} TAKE_FROM_MARKET idx=${idx}`);
    return { state: next, accepted: true };
  }

  if (action.type === "PLAY_TO_PORTFOLIO") {
    if (state.stage !== STAGE_PLAY) {
      return { state, accepted: false, message: "当前不是 PLAY 阶段" };
    }
    const idx = action.index;
    if (idx < 0 || idx >= state.players[pid].hand.length) {
      return { state, accepted: false, message: "手牌索引越界" };
    }
    const cardId = player.hand[idx];
    player.hand = [...player.hand.slice(0, idx), ...player.hand.slice(idx + 1)];
    player.portfolio[cardId] += 1;
    player.history.push(`play_portfolio:${cardId}`);
    next.last_took_company = null;
    next.last_took_from_market = false;
    next.companies = recomputeAntiMonopoly(next);
    next.events.push(`P${pid} PLAY_TO_PORTFOLIO ${cardId}`);
    return { state: finishTurn(next), accepted: true };
  }

  if (action.type === "PLAY_TO_MARKET") {
    if (state.stage !== STAGE_PLAY) {
      return { state, accepted: false, message: "当前不是 PLAY 阶段" };
    }
    const idx = action.index;
    if (idx < 0 || idx >= state.players[pid].hand.length) {
      return { state, accepted: false, message: "手牌索引越界" };
    }
    const cardId = player.hand[idx];
    if (state.last_took_from_market && state.last_took_company === cardId) {
      return {
        state,
        accepted: false,
        message: "你刚从市场拿到该公司牌，不能直接打回市场。",
      };
    }
    player.hand = [...player.hand.slice(0, idx), ...player.hand.slice(idx + 1)];
    next.market = [...next.market, { company_id: cardId, coins: 0 }];
    player.history.push(`play_market:${cardId}`);
    next.last_took_company = null;
    next.last_took_from_market = false;
    next.events.push(`P${pid} PLAY_TO_MARKET ${cardId}`);
    return { state: finishTurn(next), accepted: true };
  }

  return { state, accepted: false, message: "未知动作" };
}

function computeScores(state) {
  const players = clone(state.players);
  const payouts = [];
  for (const company of COMPANIES) {
    const counts = players.map((player) => player.portfolio[company.id]);
    const maxCount = Math.max(...counts);
    if (maxCount <= 0) continue;
    const winners = counts.reduce((acc, count, idx) => {
      if (count === maxCount) acc.push(idx);
      return acc;
    }, []);
    if (winners.length !== 1) continue;
    const holder = winners[0];
    counts.forEach((stock, idx) => {
      if (idx === holder || stock === 0 || stock >= maxCount) return;
      const payer = players[idx];
      const needed = stock;
      const paid = Math.min(payer.cash, needed);
      const unpaid = needed - paid;
      payer.cash -= paid;
      players[holder].flipped_coins += paid;
      payer.penalty -= unpaid;
      payouts.push({
        payer_id: idx,
        holder_id: holder,
        company_id: company.id,
        paid,
        required: needed,
      });
    });
  }
  const totals = players.map((player) => player.cash + player.flipped_coins * 3 + player.penalty);
  const winner = totals.reduce(
    (best, value, idx) => (value > best.score ? { score: value, playerId: idx } : best),
    { score: totals[0], playerId: 0 },
  );
  return { players, totals, winner: winner.playerId, payouts };
}

function autoTakeAction(state) {
  if (state.stage !== STAGE_TAKE) return null;
  const legalMarket = canTakeFromMarket(state);
  if (!legalMarket.length && state.deck.length > 0) return { type: "TAKE_FROM_DECK" };
  return null;
}

function aiAction(state) {
  const policy = Math.random() < 0.5 ? "greedy" : "anti_pressure";
  if (state.stage === STAGE_TAKE) {
    const legalMarket = canTakeFromMarket(state);
    if (!legalMarket.length && !state.deck.length) return null;
    const cost = marketDrawCost(state, state.current_player);
    const player = state.players[state.current_player];
    if (policy === "anti_pressure" && legalMarket.length > 0) {
      const best = legalMarket.sort((a, b) => b.coins - a.coins)[0];
      if (best.coins > 0) return { type: "TAKE_FROM_MARKET", index: state.market.indexOf(best) };
      if (player.cash >= cost) return { type: "TAKE_FROM_DECK" };
      return { type: "TAKE_FROM_MARKET", index: state.market.indexOf(legalMarket[0]) };
    }
    if (legalMarket.length > 0 && player.cash < cost) {
      return { type: "TAKE_FROM_MARKET", index: state.market.indexOf(legalMarket[0]) };
    }
    return { type: "TAKE_FROM_DECK" };
  }
  const hand = state.players[state.current_player].hand;
  const marketOptions = [];
  const portfolioOptions = [];
  hand.forEach((cardId, idx) => {
    const holder = companyOwner(state, cardId);
    const base = holder === state.current_player ? 2 : 1;
    const antiPressure = holder === null ? 1 : 0;
    portfolioOptions.push({ idx, cardId, score: base + antiPressure });
    if (!(state.last_took_from_market && state.last_took_company === cardId)) {
      marketOptions.push({ idx, cardId, score: base });
    }
  });
  marketOptions.sort((a, b) => b.score - a.score);
  portfolioOptions.sort((a, b) => b.score - a.score);

  if (policy === "anti_pressure" && marketOptions.length > 0) {
    return { type: "PLAY_TO_MARKET", index: marketOptions[0].idx };
  }
  if (portfolioOptions.length > 0) {
    return { type: "PLAY_TO_PORTFOLIO", index: portfolioOptions[0].idx };
  }
  if (marketOptions.length > 0) {
    return { type: "PLAY_TO_MARKET", index: marketOptions[0].idx };
  }
  return null;
}

function deckRemainingByCompany(state) {
  const table = {};
  for (const company of COMPANIES) table[company.id] = company.total;
  for (const card of state.deck) table[card] -= 1;
  return table;
}

function renderHandTotals(state, playerId) {
  const deckTable = deckRemainingByCompany(state);
  const player = state.players[playerId];
  const counts = {};
  for (const card of player.hand) counts[card] = (counts[card] || 0) + 1;
  return { counts, deckTable };
}

function render(state, singlePlayer) {
  const gameSection = document.getElementById("game");
  const summary = document.getElementById("state-summary");
  const marketNode = document.getElementById("market");
  const monopolyNode = document.getElementById("monopoly");
  const currentNode = document.getElementById("current-player");
  const actionNode = document.getElementById("actions");
  const results = document.getElementById("results");
  const scoreboard = document.getElementById("scoreboard");

  gameSection.hidden = false;

  summary.innerHTML = `
    <div class="row">回合：${state.turn_number}</div>
    <div class="row">阶段：${state.stage}</div>
    <div class="row">当前玩家：P${state.current_player}${state.current_player === 0 ? "（你）" : ""}</div>
    <div class="row">抽牌堆剩余：${state.deck.length}</div>
    <div class="row">最新事件：${state.events[state.events.length - 1]}</div>
  `;

  marketNode.innerHTML = "";
  if (!state.market.length) {
    marketNode.innerHTML = "<div class='row muted'>（当前无市场牌）</div>";
  } else {
    state.market.forEach((card, idx) => {
      const owner = companyOwner(state, card.company_id);
      const blocked = owner === state.current_player;
      const node = document.createElement("div");
      node.className = `market-card ${blocked ? "blocked" : ""}`;
      node.textContent = `#${idx} ${companyName(card.company_id)}，金币:${card.coins}，`;
      const flag = document.createElement("span");
      flag.textContent = blocked ? "不可取（反垄断）" : "可取";
      flag.className = blocked ? "muted" : "winner";
      node.appendChild(flag);
      marketNode.appendChild(node);
    });
  }

  monopolyNode.innerHTML = "";
  state.companies.forEach((company) => {
    const row = document.createElement("div");
    row.className = "row";
    row.textContent = `${companyName(company.company_id)}：${company.anti_monopoly_owner === null
      ? "无人"
      : `P${company.anti_monopoly_owner}`}`;
    monopolyNode.appendChild(row);
  });

  currentNode.innerHTML = "";
  const player = state.players[state.current_player];
  const handInfo = renderHandTotals(state, state.current_player);
  const handTitle = document.createElement("div");
  handTitle.className = "row";
  handTitle.innerHTML = "<strong>手牌</strong>";
  currentNode.appendChild(handTitle);

  player.hand.forEach((cardId, idx) => {
    const total = (handInfo.deckTable[cardId] || 0) + (handInfo.counts[cardId] || 0);
    const line = document.createElement("div");
    line.className = "row";
    line.textContent = `${idx}）${companyName(cardId)}（总量：${total}）`;
    currentNode.appendChild(line);
  });

  const portfolioText = player.portfolio
    .map((count, idx) => `${companyName(idx)}：${count}`)
    .join(" / ");
  currentNode.innerHTML += `<div class="row">现金：${player.cash}</div>`;
  currentNode.innerHTML += `<div class="row">持股：${portfolioText}</div>`;

  actionNode.innerHTML = "";
  if (state.stage === STAGE_TAKE) {
    const cost = marketDrawCost(state, state.current_player);
    const auto = autoTakeAction(state);
    const deckBtn = document.createElement("button");
    deckBtn.textContent = `从牌堆抽取（花费 ${cost} 金币）`;
    deckBtn.disabled = auto ? false : player.cash < cost || state.deck.length === 0;
    deckBtn.onclick = () => onAction({ type: "TAKE_FROM_DECK" });
    actionNode.appendChild(deckBtn);

    state.market.forEach((card, idx) => {
      const banned = companyOwner(state, card.company_id) === state.current_player;
      const btn = document.createElement("button");
      btn.textContent = `拿市场 #${idx}（${companyName(card.company_id)}，+${card.coins}）`;
      btn.disabled = banned;
      btn.onclick = () => onAction({ type: "TAKE_FROM_MARKET", index: idx });
      actionNode.appendChild(btn);
    });
  } else if (state.stage === STAGE_PLAY) {
    if (!player.hand.length) {
      actionNode.innerHTML = "<div class='muted'>无手牌，回合自动结束。</div>";
    }
    player.hand.forEach((cardId, idx) => {
      const toPortfolio = document.createElement("button");
      toPortfolio.textContent = `${idx} 放入 ${companyName(cardId)} 资本账户`;
      toPortfolio.onclick = () => onAction({ type: "PLAY_TO_PORTFOLIO", index: idx });
      actionNode.appendChild(toPortfolio);

      const toMarket = document.createElement("button");
      const disabled = state.last_took_from_market && state.last_took_company === cardId;
      toMarket.textContent = `${idx} 放入市场 ${companyName(cardId)}`;
      toMarket.disabled = disabled;
      toMarket.onclick = () => onAction({ type: "PLAY_TO_MARKET", index: idx });
      actionNode.appendChild(toMarket);
    });
  }

  results.hidden = state.stage !== STAGE_FINISHED;
  if (state.stage === STAGE_FINISHED) {
    const result = computeScores(state);
    scoreboard.innerHTML = "";
    result.totals.forEach((total, idx) => {
      const row = document.createElement("div");
      const isWinner = idx === result.winner;
      row.className = `row ${isWinner ? "winner" : ""}`;
      row.textContent = `P${idx}：${total}（现金 ${result.players[idx].cash}，翻牌 ${result.players[idx].flipped_coins}，罚金 ${result.players[idx].penalty}）`;
      scoreboard.appendChild(row);
    });
    const winnerLine = document.createElement("div");
    winnerLine.className = "row winner";
    winnerLine.textContent = `胜者：P${result.winner}`;
    scoreboard.appendChild(winnerLine);
  }

  const isHuman = !singlePlayer || state.current_player === 0;
  if (!isHuman) {
    actionNode.innerHTML = "<div class='row muted'>AI 正在决策...</div>";
    setTimeout(() => {
      const choose = autoTakeAction(state) || aiAction(state);
      if (choose) {
        onAction(choose, true);
        return;
      }
      actionNode.innerHTML = "<div class='row muted'>AI 无可执行动作，等待下一步。</div>";
    }, 600);
  }
}

function applyIfAllowed(action) {
  const result = applyAction(window.gameState, action);
  if (!result.accepted) {
    window.alert(result.message || "动作不可执行");
    return;
  }
  window.gameState = result.state;
  render(window.gameState, window.singlePlayer);
}

function onAction(action, skipAlert) {
  const result = applyAction(window.gameState, action);
  if (!result.accepted) {
    if (!skipAlert) {
      window.alert(result.message || "动作不可执行");
    } else {
      window.console.warn(result.message || "动作不可执行");
    }
    return;
  }
  window.gameState = result.state;
  render(window.gameState, window.singlePlayer);
}

function startGame() {
  const players = Number(document.getElementById("players").value);
  const seedInput = document.getElementById("seed").value;
  const seed = seedInput ? Number(seedInput) : Date.now();
  const singlePlayer = document.getElementById("single-player").checked;

  if (players < 3 || players > 7) {
    window.alert("支持 3-7 人玩家。");
    return;
  }

  window.singlePlayer = singlePlayer;
  window.gameState = setupGame(players, Math.abs(Math.floor(seed)));
  render(window.gameState, singlePlayer);
}

function setRandomSeed() {
  document.getElementById("seed").value = String(Math.floor(Math.random() * 1000000));
}

document.getElementById("new-game").addEventListener("click", startGame);
document.getElementById("seed-random").addEventListener("click", setRandomSeed);

window.onload = () => {
  setRandomSeed();
};
