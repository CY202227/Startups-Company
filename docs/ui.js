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

const I18N = {
  zh: {
    title: "Startups 可视化对局（Web）",
    subtitle: "本页面为静态版前端界面，支持多人手动/单人局（P0 人类，P1+ AI）。",
    setup_title: "开局设置",
    players_label: "人数：",
    seed_label: "种子（可留空）：",
    seed_placeholder: "例如 101",
    single_player_label: "单人局（P0 人类，P1+ AI）",
    new_game_btn: "开始新游戏",
    random_seed_btn: "随机种子",
    state_title: "当前局面",
    market_title: "市场",
    monopoly_title: "公司反垄断持有人",
    current_title: "当前玩家",
    actions_title: "可选动作",
    result_title: "结算结果",
    // existing keys ...
    game_ended: "游戏已结束",
    not_take_stage: "当前不是 TAKE 阶段",
    not_play_stage: "当前不是 PLAY 阶段",
    deck_empty: "抽牌堆已空",
    insufficient_cash: "现金不足，需 {cost} 金币",
    index_market_oob: "市场索引越界",
    anti_monopoly_forbid: "反垄断限制，不可拿该牌",
    hand_index_oob: "手牌索引越界",
    market_recent_forbid: "你刚从市场拿到该公司牌，不能直接打回市场。",
    unknown_action: "未知动作",
    ai_thinking: "AI 正在决策...",
    ai_no_action: "AI 无可执行动作，等待下一步。",
    game_action_invalid: "动作不可执行",
    no_market_card: "（当前无市场牌）",
    blocked_market_card: "不可取（反垄断）",
    market_card: "可取",
    holder_none: "无人",
    you_suffix: "（你）",
    hand_title: "手牌",
    hand_line: "{idx}）{name}（总量：{total}）",
    cash: "现金：{value}",
    portfolio: "持股：{value}",
    draw_from_deck_btn: "从牌堆抽取（花费 {cost} 金币）",
    take_market_btn: "拿市场 #{idx}（{name}，+{coins}）",
    to_portfolio_btn: "{idx} 放入 {name} 资本账户",
    to_market_btn: "{idx} 放入市场 {name}",
    no_hand_skip: "无手牌，回合自动结束。",
    result_prefix: "胜者：P{winner}",
    score_line: "P{idx}：{total}（现金 {cash}，翻牌 {flipped}，罚金 {penalty}）",
    turn_label: "回合：{value}",
    stage_label: "阶段：{value}",
    player_label: "当前玩家：P{value}",
    deck_left_label: "抽牌堆剩余：{value}",
    event_label: "最新事件：{value}",
    players_limit: "支持 3-7 人玩家。",
    stage_take: "拿牌",
    stage_play: "出牌",
    stage_finished: "结束",
  },
  en: {
    title: "Startups Visual Match (Web)",
    subtitle:
      "This is a static frontend interface with multi-player manual mode or single-player (P0 is human, P1+ AI).",
    setup_title: "Setup",
    players_label: "Players:",
    seed_label: "Seed (optional):",
    seed_placeholder: "e.g., 101",
    single_player_label: "Single player (P0 is human, P1+ AI)",
    new_game_btn: "New Game",
    random_seed_btn: "Random Seed",
    state_title: "Current State",
    market_title: "Market",
    monopoly_title: "Anti-monopoly Holder",
    current_title: "Current Player",
    actions_title: "Available Actions",
    result_title: "Final Scores",
    // existing keys ...
    game_ended: "Game over",
    not_take_stage: "Current phase is not TAKE",
    not_play_stage: "Current phase is not PLAY",
    deck_empty: "Deck is empty",
    insufficient_cash: "Not enough cash. Need {cost}.",
    index_market_oob: "Market index out of range",
    anti_monopoly_forbid: "Cannot take this card due to anti-monopoly restriction",
    hand_index_oob: "Hand index out of range",
    market_recent_forbid: "You cannot put this card back to market immediately.",
    unknown_action: "Unknown action",
    ai_thinking: "AI is deciding...",
    ai_no_action: "AI has no valid action and is waiting.",
    game_action_invalid: "Invalid action",
    no_market_card: "(No cards in market)",
    blocked_market_card: "Blocked (anti-monopoly)",
    market_card: "Available",
    holder_none: "No owner",
    you_suffix: "(You)",
    hand_title: "Hand",
    hand_line: "{idx}) {name} (Total: {total})",
    cash: "Cash: {value}",
    portfolio: "Portfolio: {value}",
    draw_from_deck_btn: "Draw from deck (cost {cost})",
    take_market_btn: "Take market #{idx} ({name}, +{coins})",
    to_portfolio_btn: "{idx} -> Place to portfolio {name}",
    to_market_btn: "{idx} -> Put to market {name}",
    no_hand_skip: "No cards in hand, turn auto-skips.",
    result_prefix: "Winner: P{winner}",
    score_line: "P{idx}: {total} (Cash {cash}, Flipped {flipped}, Penalty {penalty})",
    turn_label: "Turn: {value}",
    stage_label: "Phase: {value}",
    player_label: "Current player: P{value}",
    deck_left_label: "Deck left: {value}",
    event_label: "Latest event: {value}",
    players_limit: "Players must be between 3 and 7.",
    stage_take: "Take",
    stage_play: "Play",
    stage_finished: "Finished",
  },
};

