# Robot Learning Atlas maintenance

- Use autodev for implementation and recover status from docs/roadmap.md and docs/validation.md before starting another slice.
- Use [GitHub Project #3](https://github.com/users/huangkiki/projects/3) and its linked issues for the queue, dependencies and acceptance. Synchronize actual status at start, blockage and delivery, and verify remote readback.
- This repository owns framework learning materials. Preserve mjlab, Isaac Lab and UniLab native names and behavior. Do not add a shared runtime wrapper or install heavyweight simulators for documentation checks.
- Work with one writer by default. Delegate only when the user or another applicable instruction explicitly requests it.
- Keep Chinese and English entry/status consistent. Detailed lessons are currently Chinese; do not imply full bilingual coverage.
- Every implementation claim needs a pinned upstream source link. docs/sources.json records repository, full commit, reviewed file hashes and line counts. Update affected explanations when changing a source pin.
- Each lesson includes prerequisites, goals, native fields, a call path, assumptions/units, pitfalls, exercises with answers, and evidence boundaries.
- Keep source inspection, course-script execution, native simulation, training quality, evaluation and real-robot validation separate. A static example is not a trained policy.
- Do not infer a shared terminal-observation contract, identical reset order, numerical equivalence or backend capability from similar class names.
- Keep the README as the homepage. Do not create a website framework, benchmark platform, scheduler, issue taxonomy or new infrastructure without a current need.
- Run python3 scripts/check_docs.py, python3 -m compileall -q scripts mjlab/examples learning/examples, python3 learning/examples/rollout_math.py and git diff --check. For source changes run scripts/verify_sources.py with all pinned checkouts and the affected course example.
- Preserve user's unrelated changes. No credentials, addresses, machine-specific paths, cached environments, models or training artifacts in commits.
- Local development, GitHub visibility/publication, merge/release and scheduling are distinct scopes. Follow the user's existing authorization, including Obsidian course archival and synchronization.
