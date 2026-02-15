export interface Evidence {
  evidence: string
  signal_id: number
  content_url: string
  source_name: string
  signal_title: string
}

export interface Idea {
  id: number
  title: string
  description: string
  problem: string
  solution: string
  why_solana: string
  scale_potential: string
  market_signals?: string
  supporting_signals: string[]
  created_at: string
}

export interface Narrative {
  id: number
  title: string
  summary: string
  confidence: "high" | "medium" | "low"
  confidence_reasoning: string
  is_active: boolean
  velocity_score: number
  rank: number
  tags: string[]
  key_evidence: Evidence[]
  supporting_source_names: string[]
  idea_count: number
  ideas: Idea[]
  created_at: string
  updated_at: string
  last_detected_at: string
}

export interface Signal {
  id: number
  scraped_content_id: number
  signal_title: string
  description: string
  signal_type: string
  novelty: "high" | "medium" | "low"
  evidence: string
  related_projects: string[]
  tags: string[]
  created_at: string
  content_url: string
  content_title: string
  scraped_at: string
  data_source_id: number
  data_source_name: string
  data_source_url: string
  data_source_type: string
  data_source_category: string
}

export interface Stats {
  active_narratives_count: number
  total_narratives_count: number
  total_ideas_count: number
  avg_velocity_score: number
  active_builders: number
  sources_scraped_count: number
  total_signals_count: number
  last_web_scrape_time: string
  last_twitter_scrape_time: string
  next_synthesis_time: string
}

export const statsData: Stats = {
  active_narratives_count: 11,
  total_narratives_count: 11,
  total_ideas_count: 22,
  avg_velocity_score: 2.906,
  active_builders: 164,
  sources_scraped_count: 69,
  total_signals_count: 335,
  last_web_scrape_time: "2026-02-15T13:08:24.897695Z",
  last_twitter_scrape_time: "2026-02-15T10:14:09.289474Z",
  next_synthesis_time: "2026-03-01T13:11:27.571718Z",
}