function currentLocale() {
  if (window.UI_LOCALE === "en") return "en";
  return "zh";
}

function setLocale(locale) {
  const next = locale === "en" ? "en" : "zh";
  window.UI_LOCALE = next;
  window.localStorage.setItem("startups-locale", next);
  applyLocaleTexts();
  if (window.gameState) {
    render(window.gameState, window.singlePlayer);
  }
}

function syncLocaleButtons() {
  const locale = currentLocale();
  const zhBtn = document.getElementById("lang-zh");
  const enBtn = document.getElementById("lang-en");
  if (!zhBtn || !enBtn) return;
  zhBtn.classList.toggle("active", locale === "zh");
  enBtn.classList.toggle("active", locale === "en");
}

function applyLocaleTextById(elementId, key, params) {
  const node = document.getElementById(elementId);
  if (!node) return;
  node.textContent = t(key, params);
}

function applyLocaleAttributeById(elementId, attribute, key, params) {
  const node = document.getElementById(elementId);
  if (!node) return;
  node.setAttribute(attribute, t(key, params));
}

function applyLocaleTexts() {
  const locale = currentLocale();
  document.documentElement.lang = locale === "en" ? "en" : "zh-CN";
  document.title = t("title");

  applyLocaleTextById("app-title", "title");
  applyLocaleTextById("app-subtitle", "subtitle");
  applyLocaleTextById("setup-title", "setup_title");
  applyLocaleTextById("players-label", "players_label");
  applyLocaleTextById("seed-label", "seed_label");
  applyLocaleAttributeById("seed", "placeholder", "seed_placeholder");
  applyLocaleTextById("single-player-label", "single_player_label");
  applyLocaleTextById("new-game", "new_game_btn");
  applyLocaleTextById("seed-random", "random_seed_btn");
  applyLocaleTextById("state-title", "state_title");
  applyLocaleTextById("market-title", "market_title");
  applyLocaleTextById("monopoly-title", "monopoly_title");
  applyLocaleTextById("current-title", "current_title");
  applyLocaleTextById("actions-title", "actions_title");
  applyLocaleTextById("result-title", "result_title");
  syncLocaleButtons();
}

function t(key, params) {
  const locale = currentLocale();
  const item = I18N[locale][key] || I18N.zh[key];
  if (typeof item === "string" && params) {
    return item.replace(/{(\w+)}/g, (_, name) => String(params[name] ?? ""));
  }
  return item || key;
}

