# Speed Reading Research — Links & Notes

Collected during development of the multi-line pacer mode.
For wiki / documentation use.

## Key Papers

### Perceptual Span & Eye Movements

- **Rayner, K. (1998). "Eye movements in reading and information processing: 20 years of research."**
  Psychological Bulletin, 124(3), 372-422.
  https://doi.org/10.1037/0033-2909.124.3.372
  — Foundational review. The perceptual span extends ~15 characters to the right and ~4 to the left of fixation. Almost entirely horizontal — vertical span is minimal.

- **McConkie, G.W. & Rayner, K. (1975). "The span of the effective stimulus during a fixation in reading."**
  Perception & Psychophysics, 17, 578-586.
  https://doi.org/10.3758/BF03203972
  — Original gaze-contingent display study establishing the asymmetric perceptual span.

### Speed Reading Claims vs. Science

- **Rayner, K., Schotter, E.R., Masson, M.E.J., Potter, M.C., & Treiman, R. (2016). "So Much to Read, So Little Time: How Do We Read, and Can Speed Reading Help?"**
  Psychological Science in the Public Interest, 17(1), 4-34.
  https://doi.org/10.1177/1529100615623267
  — Comprehensive review debunking many speed reading claims. Key finding: there is a speed-accuracy tradeoff; skimming is possible but comprehension drops. RSVP eliminates regressions but doesn't improve comprehension at high speeds.

- **Carver, R.P. (1990). "Reading Rate: A Review of Research and Theory."**
  Academic Press.
  — Defines reading rate "gears" from scanning (~600 WPM) to memorizing (~138 WPM). Normal reading for comprehension: ~250-300 WPM.

### Parafoveal Processing

- **Schotter, E.R., Angele, B., & Rayner, K. (2012). "Parafoveal processing in reading."**
  Attention, Perception, & Psychophysics, 74, 5-35.
  https://doi.org/10.3758/s13414-011-0219-2
  — Parafoveal preview benefit is real but limited: word length, first letters, and some orthographic info. Full word recognition requires foveal fixation.

### Chunking & Phrase Reading

- **Buzan, T. (2006). "Speed Reading."** BBC Active.
  — Popular speed reading guide advocating multi-word fixation, reduced subvocalization, and peripheral vision training. Source of many multi-line and Z-pattern techniques.

- **Castelhano, M.S. & Muter, P. (2001). "Optimizing the reading of electronic text using rapid serial visual presentation."**
  Behaviour & Information Technology, 20(4), 237-247.
  https://doi.org/10.1080/01449290110069464
  — RSVP studies showing optimal presentation rates and the effect of chunk size on comprehension.

## Relevant Concepts

### Why Multi-Line "Works" (Subjectively)

The experience of reading multiple lines at once in a narrow book is real but isn't true parallel line processing. What happens:

1. **Narrow columns** (4-6 words/line) fit within the horizontal perceptual span (~15 chars)
2. **Rapid vertical saccades** between lines take only 20-30ms
3. **Predictive processing** fills gaps using context and syntax
4. **Gist extraction** from parafoveal preview of adjacent lines

This creates the subjective experience of "seeing 5 lines at once" while actually performing very fast sequential scanning. This is a trainable skill — the multi-line pacer mode trains exactly this.

### Why Z-Pattern Was Removed

Z-pattern (zigzag across line groups) is a structured skimming technique from speed reading books (Buzan, etc.). Problems:

1. No scientific support for improved reading via diagonal saccades
2. Diagonal eye movements are slower than horizontal ones
3. Difficult to highlight meaningfully — the highlight doesn't correspond to readable text chunks
4. Better suited as a manual skimming strategy than a paced exercise

May revisit in a future version with a different approach (e.g., guided fixation points rather than sweep highlighting).

### WPM in Multi-Line Mode

The pacer's multi-line WPM represents the **visual sweep speed** across the first line of each group. The reader processes all lines in the group during the sweep. At 300 WPM multi-line with 3 lines, the effective reading rate is higher than 300 WPM — the WPM setting controls the pace of the visual guide, not the total throughput.

## Further Reading

- **Dehaene, S. (2009). "Reading in the Brain."** Viking.
  — How the visual system processes written language. Explains foveal vs. parafoveal processing.

- **Legge, G.E. (2007). "Psychophysics of Reading in Normal and Low Vision."**
  Lawrence Erlbaum Associates.
  — Visual factors in reading: font size, contrast, visual span.

- **Inhoff, A.W. & Rayner, K. (1986). "Parafoveal word processing during eye fixations in reading."**
  Perception & Psychophysics, 40, 431-439.
  https://doi.org/10.3758/BF03208203
  — Early evidence for parafoveal preview benefit.