export const narrativesData: Narrative[] = [
  {
    id: 5,
    title: "Institutional RWA Tokenization Explosion",
    summary:
      "Solana's RWA ecosystem hit $1.66B ATH with launches of tokenized gold (Matrixdock XAUm), 200+ US stocks/ETFs (Ondo), full regulated funds suite (WisdomTree), and supply chain finance (Citi). Multiple sources confirm 64% MoM growth in regulated onchain assets to $10B. This shift brings TradFi liquidity and composability to Solana DeFi, enabling 24/7 global access previously locked in legacy markets.",
    confidence: "high",
    confidence_reasoning:
      "Converges across Solana News (10+ signals), Solana Homepage, Reddit r/solana, Solana Compass; official @solana amplification; multiple independent issuers (Ondo, WisdomTree, Matrixdock, Citi).",
    is_active: true,
    velocity_score: 5.1,
    rank: 1,
    tags: ["rwa", "defi", "institutional"],
    key_evidence: [
      {
        evidence:
          "SPY, QQQ, NVDA, TSLA tokenized as DeFi assets enabling borrow, lend, leverage, yield on Solana",
        signal_id: 307,
        content_url:
          "https://www.reddit.com/r/solana/comments/1r29b4x/its_been_a_big_week_for_solana_here_are_8_big/",
        source_name: "Reddit r/solana",
        signal_title: "Tokenized Equities Live on Solana DeFi",
      },
      {
        evidence:
          "Matrixdock Expands XAUm to Solana, Enabling Institutional-Grade Tokenized Gold at Scale",
        signal_id: 152,
        content_url:
          "https://www.reddit.com/r/solana/comments/1r4oq0i/this_week_in_media_26213/",
        source_name: "Reddit r/solana",
        signal_title: "Matrixdock launches tokenized gold on Solana",
      },
      {
        evidence:
          "WisdomTree brings its full suite of regulated tokenized funds to Solana",
        signal_id: 258,
        content_url: "https://solana.com/news",
        source_name: "Solana News",
        signal_title: "Matrixdock Launches XAUm Tokenized Gold on Solana",
      },
      {
        evidence:
          "Solana's RWA ecosystem just hit a new ATH: $1.66B+ in tokenized value",
        signal_id: 30,
        content_url: "https://x.com/solana/status/2022947927413686542",
        source_name: "@solana",
        signal_title: "Solana RWA ecosystem hits new ATH",
      },
    ],
    supporting_source_names: [
      "Reddit r/solana",
      "Solana Compass",
      "Solana Homepage",
      "Solana News",
    ],
    idea_count: 3,
    created_at: "2026-02-15T11:15:36.483217Z",
    updated_at: "2026-02-15T13:11:27.596779Z",
    last_detected_at: "2026-02-15T13:11:00.731057Z",
    ideas: [
      {
        id: 17,
        title: "RWA Merchant Gateway",
        description:
          "API for merchants to accept tokenized stocks/gold as payment, auto-converting to USDC/SOL at point-of-sale via Solflare Card-style integration.",
        problem:
          "RWAs unspendable in real-world commerce despite Solana payment tech superiority (signal 329).",
        solution:
          "Unlocks organic RWA demand via commerce; Solflare Card precedent (signals 3-5) proves token spendability works.",
        why_solana:
          "Fast/cheap txns + SPL standard unify fragmented assets; mobile wallet ecosystem (Solana Mobile signals) aids onboarding.",
        scale_potential:
          "E-commerce TAM $6T+; network effects as more RWAs onboard, similar to Shopify crypto payments but onchain-native.",
        market_signals:
          "Solflare Card any-SPL spending (signals 3,4,5); commerce frustration (signal 329).",
        supporting_signals: [
          "Solflare Card enables spending any SPL token",
          "Community frustration over lack of SOL spending vs trading",
        ],
        created_at: "2026-02-15T13:11:27.544168Z",
      },
      {
        id: 18,
        title: "Institutional RWA Compliance Dashboard",
        description:
          "Real-time PoR dashboard for RWA issuers integrating Chainlink/Tessera proofs with onchain analytics for TradFi compliance reporting.",
        problem:
          "Institutions need verifiable reserves for RWAs but lack unified tooling (signals 312, 313).",
        solution:
          "Capitalize on Tessera/Chainlink momentum; regulatory clarity from Anatoly CFTC role (signals 322,155) accelerates.",
        why_solana:
          "High-frequency proofs + low costs suit institutional scale; Alpenglow 150ms finality ensures audit-grade timestamps.",
        scale_potential:
          "Every RWA issuer needs this; $1.66B TVL demands compliance layer, comparable to Chainlink CCIP growth.",
        market_signals:
          "Tessera x Chainlink PoR (signals 312,313); RWA ATH $1.66B (signal 30).",
        supporting_signals: [
          "Tessera integrates Chainlink Proof of Reserve",
          "Ondo Global Markets Launches 200+ Tokenized US Stocks",
        ],
        created_at: "2026-02-15T13:11:27.544168Z",
      },
      {
        id: 16,
        title: "RWA Yield Optimizer",
        description:
          "Automated vault that allocates across Solana RWAs (stocks, gold, funds) for optimized yield via lending/borrowing while maintaining 24/7 liquidity and rebalancing based on onchain rates.",
        problem:
          "Fragmented RWA liquidity across issuers prevents optimal yield farming; signals show Ondo/Jupiter integration but no unified optimizer (signals 236, 307).",
        solution:
          "Leverage Solana's composability for auto-compounding strategies now viable with native tokenized assets; post-RWA ATH timing perfect for capture.",
        why_solana:
          "Sub-second settlement + low fees enable real-time rebalancing impossible on slower chains; existing Jupiter integration accelerates.",
        scale_potential:
          "TAM = $10B+ regulated RWAs + growing TradFi inflows; comparable to Yearn on ETH ($500M+ TVL) but with 24/7 stocks/gold.",
        market_signals:
          "64% MoM RWA growth (signal 257), Ondo 200+ assets (signal 235), WisdomTree $116B AUM entry (signal 238).",
        supporting_signals: [
          "Tokenized Equities Live on Solana DeFi",
          "Matrixdock launches tokenized gold on Solana",
        ],
        created_at: "2026-02-15T13:11:27.544163Z",
      },
    ],
  },
  {
    id: 10,
    title: "Developer Tooling Arms Race for Latency & Reliability",
    summary:
      "Helius launches Gatekeeper (4.6x faster RPC), gTFA (3-10x speedup), LaserStream, Orb explorer; Raydium LaunchLab vs Pump.fun; bundler demand surges. Agave 3.1 + Alpenglow signal core infra push. Signals indicate convergence on performance as table stakes for HFT/MEV/memecoin trading.",
    confidence: "high",
    confidence_reasoning:
      "Heavy Helius Blog coverage (10+ signals) + Reddit dev tools demand (332,325,140); cross-source with Solana News upgrades.",
    is_active: true,
    velocity_score: 4.5,
    rank: 2,
    tags: ["infrastructure", "rpc", "developer-tooling", "performance"],
    key_evidence: [
      {
        evidence:
          "Helius getTransactionsForAddress RPC with 3-10x speedup",
        signal_id: 140,
        content_url:
          "https://www.reddit.com/r/solana/comments/1r3rytx/fetching_transaction_history_on_solana_now_call/",
        source_name: "Reddit r/solana",
        signal_title:
          "Helius Launches getTransactionsForAddress RPC with 3-10x Speedup",
      },
      {
        evidence:
          "Gatekeeper reduces RPC latency 4.6x cold (27ms vs 123ms), 7.8x warm",
        signal_id: 197,
        content_url:
          "https://www.helius.dev/blog/introducing-gatekeeper",
        source_name: "Helius Blog",
        signal_title:
          "Helius launches Gatekeeper edge gateway for sub-ms latency",
      },
      {
        evidence: "Raydium LaunchLab as Pump.fun competitor",
        signal_id: 334,
        content_url:
          "https://www.reddit.com/r/solana/comments/1r5dvdd/took_me_4_rugs_to_figure_out_where_to_buy_meme/",
        source_name: "Reddit r/solana",
        signal_title: "Raydium LaunchLab as Pump.fun competitor",
      },
      {
        evidence: "Alpenglow slashes Solana latency to 150ms",
        signal_id: 306,
        content_url:
          "https://www.reddit.com/r/solana/comments/1r29b4x/its_been_a_big_week_for_solana_here_are_8_big/",
        source_name: "Reddit r/solana",
        signal_title: "Alpenglow Slashes Solana Latency to 150ms",
      },
    ],
    supporting_source_names: ["Helius Blog", "Reddit r/solana"],
    idea_count: 3,
    created_at: "2026-02-15T13:11:27.564835Z",
    updated_at: "2026-02-15T13:11:27.599200Z",
    last_detected_at: "2026-02-15T13:11:00.731057Z",
    ideas: [
      {
        id: 24,
        title: "Rent Reclaimer Automation Suite",
        description:
          "No-code dashboard automating SOL rent reclamation across wallets with community-voted UI/fee transparency improvements.",
        problem:
          "Community-driven iterations show grassroots demand (signals 332,148).",
        solution:
          "Build on Reddit feedback loops; state rent reduction (signal 195) amplifies value.",
        why_solana:
          "Rent mechanics unique to Solana; 90% cheaper post-reduction unlocks mass adoption.",
        scale_potential:
          "Billions in reclaimable SOL; viral via wallet integrations like Phantom.",
        market_signals:
          "Developer rebuilt based on Reddit feedback (signals 332,148).",
        supporting_signals: [
          "Community-driven SOL rent reclaimer tool iteration",
          "State Rent Reduction Initiative Begins",
        ],
        created_at: "2026-02-15T13:11:27.568702Z",
      },
      {
        id: 23,
        title: "MEV Explorer & Simulator",
        description:
          "Real-time MEV dashboard using gTFA/LaserStream for bundle simulation, profitability analysis, and backtesting across Jito/Helius.",
        problem:
          "Traders lack visibility into landing rates/fees; Helius tools expose demand (signals 166,197).",
        solution:
          "Leverage new RPCs for accurate sims; Agave/Alpenglow upgrades boost precision.",
        why_solana:
          "MEV infra (Jito) + fastest RPCs (Helius Gatekeeper) enable real-time edge vs slower chains.",
        scale_potential:
          "MEV market $1B+ annually; network effects as more bots integrate.",
        market_signals:
          "Gatekeeper 7.8x speedup (signal 197); gTFA launch (signal 166).",
        supporting_signals: [
          "New getTransactionsForAddress RPC Method",
          "Helius launches Gatekeeper edge gateway",
        ],
        created_at: "2026-02-15T13:11:27.568701Z",
      },
      {
        id: 22,
        title: "Bundler Marketplace",
        description:
          "Permissionless marketplace for pump.fun bundlers with reputation scoring, backtesting, and auto-switching based on landing rates.",
        problem:
          "Sniper bots beat launches; repeated Reddit demand for reputable bundlers (signals 325,139).",
        solution:
          "Post-LaunchLab competition + Helius Sender tools create perfect timing; aggregate best performers.",
        why_solana:
          "Memecoin frenzy + Jito bundles demand specialized tooling; low fees enable micro-payments for bundles.",
        scale_potential:
          "Pump.fun dominance = massive volume; comparable to HFT colocation services ($B market).",
        market_signals:
          "Bundler bot demand (signals 325,139); Raydium LaunchLab (signal 334).",
        supporting_signals: [
          "Rising demand for bundler bots in pump.fun launches",
          "Raydium LaunchLab as Pump.fun competitor",
        ],
        created_at: "2026-02-15T13:11:27.568700Z",
      },
    ],
  },
  {
    id: 7,
    title: "Core Infrastructure Maturity & Validator Evolution",
    summary:
      "SFDP stake share fell to 5.9% with 121% growth in independent validators; SIMD upgrades (100M CUs, Alpenglow 150ms, revenue sharing) + Firedancer live signal maturing base layer. Helius tooling (Gatekeeper, LaserStream) addresses HFT needs. Cross-source dev signals show shift to production-grade infra.",
    confidence: "high",
    confidence_reasoning:
      "Heavy Solana News coverage (248-251, 240-246) + Helius (197,210) + Reddit/Syndica dev reports.",
    is_active: true,
    velocity_score: 4.0,
    rank: 3,
    tags: ["infrastructure", "validators", "performance", "developer"],
    key_evidence: [
      {
        evidence:
          "SFDP's share of total staked SOL fell from 44.4% at launch to 5.9% by Epoch 881... non-SFDP stake grew by ~230%.",
        signal_id: 248,
        content_url:
          "https://solana.com/news/solana-foundation-delegation-program-case-study",
        source_name: "Solana News",
        signal_title:
          "SFDP Stake Share Declines to 5.9% Amid 230% Non-SFDP Stake Growth",
      },
      {
        evidence:
          "Alpenglow is a state-of-the-art consensus protocol that will bring 150ms confirmation times to Solana.",
        signal_id: 242,
        content_url:
          "https://solana.com/news/solana-network-upgrades",
        source_name: "Solana News",
        signal_title: "Alpenglow Consensus for 150ms Confirmations",
      },
      {
        evidence:
          "Gatekeeper achieves ~26 ms with new connection and ~0.5 ms with reused connection... targeting high-frequency trading and MEV workloads.",
        signal_id: 197,
        content_url:
          "https://www.helius.dev/blog/introducing-gatekeeper",
        source_name: "Helius Blog",
        signal_title:
          "Helius launches Gatekeeper edge gateway for sub-ms latency",
      },
    ],
    supporting_source_names: [
      "Helius Blog",
      "Reddit r/solana",
      "Solana News",
    ],
    idea_count: 2,
    created_at: "2026-02-15T11:15:36.629790Z",
    updated_at: "2026-02-15T11:15:36.674039Z",
    last_detected_at: "2026-02-15T11:15:06.641847Z",
    ideas: [
      {
        id: 13,
        title: "HFT Transaction Bundler",
        description:
          "Bundler using Gatekeeper + Shred Delivery for <1ms tx landing, parallel Jito/Helius sends.",
        problem:
          "Leader-dependent PropAMMs (234); Helius Sender for traders (163).",
        solution:
          "Combine XDP + 100M CUs; infra ready post-upgrades.",
        why_solana:
          "Alpenglow 150ms + Firedancer 1M TPS (222).",
        scale_potential:
          "CEX-level HFT onchain; $543B PropAMM volume (33).",
        market_signals:
          "Helius Gatekeeper 7.8x faster (197); Shred Delivery beta (159).",
        supporting_signals: [
          "Helius launches Gatekeeper edge gateway for sub-ms latency",
          "Helius Launches Shred Delivery Beta",
        ],
        created_at: "2026-02-15T11:15:36.636752Z",
      },
      {
        id: 12,
        title: "Validator Revenue Optimizer",
        description:
          "Dashboard auto-configures commission splits (inflation vs block revenue, signal 240) and delegates to top independent validators based on IBRL scores.",
        problem:
          "Validators maturing but complex revenue sharing (243); Magic Eden pushes independents (27).",
        solution:
          "Use Vote V4 + SIMD-123; now with SFDP exit signaling market-driven era.",
        why_solana:
          "Block revenue distribution native (243); 121% independent validator growth (249).",
        scale_potential:
          "Stake = 70%+ of SOL supply; like Lido but decentralized.",
        market_signals:
          "Magic Eden 0% comm validator (26); Jito IBRL explorer (179).",
        supporting_signals: [
          "Block Revenue Distribution to Delegators",
          "Magic Eden launches independent Solana validator",
        ],
        created_at: "2026-02-15T11:15:36.636751Z",
      },
    ],
  },
  {
    id: 8,
    title: "AI Agents & Natural Language Interfaces",
    summary:
      "Solflare Magic AI wallets, Solana Bench LLM benchmarks, OpenClaw payments via Lobster.cash, and agent hackathons signal shift to non-human economy on Solana. Foundation funding + Breakpoint demos show dev tooling maturation. Converges across News, Reddit, Compass.",
    confidence: "medium",
    confidence_reasoning:
      "Multiple mentions in Breakpoint (226), Reddit (121,153), Compass (43), but fewer onchain signals vs RWA.",
    is_active: true,
    velocity_score: 3.86,
    rank: 4,
    tags: ["ai", "agents", "wallets", "developer"],
    key_evidence: [
      {
        evidence:
          "Solflare: Demoed Magic AI, a natural language interface where users type 'Swap my USDC for SOL if the price increases above $150.'",
        signal_id: 226,
        content_url:
          "https://solana.com/news/solana-breakpoint-2025",
        source_name: "Solana News",
        signal_title: "AI Agents and Natural Language Wallets",
      },
      {
        evidence:
          "Solana Foundation Launches Solana Bench for LLM Transaction Building... test LLMs' ability to build and execute complex Solana transactions.",
        signal_id: 215,
        content_url: "https://solana.com/news/solana-bench",
        source_name: "Solana News",
        signal_title:
          "Solana Foundation Launches Solana Bench for LLM Transaction Building",
      },
      {
        evidence:
          "lobster.cash... secure payment layer for over 1M deployed OpenClaw agents using cards and stablecoins on Solana.",
        signal_id: 121,
        content_url:
          "https://www.reddit.com/r/solana/comments/1r32sb6/crossmint_announced_httplobstercash_the_open/",
        source_name: "Reddit r/solana",
        signal_title:
          "Crossmint Launches Lobster.cash for OpenClaw Agent Payments on Solana",
      },
    ],
    supporting_source_names: [
      "@metaplex",
      "Reddit r/solana",
      "Solana Compass",
      "Solana News",
    ],
    idea_count: 2,
    created_at: "2026-02-15T11:15:36.643705Z",
    updated_at: "2026-02-15T11:15:36.675022Z",
    last_detected_at: "2026-02-15T11:15:06.641847Z",
    ideas: [
      {
        id: 15,
        title: "LLM Transaction Builder SDK",
        description:
          "SDK wrapping Solana Bench environments for production agent tx building, with safety rails for complex DeFi/Jupiter swaps.",
        problem:
          "No reproducible LLM evals for Solana (215); Foundation funding benchmarks (216).",
        solution:
          "Fine-tune on Basic/Swap envs; agent economy emerging.",
        why_solana:
          "SVM ISA formal spec (184) + P-Token 95% compute reduction (212).",
        scale_potential:
          "Every wallet becomes agent interface; like Infura for AI.",
        market_signals:
          "Solana Foundation funding LLM benchmarks (216).",
        supporting_signals: [
          "Solana Foundation Launches Solana Bench for LLM Transaction Building",
        ],
        created_at: "2026-02-15T11:15:36.648676Z",
      },
      {
        id: 14,
        title: "Agent Payment Rails",
        description:
          "Universal payment adapter for AI agents using Solflare Magic + Lobster.cash, auto-swapping any SPL to USDC for card spends.",
        problem:
          "Agents can't hold bank accounts but need payments (226); Lobster.cash for OpenClaw (121).",
        solution:
          "Natural language tx building via Bench (215); now with 1M+ agents deployed.",
        why_solana:
          "Cheap state (rent 90% down, 241) + Mobile Kit for 2B devices (225).",
        scale_potential:
          "1M+ OpenClaw agents; TAM = AI economy payments.",
        market_signals:
          "Crossmint Lobster.cash launch (121); Solflare Magic demo (226).",
        supporting_signals: [
          "AI Agents and Natural Language Wallets",
          "Crossmint Launches Lobster.cash",
        ],
        created_at: "2026-02-15T11:15:36.648675Z",
      },
    ],
  },
  {
    id: 9,
    title: "Privacy Infrastructure Maturing with Hackathon Momentum",
    summary:
      "Solana Privacy Hackathon produced 47 submissions using MagicBlock's Private Ephemeral Rollups for private prediction markets, payroll, bookings; Arcium announces CSPL confidential tokens Q1 2026. Graveyard Hack targets privacy-dead categories. Signals shift from theoretical to production-ready apps, enabling confidential DeFi/gaming.",
    confidence: "high",
    confidence_reasoning:
      "Cross-validated in Reddit r/solana (multiple signals), Solana Compass, Helius Blog; hackathon results + Arcium announcement show builder convergence.",
    is_active: true,
    velocity_score: 3.3,
    rank: 5,
    tags: ["privacy", "infrastructure", "hackathon", "rollup"],
    key_evidence: [
      {
        evidence:
          "47 submissions; top projects: private prediction markets (Swiv), payroll (Bagel), using Private Ephemeral Rollups",
        signal_id: 326,
        content_url:
          "https://www.reddit.com/r/solana/comments/1r3yjlz/the_solana_privacy_hackathon_has_officially/",
        source_name: "Reddit r/solana",
        signal_title:
          "Solana Privacy Hackathon Reveals Winning Projects Using Private Ephemeral Rollups",
      },
      {
        evidence:
          "Arcium unveils CSPL confidential token standard launching Q1 2026 on Solana",
        signal_id: 267,
        content_url: "https://solanacompass.com/",
        source_name: "Solana Compass",
        signal_title:
          "Arcium Announces Confidential Token Standard CSPL",
      },
      {
        evidence:
          "Graveyard Hackathon targeting 'dead' categories including privacy with $75K prizes",
        signal_id: 319,
        content_url:
          "https://www.reddit.com/r/solana/comments/1r31ttj/graveyard_hack_for_art_nfts_onchain_social_gaming/",
        source_name: "Reddit r/solana",
        signal_title:
          "Solana Graveyard Hackathon Launch with $75K Prizes",
      },
    ],
    supporting_source_names: ["Reddit r/solana", "Solana Compass"],
    idea_count: 3,
    created_at: "2026-02-15T13:11:27.554568Z",
    updated_at: "2026-02-15T13:11:27.598167Z",
    last_detected_at: "2026-02-15T13:11:00.731057Z",
    ideas: [
      {
        id: 21,
        title: "ZK Privacy Wallet Shield",
        description:
          "Wallet add-on using Light Protocol ZK (200x cheaper than SPL) + CSPL for shielding DeFi positions from chain analysis.",
        problem:
          "Privacy primitives fragmented; hackathons show convergence (signals 326,223).",
        solution:
          "Consumer-facing layer atop maturing infra; Solflare Magic AI precedent for UX (signal 266).",
        why_solana:
          "ZK compression + rollups cheapest privacy; mobile stack aids consumer onboarding.",
        scale_potential:
          "Every wallet user needs privacy; comparable to Tornado Cash but compliant/onchain.",
        market_signals:
          "Light Token 200x cheaper ZK (signal 223); privacy hackathon 47 submissions (signal 326).",
        supporting_signals: [
          "Privacy and Cheap State Primitives Emerge",
          "Arcium Announces Confidential Token Standard CSPL",
        ],
        created_at: "2026-02-15T13:11:27.561372Z",
      },
      {
        id: 20,
        title: "Confidential Prediction Market Aggregator",
        description:
          "DEX aggregator for private prediction markets (Swiv-style) routing via PER for anonymous positions across Solana PMs.",
        problem:
          "Public bets expose strategies; Swiv proves private PMs viable (signal 326).",
        solution:
          "Post-hackathon primitives ready; DFlow/Kalshi integration (signals 263,256) provides liquidity.",
        why_solana:
          "High TPS + privacy rollups enable real-time anonymous trading vs Ethereum gas limits.",
        scale_potential:
          "PM market $100B+ TradFi equivalent; composability with DeFi yields explosive growth.",
        market_signals:
          "Swiv 1st place hackathon (signal 326); DFlow Kalshi launch (signal 263).",
        supporting_signals: [
          "Solana Privacy Hackathon Winners Showcase Private Ephemeral Rollups",
          "DFlow Launches Kalshi Prediction Markets Tokenization",
        ],
        created_at: "2026-02-15T13:11:27.561371Z",
      },
      {
        id: 19,
        title: "Private Payroll Processor",
        description:
          "Onchain payroll using MagicBlock PER for confidential salary streaming compliant with tax reporting, integrating Bagel hackathon prototype.",
        problem:
          "Public ledgers expose salary data; hackathon shows demand for private payroll (signal 326).",
        solution:
          "PER enables compliant confidentiality now battle-tested via hackathon; Arcium CSPL adds token privacy.",
        why_solana:
          "Ephemeral rollups + low fees suit streaming payments; hackathon proves developer readiness.",
        scale_potential:
          "Global payroll TAM $6T; crypto payroll underserved, network effects via employer/employee adoption.",
        market_signals:
          "Bagel payroll hackathon winner (signal 326); CSPL Q1 launch (signal 267).",
        supporting_signals: [
          "Solana Privacy Hackathon Reveals Winning Projects",
          "Arcium Announces Confidential Token Standard CSPL",
        ],
        created_at: "2026-02-15T13:11:27.561369Z",
      },
    ],
  },
  {
    id: 6,
    title: "Tokenized Prediction Markets API",
    summary:
      "DFlow launched the first tokenization layer for Kalshi's regulated prediction markets on Solana, enabling fully composable SPL tokens with 100% market coverage and $2M grants. This shifts prediction markets from CEX/speculative to DeFi primitives, validated across Solana News, Reddit, and Breakpoint signals.",
    confidence: "high",
    confidence_reasoning:
      "Multiple signals from Solana News (263,256,217,219), Reddit (153), cross-validated with grants program.",
    is_active: true,
    velocity_score: 2.9,
    rank: 6,
    tags: ["prediction-markets", "defi", "tokenization"],
    key_evidence: [
      {
        evidence:
          "DFlow launches the first tokenization layer bringing Kalshi's prediction markets to Solana, enabling developers to integrate real prediction market tokens with full composability and 100% market coverage.",
        signal_id: 263,
        content_url: "https://solana.com/news",
        source_name: "Solana News",
        signal_title:
          "DFlow Launches Kalshi Prediction Markets Tokenization on Solana",
      },
      {
        evidence:
          "Kalshi is backing the ecosystem with a $2M grants program to fund new applications built on top.",
        signal_id: 219,
        content_url:
          "https://solana.com/news/dflow-prediction-markets-api",
        source_name: "Solana News",
        signal_title:
          "Kalshi launches $2M grants program for Solana prediction market apps",
      },
    ],
    supporting_source_names: ["Reddit r/solana", "Solana News"],
    idea_count: 2,
    created_at: "2026-02-15T11:15:36.621898Z",
    updated_at: "2026-02-15T11:15:36.672023Z",
    last_detected_at: "2026-02-15T11:15:06.641847Z",
    ideas: [
      {
        id: 11,
        title: "Prediction Market Collateral Lending",
        description:
          "Lend/borrow against tokenized PM positions as collateral in Kamino-style markets.",
        problem:
          "PM winners locked until resolution; DFlow tokens enable use as collateral now.",
        solution:
          "Integrate with Kamino's RWA DEX (227); high novelty timing.",
        why_solana:
          "CPI nesting to 8 levels (246) for complex PM + lending calls.",
        scale_potential:
          "Unlocks $B+ PM liquidity; network effects as more markets tokenize.",
        market_signals: "DFlow's CLPs bridge offchain liquidity (218).",
        supporting_signals: [
          "Introduction of Concurrent Liquidity Programs (CLPs)",
          "Kamino Evolves to Institutional Yield Stack",
        ],
        created_at: "2026-02-15T11:15:36.626728Z",
      },
      {
        id: 10,
        title: "PM Derivatives DEX",
        description:
          "Perps and options on tokenized Kalshi markets, e.g. long election outcome while hedging with inverse PM tokens.",
        problem:
          "No composability for PMs; DFlow enables but no trading venues (263).",
        solution:
          "Use CLPs for offchain liquidity (218); grants fund builds (219).",
        why_solana:
          "High-frequency updates via PropAMMs (233) + XDP 200x latency reduction (244).",
        scale_potential:
          "Kalshi's regulated volume + Solana's $15B stablecoins; like Polymarket but composable.",
        market_signals: "$2M grants program (219).",
        supporting_signals: [
          "DFlow Launches Kalshi Prediction Markets Tokenization on Solana",
          "Kalshi launches $2M grants program",
        ],
        created_at: "2026-02-15T11:15:36.626726Z",
      },
    ],
  },
  {
    id: 11,
    title: "Gaming & 'Dead' Category Revival via Hackathons",
    summary:
      "Graveyard Hack ($75K prizes) targets reviving Art/NFTs/Gaming/DAOs; Solana games 'getting crazy during bear market' gains Reddit traction. Counter-cyclical builder activity amid meme fatigue (90% losses, signal 327). Signals grassroots pivot to sustainable consumer apps.",
    confidence: "medium",
    confidence_reasoning:
      "Strong Reddit convergence (signals 319,129,323,324) + hackathon launch; lower confidence vs RWAs due to fewer sources.",
    is_active: true,
    velocity_score: 2.56,
    rank: 7,
    tags: ["gaming", "nfts", "hackathon", "consumer"],
    key_evidence: [
      {
        evidence:
          "Graveyard Hackathon $75K prizes targeting dead categories: Art, NFTs, Gaming, DAOs",
        signal_id: 319,
        content_url:
          "https://www.reddit.com/r/solana/comments/1r31ttj/graveyard_hack_for_art_nfts_onchain_social_gaming/",
        source_name: "Reddit r/solana",
        signal_title:
          "Solana Graveyard Hackathon Launch with $75K Prizes",
      },
      {
        evidence:
          "Solana games getting crazy during bear market; Score: 5 | Comments: 4",
        signal_id: 323,
        content_url:
          "https://www.reddit.com/r/solana/comments/1r3ioho/solana_games_getting_crazy_during_bear_market/",
        source_name: "Reddit r/solana",
        signal_title: "Solana games surging in bear market",
      },
    ],
    supporting_source_names: ["Reddit r/solana"],
    idea_count: 1,
    created_at: "2026-02-15T13:11:27.571718Z",
    updated_at: "2026-02-15T13:11:27.600196Z",
    last_detected_at: "2026-02-15T13:11:00.731057Z",
    ideas: [
      {
        id: 25,
        title: "Bear Market Game Studio Toolkit",
        description:
          "No-code toolkit for hackathon-style games with onchain leaderboards, tokenized rewards, and mobile-first templates using Solana Mobile primitives.",
        problem:
          "Games surging in bear (signal 323) but lack standardized tooling; Graveyard Hack bounties show demand.",
        solution:
          "Capitalize on counter-cyclical momentum; Solana Mobile Mtndao hack (signal 310) proves mobile focus.",
        why_solana:
          "Saga/Seeker diagnostics + low fees suit casual gaming; hackathons validate primitives.",
        scale_potential:
          "$200B mobile gaming TAM; viral via airdrops like Parallel.",
        market_signals:
          "Solana games bear market surge (signal 323); Graveyard Gaming track (signal 319).",
        supporting_signals: [
          "Solana games surging in bear market",
          "Solana Graveyard Hackathon Launch",
        ],
        created_at: "2026-02-15T13:11:27.576346Z",
      },
    ],
  },
  {
    id: 1,
    title: "RWA Tokenization Accelerating on Solana",
    summary:
      "Solana's RWA ecosystem hit $1.66B ATH with official amplification, while wallets like Solflare demonstrate practical spendability of tokenized stocks via debit cards. This marks a shift from speculative DeFi to real-world asset utility. Matters because it bridges TradFi and Solana, unlocking institutional capital flows.",
    confidence: "high",
    confidence_reasoning:
      "Cross-validated by official Solana account (signal_ids 30,31) and Solflare consumer integration (signal_id 4), multiple high-novelty signals from core ecosystem accounts.",
    is_active: true,
    velocity_score: 2.1,
    rank: 8,
    tags: ["rwa", "consumer", "payments", "defi"],
    key_evidence: [
      {
        evidence:
          "Solana's RWA ecosystem just hit a new ATH: $1.66B+ in tokenized value",
        signal_id: 30,
        content_url:
          "https://x.com/solana/status/2022947927413686542",
        source_name: "@solana",
        signal_title: "Solana RWA ecosystem hits new ATH",
      },
      {
        evidence: "Official amplification of RWA growth milestone",
        signal_id: 31,
        content_url:
          "https://x.com/solana/status/2022947927413686542",
        source_name: "@solana",
        signal_title: "Official amplification of RWA growth",
      },
      {
        evidence:
          "xStocks integration with Solflare Card for spending tokenized stocks",
        signal_id: 4,
        content_url:
          "https://x.com/solflare/status/2021513881697529978",
        source_name: "@solflare",
        signal_title: "xStocks integration with Solflare Card",
      },
    ],
    supporting_source_names: ["@solana", "@solflare"],
    idea_count: 2,
    created_at: "2026-02-15T10:23:15.816874Z",
    updated_at: "2026-02-15T10:23:15.917108Z",
    last_detected_at: "2026-02-15T10:22:58.779517Z",
    ideas: [
      {
        id: 2,
        title: "RWA Card Aggregator",
        description:
          "Meta-wallet that unifies multiple RWA spend cards (Solflare + others) with auto-conversion, cashback in RWA yields, and merchant acceptance mapping.",
        problem:
          "Siloed card integrations limit RWA spendability (signal 3,4 show early Solflare support but fragmented).",
        solution:
          "Builds on demonstrated SPL spendability; now viable with RWA TVL growth.",
        why_solana:
          "Universal SPL token standard enables any RWA spending; compressed transactions keep costs near-zero.",
        scale_potential:
          "Visa/Mastercard TAM $30T; viral via cashback loops; expands beyond crypto to TradFi users.",
        market_signals:
          "Solflare Card enables spending xStocks/USDT/BONK (signal 3), official RWA push (signal 31).",
        supporting_signals: [
          "Solflare Card enables spending any SPL token",
          "Official amplification of RWA growth",
        ],
        created_at: "2026-02-15T10:23:15.835880Z",
      },
      {
        id: 1,
        title: "RWA Yield Optimizer",
        description:
          "Automated platform that scans RWA protocols for highest yields, auto-compounds tokenized treasuries/bonds, and provides one-click entry/exit ramps to stablecoins.",
        problem:
          "Fragmented RWA liquidity across protocols makes yield optimization manual and risky (signals 30,31 show growth but no unified access).",
        solution:
          "Leverages Solana's speed for real-time yield scanning; timed perfectly with $1.66B ATH signaling liquidity influx.",
        why_solana:
          "Sub-second finality for arbitrage, low fees for frequent rebalancing, native SPL token support for RWAs.",
        scale_potential:
          "TAM mirrors BlackRock's $10T bond funds; network effects from shared yield intel; comparable to Yearn on ETH but 100x cheaper.",
        market_signals:
          "$1.66B ATH tokenized value (signal 30), Solflare card integration proving consumer demand (signal 4).",
        supporting_signals: [
          "Solana RWA ecosystem hits new ATH",
          "xStocks integration with Solflare Card",
        ],
        created_at: "2026-02-15T10:23:15.835874Z",
      },
    ],
  },
  {
    id: 3,
    title: "AI Agents Powered by New Asset Standards",
    summary:
      "Metaplex highlights Core asset signer + Genesis enabling previously impossible agent features on Solana. This unlocks autonomous AI agents holding/managing assets. Represents shift from human-driven to agent-driven economy on Solana.",
    confidence: "medium",
    confidence_reasoning:
      "High novelty developer signals from Metaplex (signal_ids 8,9) but single-source; technically compelling.",
    is_active: true,
    velocity_score: 1.36,
    rank: 9,
    tags: ["agents", "ai", "infrastructure", "developer-tooling"],
    key_evidence: [
      {
        evidence:
          "Metaplex powers agents on Solana using Core asset signer and Genesis",
        signal_id: 8,
        content_url:
          "https://x.com/metaplex/status/2022392527152910405",
        source_name: "@metaplex",
        signal_title:
          "Metaplex enables AI agents with Core asset signer and Genesis",
      },
      {
        evidence:
          "Core asset signer and Genesis enable new agent possibilities",
        signal_id: 9,
        content_url:
          "https://x.com/metaplex/status/2022392527152910405",
        source_name: "@metaplex",
        signal_title:
          "Core asset signer and Genesis enable new agent possibilities",
      },
    ],
    supporting_source_names: ["@metaplex"],
    idea_count: 1,
    created_at: "2026-02-15T10:23:15.894449Z",
    updated_at: "2026-02-15T10:23:15.919810Z",
    last_detected_at: "2026-02-15T10:22:58.779517Z",
    ideas: [
      {
        id: 5,
        title: "Agent Asset Manager",
        description:
          "No-code platform for deploying AI agents that autonomously manage NFT/RWA portfolios based on market signals and user goals.",
        problem:
          "New primitives exist but no user-friendly agent deployment layer (signals 8,9).",
        solution:
          "Builds directly on Metaplex/Core/Genesis stack just announced.",
        why_solana:
          "Account abstraction + asset signers enable true agent autonomy; sub-cent tx costs.",
        scale_potential:
          "Robinhood TAM for AI advisors; composability creates agent economy.",
        market_signals:
          "Metaplex confirms agent viability with new standards (signals 8,9).",
        supporting_signals: [
          "Metaplex enables AI agents with Core asset signer and Genesis",
          "Core asset signer and Genesis enable new agent possibilities",
        ],
        created_at: "2026-02-15T10:23:15.896593Z",
      },
    ],
  },
  {
    id: 2,
    title: "Validator Decentralization Push",
    summary:
      "Magic Eden launched 0% commission validator and urgently called for independent validator support, signaling validator concentration crisis. This represents a decentralization imperative amid network growth. Critical for Solana's long-term resilience against censorship and outages.",
    confidence: "medium",
    confidence_reasoning:
      "Strong signals from major NFT marketplace (signal_ids 26,27,28) but limited cross-source validation beyond Magic Eden.",
    is_active: true,
    velocity_score: 1.36,
    rank: 10,
    tags: ["infrastructure", "validator", "decentralization", "staking"],
    key_evidence: [
      {
        evidence:
          "'There has maybe never been a more important time to support independent validators'",
        signal_id: 27,
        content_url:
          "https://x.com/MagicEden/status/2021381957536424402",
        source_name: "@MagicEden",
        signal_title:
          "Urgent push for independent Solana validators",
      },
      {
        evidence:
          "Magic Eden validator with 0% commission and 100% revenue $ME buyback",
        signal_id: 26,
        content_url:
          "https://x.com/MagicEden/status/2021381957536424402",
        source_name: "@MagicEden",
        signal_title:
          "Magic Eden launches independent Solana validator with 0% commission",
      },
    ],
    supporting_source_names: ["@MagicEden"],
    idea_count: 2,
    created_at: "2026-02-15T10:23:15.889101Z",
    updated_at: "2026-02-15T10:23:15.918565Z",
    last_detected_at: "2026-02-15T10:22:58.779517Z",
    ideas: [
      {
        id: 4,
        title: "Validator Revenue Sharing Pool",
        description:
          "Liquid staking pool that auto-allocates stakes across independent validators, sharing MEV/commission revenue via onchain DAO.",
        problem:
          "Independent validators struggle with low commissions vs centralized ones (signal 26 model).",
        solution:
          "Extends Magic Eden's 0% + revenue buyback model to all independents.",
        why_solana:
          "Jito MEV + stake delegation primitives enable sophisticated revenue routing.",
        scale_potential:
          "EigenLayer-style restaking TAM; captures growing LST demand.",
        market_signals:
          "Magic Eden's community-centric validator model (signal 26).",
        supporting_signals: [
          "Magic Eden launches independent Solana validator with 0% commission",
        ],
        created_at: "2026-02-15T10:23:15.892415Z",
      },
      {
        id: 3,
        title: "Validator Scorecard Dashboard",
        description:
          "Real-time dashboard ranking validators by decentralization metrics, performance, commission, and MEV resistance with one-click delegation.",
        problem:
          "Users lack transparency to choose truly independent validators amid urgent calls (signal 27).",
        solution:
          "Capitalizes on Magic Eden's validator precedent; provides missing discovery layer.",
        why_solana:
          "Native stake program + RPC data enables comprehensive metrics; low-cost UI updates.",
        scale_potential:
          "Recurring $SOL staking fees; Lido-like dominance possible; mandatory for institutions.",
        market_signals:
          "Magic Eden's urgent validator support call (signal 27), 0% commision launch (signal 26).",
        supporting_signals: [
          "Urgent push for independent Solana validators",
          "Magic Eden launches independent Solana validator",
        ],
        created_at: "2026-02-15T10:23:15.892413Z",
      },
    ],
  },
]

