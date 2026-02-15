import type {
  Evidence,
  LandingResponse,
  Narrative,
  NarrativeListResponse,
  Signal,
  SignalListResponse,
} from "@/lib/api-types"
import { apiGet } from "@/lib/http"

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null
}

function normalizeStringArray(v: unknown): string[] {
  if (!Array.isArray(v)) return []
  return v.map((x) => (typeof x === "string" ? x : String(x))).filter(Boolean)
}

function normalizeEvidenceItem(v: unknown): Evidence | null {
  if (!isRecord(v)) return null
  const evidence = typeof v.evidence === "string" ? v.evidence : null
  const signal_id =
    typeof v.signal_id === "number"
      ? v.signal_id
      : typeof v.signal_id === "string" && v.signal_id.trim()
        ? Number(v.signal_id)
        : NaN
  const content_url = typeof v.content_url === "string" ? v.content_url : ""
  const source_name = typeof v.source_name === "string" ? v.source_name : ""
  const signal_title = typeof v.signal_title === "string" ? v.signal_title : ""
  if (!evidence || !Number.isFinite(signal_id)) return null
  return { evidence, signal_id, content_url, source_name, signal_title }
}

function normalizeNarrative(n: Narrative, fallbackRank?: number): Narrative & { ideas: NonNullable<Narrative["ideas"]> } {
  const keyEvidenceRaw = (n as unknown as { key_evidence?: unknown }).key_evidence
  const key_evidence = Array.isArray(keyEvidenceRaw)
    ? keyEvidenceRaw.map(normalizeEvidenceItem).filter(Boolean) as Evidence[]
    : []

  const tags = normalizeStringArray((n as unknown as { tags?: unknown }).tags)
  const supporting_source_names = normalizeStringArray(
    (n as unknown as { supporting_source_names?: unknown }).supporting_source_names
  )

  const ideasRaw = (n as unknown as { ideas?: unknown }).ideas
  const ideas = Array.isArray(ideasRaw) ? (ideasRaw as any[]).map((i) => i) : []

  return {
    ...n,
    rank: n.rank ?? fallbackRank ?? null,
    tags,
    supporting_source_names,
    key_evidence,
    idea_count:
      typeof n.idea_count === "number"
        ? n.idea_count
        : Array.isArray(ideas)
          ? ideas.length
          : 0,
    ideas,
  }
}

function normalizeSignal(s: Signal): Signal {
  return {
    ...s,
    tags: normalizeStringArray((s as unknown as { tags?: unknown }).tags),
    related_projects: normalizeStringArray(
      (s as unknown as { related_projects?: unknown }).related_projects
    ),
  }
}

export async function getLanding(params: {
  narratives_limit: number
  narratives_offset: number
  signal?: AbortSignal
}): Promise<LandingResponse> {
  const data = await apiGet<LandingResponse>("/landing", {
    query: {
      narratives_limit: params.narratives_limit,
      narratives_offset: params.narratives_offset,
    },
    signal: params.signal,
  })

  return {
    ...data,
    narratives: {
      ...data.narratives,
      narratives: data.narratives.narratives.map((n, i) =>
        normalizeNarrative(n, data.narratives.offset + i + 1)
      ),
    },
  }
}

export async function listSignals(params: {
  limit: number
  offset: number
  signal?: AbortSignal
}): Promise<SignalListResponse> {
  const data = await apiGet<SignalListResponse>("/signals", {
    query: { limit: params.limit, offset: params.offset },
    signal: params.signal,
  })
  return {
    ...data,
    signals: data.signals.map(normalizeSignal),
  }
}

export async function listHackathonNarratives(params: {
  limit: number
  offset: number
  signal?: AbortSignal
}): Promise<NarrativeListResponse> {
  const data = await apiGet<NarrativeListResponse>("/narratives/hackathons", {
    query: { limit: params.limit, offset: params.offset },
    signal: params.signal,
  })
  return {
    ...data,
    narratives: data.narratives.map((n, i) =>
      normalizeNarrative(n, data.offset + i + 1)
    ),
  }
}

export async function getNarrativeDetail(params: {
  id: number
  signal?: AbortSignal
}): Promise<Narrative> {
  const data = await apiGet<Narrative>(`/narratives/${params.id}`, {
    signal: params.signal,
  })
  return normalizeNarrative(data)
}

