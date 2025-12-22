import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10, // 10 minutes (formerly cacheTime)
      refetchOnWindowFocus: false,
      retry: 3, // 3 attempts as per spec (plan.md operational parameters)
      retryDelay: (attemptIndex) => {
        // Exponential backoff: 500ms, 1s, 2s
        const delays = [500, 1000, 2000]
        return delays[attemptIndex] || 2000
      },
    },
  },
})