export const signalsData: Signal[] = [
  {
    id: 335,
    scraped_content_id: 190,
    signal_title:
      "Post-$TRUMP $LIBRA skepticism shift in meme coin trading",
    description:
      "Community sentiment has shifted to higher skepticism after recent meme coin disasters, making DYOR more valued",
    signal_type: "social",
    novelty: "medium",
    evidence:
      '"The vibe shifted hard after the $TRUMP and $LIBRA disasters btw. People are way more skeptical about meme coins now. Honestly that\'s healthy. DYOR means something again."',
    related_projects: [],
    tags: ["meme", "sentiment"],
    created_at: "2026-02-15T13:10:59.722716Z",
    content_url:
      "https://www.reddit.com/r/solana/comments/1r5dvdd/took_me_4_rugs_to_figure_out_where_to_buy_meme/",
    content_title:
      "Took me 4 rugs to figure out where to buy meme coins on Solana. Here's my whole setup now.",
    scraped_at: "2026-02-15T13:06:57.673481Z",
    data_source_id: 62,
    data_source_name: "Reddit r/solana",
    data_source_url: "https://www.reddit.com/r/solana.json?limit=50",
    data_source_type: "reddit",
    data_source_category: "community_forum",
  },
  {
    id: 334,
    scraped_content_id: 190,
    signal_title: "Raydium LaunchLab as Pump.fun competitor",
    description:
      "Raydium launched LaunchLab as a response to Pump.fun for new token launches",
    signal_type: "other",
    novelty: "high",
    evidence:
      '"They launched LaunchLab as their answer to Pump.fun which is worth watching."',
    related_projects: ["Raydium", "LaunchLab", "Pump.fun"],
    tags: ["launchpad", "meme", "dex"],
    created_at: "2026-02-15T13:10:59.722715Z",
    content_url:
      "https://www.reddit.com/r/solana/comments/1r5dvdd/took_me_4_rugs_to_figure_out_where_to_buy_meme/",
    content_title:
      "Took me 4 rugs to figure out where to buy meme coins on Solana. Here's my whole setup now.",
    scraped_at: "2026-02-15T13:06:57.673481Z",
    data_source_id: 62,
    data_source_name: "Reddit r/solana",
    data_source_url: "https://www.reddit.com/r/solana.json?limit=50",
    data_source_type: "reddit",
    data_source_category: "community_forum",
  },
  {
    id: 333,
    scraped_content_id: 190,
    signal_title: "Meteora gaining traction for meme coin trading",
    description:
      "User reports increased usage of Meteora for mid-cap meme coin positions, noting it sometimes flips Raydium on volume",
    signal_type: "social",
    novelty: "medium",
    evidence:
      '"Meteora. Dark horse. Some days it flips Raydium on volume. Been using it more for mid-cap meme coin positions lately."',
    related_projects: ["Meteora"],
    tags: ["meme", "dex", "trading"],
    created_at: "2026-02-15T13:10:59.722712Z",
    content_url:
      "https://www.reddit.com/r/solana/comments/1r5dvdd/took_me_4_rugs_to_figure_out_where_to_buy_meme/",
    content_title:
      "Took me 4 rugs to figure out where to buy meme coins on Solana. Here's my whole setup now.",
    scraped_at: "2026-02-15T13:06:57.673481Z",
    data_source_id: 62,
    data_source_name: "Reddit r/solana",
    data_source_url: "https://www.reddit.com/r/solana.json?limit=50",
    data_source_type: "reddit",
    data_source_category: "community_forum",
  },
  {
    id: 332,
    scraped_content_id: 191,
    signal_title: "Community-driven SOL rent reclaimer tool iteration",
    description:
      "Developer rebuilt SOL rent reclaimer tool based on Reddit feedback, improving UI, flow, claim process, and fee transparency to build trust.",
    signal_type: "developer",
    novelty: "medium",
    evidence:
      "'A few days ago I shared my SOL rent reclaimer all around reddit and got a ton of feedback... So I went back and rebuilt a lot of it.'",
    related_projects: [],
    tags: ["infrastructure", "tools", "rent-reclamation"],
    created_at: "2026-02-15T13:10:55.678974Z",
    content_url:
      "https://www.reddit.com/r/solana/comments/1r5ashb/took_your_feedback_seriously_would_love_your/",
    content_title:
      "Took your feedback seriously, would love your thoughts!",
    scraped_at: "2026-02-15T13:06:57.680099Z",
    data_source_id: 62,
    data_source_name: "Reddit r/solana",
    data_source_url: "https://www.reddit.com/r/solana.json?limit=50",
    data_source_type: "reddit",
    data_source_category: "community_forum",
  },
  {
    id: 331,
    scraped_content_id: 192,
    signal_title: "Openclaw Drainer Scam Targeting r/solana Users",
    description:
      "User reports persistent DMs promoting Openclaw, an automated chatbot monitor integrating with Trojan wallet, which drained SOL from a burner account",
    signal_type: "other",
    novelty: "high",
    evidence:
      "it got transferred to this wallet address straight away within seconds",
    related_projects: ["Openclaw", "Trojan"],
    tags: ["security", "scam", "drainer", "wallet"],
    created_at: "2026-02-15T13:10:53.126288Z",
    content_url:
      "https://www.reddit.com/r/solana/comments/1r5dupt/warning_someone_on_this_sub_keeps_dming_people/",
    content_title:
      "Warning: Someone on this sub keeps DM'ing people about Openclaw.",
    scraped_at: "2026-02-15T13:06:57.681231Z",
    data_source_id: 62,
    data_source_name: "Reddit r/solana",
    data_source_url: "https://www.reddit.com/r/solana.json?limit=50",
    data_source_type: "reddit",
    data_source_category: "community_forum",
  },
  {
    id: 330,
    scraped_content_id: 193,
    signal_title: "Solana validator economics debate intensifies",
    description:
      "Growing discussion around validator profitability and the sustainability of Solana's validator set as hardware costs increase",
    signal_type: "social",
    novelty: "medium",
    evidence:
      '"Running a validator is getting expensive. Between the hardware upgrades and the vote costs, smaller operators are getting squeezed out."',
    related_projects: [],
    tags: ["validators", "economics", "infrastructure"],
    created_at: "2026-02-15T12:45:30.000000Z",
    content_url:
      "https://www.reddit.com/r/solana/comments/example4/",
    content_title: "Validator economics thread",
    scraped_at: "2026-02-15T12:40:00.000000Z",
    data_source_id: 62,
    data_source_name: "Reddit r/solana",
    data_source_url: "https://www.reddit.com/r/solana.json?limit=50",
    data_source_type: "reddit",
    data_source_category: "community_forum",
  },
  {
    id: 329,
    scraped_content_id: 194,
    signal_title: "Jupiter Perps volume hits new weekly record",
    description:
      "Jupiter perpetual exchange sees record weekly trading volume as DeFi activity accelerates on Solana",
    signal_type: "other",
    novelty: "medium",
    evidence:
      '"Jupiter perps just did $3.2B in weekly volume. That\'s insane for a Solana-native perps platform."',
    related_projects: ["Jupiter"],
    tags: ["defi", "perps", "trading"],
    created_at: "2026-02-15T11:30:00.000000Z",
    content_url: "https://x.com/solana/status/example2",
    content_title: "Jupiter weekly stats",
    scraped_at: "2026-02-15T11:25:00.000000Z",
    data_source_id: 60,
    data_source_name: "@solana",
    data_source_url: "https://x.com/solana",
    data_source_type: "twitter",
    data_source_category: "official",
  },
  {
    id: 328,
    scraped_content_id: 195,
    signal_title: "Tensor integrates compressed NFT trading",
    description:
      "Tensor marketplace adds full support for compressed NFT collections, reducing listing and trading costs significantly",
    signal_type: "developer",
    novelty: "medium",
    evidence:
      '"Tensor now fully supports cNFTs. You can list, buy, and make offers on compressed collections just like regular NFTs."',
    related_projects: ["Tensor"],
    tags: ["nft", "marketplace", "compression"],
    created_at: "2026-02-15T10:15:00.000000Z",
    content_url:
      "https://www.reddit.com/r/solana/comments/example5/",
    content_title: "Tensor cNFT support",
    scraped_at: "2026-02-15T10:10:00.000000Z",
    data_source_id: 62,
    data_source_name: "Reddit r/solana",
    data_source_url: "https://www.reddit.com/r/solana.json?limit=50",
    data_source_type: "reddit",
    data_source_category: "community_forum",
  },
  {
    id: 327,
    scraped_content_id: 196,
    signal_title: "Wormhole bridge volume surge post-W token launch",
    description:
      "Wormhole cross-chain bridge sees increased Solana-bound volume following W token airdrop and multichain expansion",
    signal_type: "other",
    novelty: "low",
    evidence:
      '"Wormhole bridge volume to Solana is up 3x this month. A lot of ETH is flowing over."',
    related_projects: ["Wormhole"],
    tags: ["bridge", "cross-chain", "infrastructure"],
    created_at: "2026-02-15T09:00:00.000000Z",
    content_url: "https://solana.com/news",
    content_title: "Cross-chain flows update",
    scraped_at: "2026-02-15T08:55:00.000000Z",
    data_source_id: 61,
    data_source_name: "Solana News",
    data_source_url: "https://solana.com/news",
    data_source_type: "web",
    data_source_category: "official",
  },
  {
    id: 326,
    scraped_content_id: 197,
    signal_title: "Phantom wallet adds multi-chain swap feature",
    description:
      "Phantom wallet introduces cross-chain swap functionality allowing direct ETH-to-SOL swaps within the wallet interface",
    signal_type: "developer",
    novelty: "medium",
    evidence:
      '"Just swapped ETH to SOL directly in Phantom. No bridge UI needed. This is the UX that onboards normies."',
    related_projects: ["Phantom"],
    tags: ["wallet", "ux", "cross-chain"],
    created_at: "2026-02-14T22:00:00.000000Z",
    content_url:
      "https://www.reddit.com/r/solana/comments/example6/",
    content_title: "Phantom cross-chain swaps",
    scraped_at: "2026-02-14T21:55:00.000000Z",
    data_source_id: 62,
    data_source_name: "Reddit r/solana",
    data_source_url: "https://www.reddit.com/r/solana.json?limit=50",
    data_source_type: "reddit",
    data_source_category: "community_forum",
  },
]
