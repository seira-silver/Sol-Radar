"use client"

import { useEffect, useRef, useCallback } from "react"

export function useInfiniteScroll(onLoadMore: () => void, hasMore: boolean) {
  const observerRef = useRef<IntersectionObserver | null>(null)
  const sentinelRef = useRef<HTMLDivElement | null>(null)

  const setSentinelRef = useCallback(
    (node: HTMLDivElement | null) => {
      if (observerRef.current) {
        observerRef.current.disconnect()
      }

      if (node && hasMore) {
        observerRef.current = new IntersectionObserver(
          (entries) => {
            if (entries[0]?.isIntersecting) {
              onLoadMore()
            }
          },
          { threshold: 0.1, rootMargin: "200px" }
        )
        observerRef.current.observe(node)
      }

      sentinelRef.current = node
    },
    [onLoadMore, hasMore]
  )

  useEffect(() => {
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect()
      }
    }
  }, [])

  return { sentinelRef: setSentinelRef }
}
