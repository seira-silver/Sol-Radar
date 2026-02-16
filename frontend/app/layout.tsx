import type { Metadata, Viewport } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'

import { SeiraChatButton } from '@/components/seira-chat-button'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-jetbrains' })

export const metadata: Metadata = {
  title: 'Sol Radar - Solana Narrative Detection',
  description: 'Detect emerging narratives and early signals within the Solana ecosystem. Analyze onchain and offchain data to surface trends early.',
}

export const viewport: Viewport = {
  themeColor: '#0d1117',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="font-sans antialiased min-h-screen">
        {children}
        <SeiraChatButton />
      </body>
    </html>
  )
}
