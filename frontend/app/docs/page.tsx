'use client'

import { API_URL } from '@/lib/constants'
import {
  ArrowLeft,
  BookOpen,
  Bot,
  Code2,
  Database,
  ExternalLink,
  Github,
  Globe,
} from 'lucide-react'
import Link from 'next/link'

const baseUrl = (API_URL || 'http://localhost:8000/api/v1').replace(/\/+$/, '')

export default function DocsPage() {
  return (
    <div className='min-h-screen bg-background'>
      {/* Header */}
      <header className='sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl'>
        <div className='mx-auto flex h-16 max-w-4xl items-center justify-between px-4 sm:px-6'>
          <Link
            href='/'
            className='flex items-center gap-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground'
          >
            <ArrowLeft className='h-4 w-4' />
            Back to Sol Radar
          </Link>
          <div className='flex items-center gap-2 text-foreground'>
            <BookOpen className='h-5 w-5' />
            <span className='font-semibold'>Documentation</span>
          </div>
        </div>
      </header>

      <main className='mx-auto max-w-4xl px-4 py-10 pb-24 sm:px-6'>
        <div className='prose prose-invert prose-sm max-w-none space-y-12'>
          {/* Project description */}
          <section>
            <h2 className='mb-3 flex items-center gap-2 text-lg font-bold text-foreground'>
              <Globe className='h-5 w-5 text-primary' />
              Project Description
            </h2>
            <p className='text-muted-foreground leading-relaxed'>
              <strong className='text-foreground'>Sol Radar</strong> is an
              automated intelligence tool that continuously scrapes, analyzes,
              and synthesizes data from across the Solana ecosystem — news
              outlets, research platforms, community forums, and key opinion
              leaders on X (Twitter) — to surface emerging narratives, rank them
              by momentum, and generate actionable product ideas for builders.
            </p>
            <p className='mt-2 text-muted-foreground leading-relaxed'>
              The pipeline runs in three stages:{' '}
              <strong className='text-foreground'>Scrape</strong> (collect from
              12+ web sources and verified Solana KOLs),{' '}
              <strong className='text-foreground'>Extract</strong> (LLM analyzes
              content into structured signals), and{' '}
              <strong className='text-foreground'>Synthesize</strong> (LLM
              aggregates signals into narratives with product ideas). All
              narratives are scored by a velocity algorithm and ranked by
              momentum.
            </p>
            <p className='mt-2 flex flex-wrap items-center gap-3 text-sm text-muted-foreground'>
              <a
                href='https://sol-radar.vercel.app/'
                target='_blank'
                rel='noopener noreferrer'
                className='inline-flex items-center gap-1.5 text-primary hover:underline'
              >
                <Globe className='h-4 w-4' />
                Live Website
              </a>
              <a
                href='https://github.com/seira-silver/Sol-Radar'
                target='_blank'
                rel='noopener noreferrer'
                className='inline-flex items-center gap-1.5 text-primary hover:underline'
              >
                <Github className='h-4 w-4' />
                GitHub
              </a>
            </p>
          </section>

          {/* Data sources */}
          <section>
            <h2 className='mb-4 flex items-center gap-2 text-lg font-bold text-foreground'>
              <Database className='h-5 w-5 text-primary' />
              Data Sources
            </h2>
            <div className='space-y-4'>
              <div>
                <h3 className='mb-2 text-sm font-semibold text-foreground'>
                  Ecosystem & News
                </h3>
                <div className='overflow-x-auto rounded-lg border border-border/50 bg-secondary/30'>
                  <table className='w-full text-left text-xs'>
                    <thead>
                      <tr className='border-b border-border/50'>
                        <th className='px-3 py-2 font-medium text-foreground'>
                          Source
                        </th>
                        <th className='px-3 py-2 font-medium text-foreground'>
                          URL
                        </th>
                        <th className='px-3 py-2 font-medium text-foreground'>
                          Priority
                        </th>
                      </tr>
                    </thead>
                    <tbody className='text-muted-foreground'>
                      <tr className='border-b border-border/30'>
                        <td className='px-3 py-2'>Solana News</td>
                        <td className='px-3 py-2'>solana.com/news</td>
                        <td className='px-3 py-2'>High</td>
                      </tr>
                      <tr className='border-b border-border/30'>
                        <td className='px-3 py-2'>Helius Blog</td>
                        <td className='px-3 py-2'>helius.dev/blog</td>
                        <td className='px-3 py-2'>High</td>
                      </tr>
                      <tr className='border-b border-border/30'>
                        <td className='px-3 py-2'>Solana Mobile Blog</td>
                        <td className='px-3 py-2'>blog.solanamobile.com</td>
                        <td className='px-3 py-2'>High</td>
                      </tr>
                      <tr className='border-b border-border/30'>
                        <td className='px-3 py-2'>Solana Homepage</td>
                        <td className='px-3 py-2'>solana.com</td>
                        <td className='px-3 py-2'>Medium</td>
                      </tr>
                      <tr>
                        <td className='px-3 py-2'>Solana Compass</td>
                        <td className='px-3 py-2'>solanacompass.com</td>
                        <td className='px-3 py-2'>Medium</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div>
                <h3 className='mb-2 text-sm font-semibold text-foreground'>
                  Research & Reports
                </h3>
                <div className='overflow-x-auto rounded-lg border border-border/50 bg-secondary/30'>
                  <table className='w-full text-left text-xs'>
                    <thead>
                      <tr className='border-b border-border/50'>
                        <th className='px-3 py-2 font-medium text-foreground'>
                          Source
                        </th>
                        <th className='px-3 py-2 font-medium text-foreground'>
                          URL
                        </th>
                      </tr>
                    </thead>
                    <tbody className='text-muted-foreground'>
                      <tr className='border-b border-border/30'>
                        <td className='px-3 py-2'>Messari</td>
                        <td className='px-3 py-2'>messari.io</td>
                      </tr>
                      <tr className='border-b border-border/30'>
                        <td className='px-3 py-2'>Arkham Research</td>
                        <td className='px-3 py-2'>info.arkm.com/research</td>
                      </tr>
                      <tr>
                        <td className='px-3 py-2'>
                          Electric Capital, CoinGecko
                        </td>
                        <td className='px-3 py-2'>Web / PDF</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div>
                <h3 className='mb-2 text-sm font-semibold text-foreground'>
                  Community & Social
                </h3>
                <p className='text-muted-foreground text-sm'>
                  Reddit r/solana, Reddit Solana Search (JSON feeds). X/Twitter
                  via ScrapeBadger API from{' '}
                  <strong className='text-foreground'>
                    59 verified Solana KOLs
                  </strong>{' '}
                  including @solana, @toly, @heliuslabs, @phantom, @MagicEden,
                  @DriftProtocol, @marginfi, @PythNetwork, and more. Full list
                  in{' '}
                  <code className='rounded bg-secondary/50 px-1.5 py-0.5 text-foreground'>
                    data/verified_solana_kols.json
                  </code>
                  .
                </p>
              </div>
            </div>
          </section>

          {/* API Base URL & Endpoints */}
          <section>
            <h2 className='mb-4 flex items-center gap-2 text-lg font-bold text-foreground'>
              <Code2 className='h-5 w-5 text-primary' />
              API Base URL & Endpoints
            </h2>
            <div className='rounded-lg border border-border/50 bg-secondary/30 p-3 font-mono text-sm text-foreground'>
              {baseUrl}
            </div>
            <p className='mt-2 text-xs text-muted-foreground'>
              Configured via{' '}
              <code className='rounded bg-secondary/50 px-1 py-0.5'>
                NEXT_PUBLIC_API_URL
              </code>{' '}
              in the frontend.
            </p>
            <div className='mt-4 overflow-x-auto rounded-lg border border-border/50 bg-secondary/30'>
              <table className='w-full text-left text-xs'>
                <thead>
                  <tr className='border-b border-border/50'>
                    <th className='px-3 py-2 font-medium text-foreground'>
                      Method
                    </th>
                    <th className='px-3 py-2 font-medium text-foreground'>
                      Endpoint
                    </th>
                    <th className='px-3 py-2 font-medium text-foreground'>
                      Description
                    </th>
                  </tr>
                </thead>
                <tbody className='text-muted-foreground'>
                  <tr className='border-b border-border/30'>
                    <td className='px-3 py-2 font-mono'>GET</td>
                    <td className='px-3 py-2 font-mono'>/landing</td>
                    <td className='px-3 py-2'>
                      Bundled stats + narratives with nested ideas
                    </td>
                  </tr>
                  <tr className='border-b border-border/30'>
                    <td className='px-3 py-2 font-mono'>GET</td>
                    <td className='px-3 py-2 font-mono'>/signals</td>
                    <td className='px-3 py-2'>
                      List signals (type, novelty, source, tags, date range)
                    </td>
                  </tr>
                  <tr className='border-b border-border/30'>
                    <td className='px-3 py-2 font-mono'>GET</td>
                    <td className='px-3 py-2 font-mono'>
                      /signals/&#123;id&#125;
                    </td>
                    <td className='px-3 py-2'>
                      Single signal with source metadata
                    </td>
                  </tr>
                  <tr className='border-b border-border/30'>
                    <td className='px-3 py-2 font-mono'>GET</td>
                    <td className='px-3 py-2 font-mono'>/narratives</td>
                    <td className='px-3 py-2'>
                      List narratives sorted by velocity score
                    </td>
                  </tr>
                  <tr className='border-b border-border/30'>
                    <td className='px-3 py-2 font-mono'>GET</td>
                    <td className='px-3 py-2 font-mono'>
                      /narratives/hackathons
                    </td>
                    <td className='px-3 py-2'>Hackathon-tagged narratives</td>
                  </tr>
                  <tr className='border-b border-border/30'>
                    <td className='px-3 py-2 font-mono'>GET</td>
                    <td className='px-3 py-2 font-mono'>
                      /narratives/&#123;id&#125;
                    </td>
                    <td className='px-3 py-2'>
                      Narrative detail with ideas and supporting signals
                    </td>
                  </tr>
                  <tr className='border-b border-border/30'>
                    <td className='px-3 py-2 font-mono'>GET</td>
                    <td className='px-3 py-2 font-mono'>/ideas</td>
                    <td className='px-3 py-2'>List product ideas</td>
                  </tr>
                  <tr className='border-b border-border/30'>
                    <td className='px-3 py-2 font-mono'>GET</td>
                    <td className='px-3 py-2 font-mono'>/hackathons</td>
                    <td className='px-3 py-2'>
                      Ideas from high-velocity or hackathon narratives
                    </td>
                  </tr>
                  <tr className='border-b border-border/30'>
                    <td className='px-3 py-2 font-mono'>GET</td>
                    <td className='px-3 py-2 font-mono'>/stats</td>
                    <td className='px-3 py-2'>Dashboard statistics</td>
                  </tr>
                  <tr>
                    <td className='px-3 py-2 font-mono'>POST</td>
                    <td className='px-3 py-2 font-mono'>/chat</td>
                    <td className='px-3 py-2'>
                      Chat with Seira — SSE streaming response
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p className='mt-2 text-xs text-muted-foreground'>
              List endpoints support{' '}
              <code className='rounded bg-secondary/50 px-1 py-0.5'>limit</code>{' '}
              and{' '}
              <code className='rounded bg-secondary/50 px-1 py-0.5'>
                offset
              </code>{' '}
              for pagination.
            </p>
          </section>

          {/* Agent-to-agent */}
          <section>
            <h2 className='mb-4 flex items-center gap-2 text-lg font-bold text-foreground'>
              <Bot className='h-5 w-5 text-primary' />
              Agent-to-Agent Integration
            </h2>
            <p className='text-muted-foreground text-sm leading-relaxed'>
              External AI agents can interact with Sol Radar via the REST API
              and the Seira chat endpoint. A machine-readable capability spec is
              published at SKILL.md with all available endpoints,
              request/response schemas, and the SSE streaming chat protocol.
            </p>
            <ul className='mt-3 space-y-1 text-sm text-muted-foreground'>
              <li>
                • Fetch narratives & signals:{' '}
                <code className='rounded bg-secondary/50 px-1 py-0.5'>
                  GET /narratives
                </code>
                ,{' '}
                <code className='rounded bg-secondary/50 px-1 py-0.5'>
                  GET /signals
                </code>
              </li>
              <li>
                • Validate product ideas via Seira:{' '}
                <code className='rounded bg-secondary/50 px-1 py-0.5'>
                  POST /chat
                </code>
              </li>
              <li>
                • Monitor ecosystem health:{' '}
                <code className='rounded bg-secondary/50 px-1 py-0.5'>
                  GET /stats
                </code>
              </li>
              <li>
                • Analyze external URLs:{' '}
                <code className='rounded bg-secondary/50 px-1 py-0.5'>
                  POST /chat
                </code>{' '}
                with{' '}
                <code className='rounded bg-secondary/50 px-1 py-0.5'>url</code>{' '}
                field
              </li>
            </ul>
            <a
              href='/SKILL.md'
              target='_blank'
              rel='noopener noreferrer'
              className='mt-4 inline-flex items-center gap-2 rounded-lg border border-primary/30 bg-primary/5 px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-primary/10'
            >
              View full SKILL.md (Agent spec)
              <ExternalLink className='h-4 w-4' />
            </a>
          </section>
        </div>
      </main>
    </div>
  )
}
