# CI confidence policy

I would begin with an 80% confidence threshold and require every rubric criterion to pass. At that level, the judge is useful as a regression signal without pretending it is a source of truth. I would initially run it as non-blocking CI, collect a representative set of results, and compare its decisions with human review. After that calibration, I would gate only high-confidence failures (for example, ≥90% confidence) and keep borderline cases as warnings. This limits false negatives caused by model variance, ambiguous prompts, or legitimate stylistic choices.

When a human reviewer disagrees with the LLM judge, the human decision wins. I would retain the original script, prompt, model output, rubric result, model/version, and reviewer decision as a labeled example. Periodically reviewing those disagreements helps refine the rubric and prompts, identify biased criteria, and adjust the threshold. Repeated disagreement on one criterion means that criterion should not gate CI until it has been redesigned and revalidated.

