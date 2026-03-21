import { useState, useRef, useCallback } from "react"

export interface EnrichedLead {
  lead_hash:         string
  name:              string
  address:           string
  city:              string
  phone:             string
  email:             string
  website:           string
  source:            string
  score:             number
  priority:          "high" | "medium" | "low"
  suggested_opening: string
  reason:            string
  business_type:     string
}

type StreamStatus =
  | "idle" | "discovering" | "enriching" | "scoring"
  | "streaming" | "completed" | "error"

export function useLeadStream() {
  const [leads, setLeads]             = useState<EnrichedLead[]>([])
  const [status, setStatus]           = useState<StreamStatus>("idle")
  const [statusMessage, setStatusMsg] = useState("")
  const [sessionId, setSessionId]     = useState("")
  const [totalReceived, setTotal]     = useState(0)
  const [error, setError]             = useState<string | null>(null)
  const abortRef                      = useRef<AbortController | null>(null)

  const startHunt = useCallback(async (params: {
    businessType:  string
    location:      string
    radiusKm:      number
    targetService: string
    apiKey:        string
  }) => {
    setLeads([])
    setError(null)
    setTotal(0)
    setSessionId("")
    setStatus("discovering")
    setStatusMsg("Connecting to LeadOS pipeline...")

    abortRef.current?.abort()
    abortRef.current = new AbortController()

    const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

    try {
      const res = await fetch(`${apiBase}/api/leads/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": params.apiKey,
        },
        body: JSON.stringify({
          business_type:  params.businessType,
          location:       params.location,
          radius_km:      params.radiusKm,
          target_service: params.targetService,
          max_leads:      80,
          batch_size:     20,
        }),
        signal: abortRef.current.signal,
      })

      if (!res.ok || !res.body)
        throw new Error(`HTTP ${res.status}`)

      const reader  = res.body.getReader()
      const decoder = new TextDecoder()
      let   buffer  = ""

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n\n")
        buffer = lines.pop() ?? ""

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue
          try {
            const event = JSON.parse(line.slice(6))
            if (event.status === "discovering" || event.status === "enriching") {
              setStatus(event.status)
              setStatusMsg(event.message)
            }
            if (event.status === "batch") {
              setStatus("streaming")
              setSessionId(event.session_id)
              setTotal(event.total_so_far)
              setLeads(prev => [...prev, ...event.batch])
              setStatusMsg(`${event.total_so_far}/80 enriched leads received...`)
            }
            if (event.status === "completed" || event.status === "done") {
              setStatus("completed")
              setTotal(event.total)
              setStatusMsg(`✅ ${event.total} enriched leads ready`)
            }
            if (event.status === "error") {
              setStatus("error")
              setError(event.detail)
            }
          } catch { /* skip malformed */ }
        }
      }
    } catch (err: any) {
      if (err.name !== "AbortError") {
        setStatus("error")
        setError(err.message ?? "Connection failed")
      }
    }
  }, [])

  const stopHunt = useCallback(() => {
    abortRef.current?.abort()
    setStatus("idle")
  }, [])

  const reset = useCallback(() => {
    stopHunt()
    setLeads([])
    setTotal(0)
    setError(null)
    setStatusMsg("")
    setSessionId("")
  }, [stopHunt])

  return {
    leads, status, statusMessage,
    sessionId, totalReceived,
    error, startHunt, stopHunt, reset,
  }
}
