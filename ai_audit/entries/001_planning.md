# Entry 001 — Planning

- **Date/time:** 2026-11-16 12:00 ICT (UTC+7)
- **Tool/model:** OpenCode / DeepSeek V4.1 Flash Free (`opencode/deepseek-v4.1-flash-free`)
- **Task:** Read the HW05 PDF, analyse requirements, produce an implementation plan, and ask clarification questions instead of inventing facts.

## Prompt (verbatim)

> Tôi cần làm bài tập về performance testing. Do đó bạn hãy đọc yêu cầu trong file .pdf ở thư mục hw5. Phân tích và viết kế hoạch thực hiện yêu cầu. Hãy hỏi lại tôi nếu như có điều cần giải thích, ko tự bịa ra. Yêu cầu kế hoạch phải đảm bảo thõa mản yêu cầu đề bài.

## AI output

The AI produced:

1. A 9-page extraction/summary of the HW05 requirements (Load/Stress/Spike, CSV, report views, endurance, video, issues, Task 2/3, Agent Skill, AI Audit, AI Critique, Git log, submission rules).
2. Source-level SUT verification (official port 3000, seed counts, lockout +2/180 s, checkout behaviour, in-memory cart, no pagination).
3. `PLAN.md` — detailed implementation plan with workflow, CSV schema, 3 scenario designs, report-view mapping, lockout probe, endurance definition, Task 2/3, Agent Skill, AI audit, Git/submission plan, risk register, traceability matrix, and open questions.
4. Clarification questions — the AI did **not** invent group membership, repo URL, hardware hostname, video availability, or AI tool declaration.

**Full output artifact:** `PLAN.md` (root of repo).  
**No performance metrics or test results were generated in this entry.**

## Human review

- Student answered the clarification questions in the next message.
- Student confirmed: repo URL, hardware hostname, seed dataset approval, no second machine.
- Student deferred the video decision; AI must not claim a video exists until it is recorded/uploaded.
- Student's answer “1. ko.” is interpreted as “workflow does not duplicate another member”; member list still needs to be recorded in `docs/group_scope.md` before the final report claims non-duplication.