function stageText(stage) {
  if (stage === STAGE_TAKE) return t("stage_take");
  if (stage === STAGE_PLAY) return t("stage_play");
  if (stage === STAGE_FINISHED) return t("stage_finished");
  return stage;
}

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
    return { state, accepted: false, message: t("game_ended") };
  }

  if (action.type === "TAKE_FROM_DECK") {
    if (state.stage !== STAGE_TAKE) {
      return { state, accepted: false, message: t("not_take_stage") };
    }
    if (!state.deck.length) {
      return { state, accepted: false, message: t("deck_empty") };
    }
    const cost = marketDrawCost(state, pid);
    if (player.cash < cost) {
      return { state, accepted: false, message: t("insufficient_cash", { cost }) };
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
      return { state, accepted: false, message: t("not_take_stage") };
    }
    const idx = action.index;
    if (idx < 0 || idx >= state.market.length) {
      return { state, accepted: false, message: t("index_market_oob") };
    }
    const card = state.market[idx];
    if (companyOwner(state, card.company_id) === pid) {
      return { state, accepted: false, message: t("anti_monopoly_forbid") };
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
      return { state, accepted: false, message: t("not_play_stage") };
    }
    const idx = action.index;
    if (idx < 0 || idx >= state.players[pid].hand.length) {
      return { state, accepted: false, message: t("hand_index_oob") };
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
      return { state, accepted: false, message: t("not_play_stage") };
    }
    const idx = action.index;
    if (idx < 0 || idx >= state.players[pid].hand.length) {
      return { state, accepted: false, message: t("hand_index_oob") };
    }
    const cardId = player.hand[idx];
    if (state.last_took_from_market && state.last_took_company === cardId) {
      return {
        state,
        accepted: false,
        message: t("market_recent_forbid"),
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

  return { state, accepted: false, message: t("unknown_action") };
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
  for (const company of COMPANIES) table[company.id] = 0;
  for (const card of state.deck) {
    table[card] = (table[card] || 0) + 1;
  }
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
    <div class="row">${t("turn_label", { value: state.turn_number })}</div>
    <div class="row">${t("stage_label", { value: stageText(state.stage) })}</div>
    <div class="row">${t("player_label", {
      value: `${state.current_player}${state.current_player === 0 ? ` ${t("you_suffix")}` : ""}`,
    })}</div>
    <div class="row">${t("deck_left_label", { value: state.deck.length })}</div>
    <div class="row">${t("event_label", { value: state.events[state.events.length - 1] })}</div>
  `;

  marketNode.innerHTML = "";
  if (!state.market.length) {
    marketNode.innerHTML = `<div class='row muted'>${t("no_market_card")}</div>`;
  } else {
    state.market.forEach((card, idx) => {
      const owner = companyOwner(state, card.company_id);
      const blocked = owner === state.current_player;
      const node = document.createElement("div");
      node.className = `market-card ${blocked ? "blocked" : ""}`;
      node.textContent = `#${idx} ${companyName(card.company_id)}${currentLocale() === "en" ? ", " : "，"}${
        currentLocale() === "en" ? `coins ${card.coins}` : `金币:${card.coins}`
      }${currentLocale() === "en" ? ", " : "，"}`;
      const flag = document.createElement("span");
      flag.textContent = blocked ? t("blocked_market_card") : t("market_card");
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
      ? t("holder_none")
      : `P${company.anti_monopoly_owner}`}`;
    monopolyNode.appendChild(row);
  });

  currentNode.innerHTML = "";
  const player = state.players[state.current_player];
  const handInfo = renderHandTotals(state, state.current_player);
  const handTitle = document.createElement("div");
  handTitle.className = "row";
  handTitle.innerHTML = `<strong>${t("hand_title")}</strong>`;
  currentNode.appendChild(handTitle);

  player.hand.forEach((cardId, idx) => {
    const total = (handInfo.deckTable[cardId] || 0) + (handInfo.counts[cardId] || 0);
    const line = document.createElement("div");
    line.className = "row";
    line.textContent = t("hand_line", {
      idx,
      name: companyName(cardId),
      total,
    });
    currentNode.appendChild(line);
  });

  const portfolioText = player.portfolio
    .map((count, idx) => `${companyName(idx)}：${count}`)
    .join(" / ");
  currentNode.innerHTML += `<div class="row">${t("cash", { value: player.cash })}</div>`;
  currentNode.innerHTML += `<div class="row">${t("portfolio", { value: portfolioText })}</div>`;

  actionNode.innerHTML = "";
  if (state.stage === STAGE_TAKE) {
    const cost = marketDrawCost(state, state.current_player);
    const auto = autoTakeAction(state);
    const deckBtn = document.createElement("button");
    deckBtn.textContent = t("draw_from_deck_btn", { cost });
    deckBtn.disabled = auto ? false : player.cash < cost || state.deck.length === 0;
    deckBtn.onclick = () => onAction({ type: "TAKE_FROM_DECK" });
    actionNode.appendChild(deckBtn);

    state.market.forEach((card, idx) => {
      const banned = companyOwner(state, card.company_id) === state.current_player;
      const btn = document.createElement("button");
      btn.textContent = t("take_market_btn", {
        idx: `${idx}`,
        name: companyName(card.company_id),
        coins: card.coins,
      });
      btn.disabled = banned;
      btn.onclick = () => onAction({ type: "TAKE_FROM_MARKET", index: idx });
      actionNode.appendChild(btn);
    });
  } else if (state.stage === STAGE_PLAY) {
    if (!player.hand.length) {
      actionNode.innerHTML = `<div class='muted'>${t("no_hand_skip")}</div>`;
    }
    player.hand.forEach((cardId, idx) => {
      const toPortfolio = document.createElement("button");
      toPortfolio.textContent = t("to_portfolio_btn", {
        idx,
        name: companyName(cardId),
      });
      toPortfolio.onclick = () => onAction({ type: "PLAY_TO_PORTFOLIO", index: idx });
      actionNode.appendChild(toPortfolio);

      const toMarket = document.createElement("button");
      const disabled = state.last_took_from_market && state.last_took_company === cardId;
      toMarket.textContent = t("to_market_btn", {
        idx,
        name: companyName(cardId),
      });
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
      row.textContent = t("score_line", {
        idx,
        total,
        cash: result.players[idx].cash,
        flipped: result.players[idx].flipped_coins,
        penalty: result.players[idx].penalty,
      });
      scoreboard.appendChild(row);
    });
    const winnerLine = document.createElement("div");
    winnerLine.className = "row winner";
    winnerLine.textContent = t("result_prefix", { winner: result.winner });
    scoreboard.appendChild(winnerLine);
  }

  const isHuman = !singlePlayer || state.current_player === 0;
  if (!isHuman) {
    actionNode.innerHTML = `<div class='row muted'>${t("ai_thinking")}</div>`;
    setTimeout(() => {
      const choose = autoTakeAction(state) || aiAction(state);
      if (choose) {
        onAction(choose, true);
        return;
      }
      actionNode.innerHTML = `<div class='row muted'>${t("ai_no_action")}</div>`;
    }, 600);
  }
}

function applyIfAllowed(action) {
  const result = applyAction(window.gameState, action);
  if (!result.accepted) {
    window.alert(result.message || t("game_action_invalid"));
    return;
  }
  window.gameState = result.state;
  render(window.gameState, window.singlePlayer);
}

function onAction(action, skipAlert) {
  const result = applyAction(window.gameState, action);
  if (!result.accepted) {
    if (!skipAlert) {
      window.alert(result.message || t("game_action_invalid"));
    } else {
      window.console.warn(result.message || t("game_action_invalid"));
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
    window.alert(t("players_limit"));
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
const zhBtn = document.getElementById("lang-zh");
const enBtn = document.getElementById("lang-en");
if (zhBtn) {
  zhBtn.addEventListener("click", () => setLocale("zh"));
}
if (enBtn) {
  enBtn.addEventListener("click", () => setLocale("en"));
}

window.onload = () => {
  const savedLocale = window.localStorage.getItem("startups-locale");
  if (savedLocale) {
    window.UI_LOCALE = savedLocale === "en" ? "en" : "zh";
  } else if (window.UI_LOCALE !== "en") {
    window.UI_LOCALE = "zh";
  }
  applyLocaleTexts();
  setRandomSeed();
};
