# Experiments log

Retrieval is evaluated on `eval/retrieval_questions.csv` (24 answerable questions) with
evidence phrases: **hit@k** = a chunk containing the phrase is in the top k (chunk level),
**doc_hit@k** = a chunk from an expected document is in the top k (document level).
With 24 questions, one question ≈ 4 percentage points.

## Retrieval

| Date | Variant | hit@5 | hit@10 | hit@15 | hit@20 | doc_hit@5 | Latency (s/query) | Notes |
|---|---|---|---|---|---|---|---|---|
| 2026-11-07 | Word overlap (reference) | 0.500 | | | | 0.917 | — | naive shared-word count |
| 2026-11-07 | e5-base, 1000/200 chunks | 0.625 | 0.750 | 0.833 | 0.917 | 0.958 | fast | baseline |
| 2026-11-07 | e5 top 30 + bge-reranker-v2-m3 (fp16) | 0.833 | | | | 1.000 | ~3.9 GPU (GTX 1650 Ti); CPU far too slow | 6 fixed, 1 broken (TAX-04) |

### e5 vs reranker, per question (k = 5)

- **Fixed (6):** BKG-01 (11→1), REG-02 (28→3), REG-06 (7→4), RES-03 (19→2), RES-04 (6→1), TAX-02 (7→2)
- **Broken (1):** TAX-04 (2→11)
- **Both miss (3):** BKG-04 (41, never reaches the 30 candidates), REG-01 (18→13), REG-04 (12→16)
- **Fragile:** BKG-02 (1→5)

### Decision (2026-11-07)

The reranker costs ~4 s/query on a laptop GPU and about a minute on a 2-vCPU Hugging Face
Space. e5 top-15 reaches the same hit rate as reranker top-5 (0.833) at no extra cost.
**Deployed app: e5, TOP_K = 15 chunks to the LLM.** Answer correctness (Milestone 3) will
show whether the LLM handles 15 chunks well.

## Open items

- Label audit: are the evidence phrases of REG-01, REG-04, TAX-04 too narrow? Decide by
  reading the retrieved chunks; if labels change, re-run **all** variants.
- Corpus contains superseded rules (ΤΑΚΚ amounts in the 2024 guide; deadline in ΠΟΛ 1187/2017).

## Generation (manual checks, Claude Haiku 5.5, effort "low", TOP_K = 15)

Single runs: the API no longer accepts `temperature`, so answers vary between runs.

### Small-to-big context (2026-11-08)

TAX-03 («Πόσο είναι το τέλος ανθεκτικότητας ... ανά διανυκτέρευση και εποχή;»). The winter
amount for short-term rentals is in `fek_A1202_2024.pdf_p2_c3`, whose heading
("Νοέμβριο έως Μάρτιο") is in `p2_c2`; `p2_c3` alone is not retrieved.

| Context | Excerpts | Input tokens | p2_c3 seen | Answer |
|---|---|---|---|---|
| 15 separate chunks (before merging) | 15 | 10,632 | no | summer 8 € / 15 € correct; winter "not in the documents" |
| merged, no expansion (`expand_top=0`) | 7 | 8,757 | no | same: winter "not in the documents" (honest, no invented amount) |
| merged + neighbours of top 5 | 6 | 9,051 | yes | **all correct**: 8 € / 15 € (Apr–Oct), 2 € / 4 € (Nov–Mar) |

- Merging consecutive chunks removes the duplicated overlap: −18% input tokens.
- Neighbour expansion adds ~300 tokens here and fixes the answer.

### Other checks (with expansion)

- BKG-01: correct (20th of the following month, from departure; example 20.12.2024). The
  unrelated 28 February sentence disappeared after rule 10.
- UNA-02 (Italy): fixed refusal sentence, 38 output tokens.
- UNA-03 (is it worth it?): explicitly gives no advice, states the relevant rules with
  citations, says the documents don't compare the two options → counts as correct
  (partial answer without advice).
