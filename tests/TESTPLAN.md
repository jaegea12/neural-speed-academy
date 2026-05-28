# Neural Speed Academy v1.0.0 — Test Plan

**Tester:** _______________  **Date:** _______________  **Platform:** _______________

**Python version:** _______________  **PyQt6 version:** _______________

**Screen resolution:** _______________  **Display server (Linux):** X11 / Wayland

---

## How to Use This Plan

1. Work through each phase in order — Phase 1 failures block everything else.
2. Check the box when a test passes. Add notes for any failures.
3. If a test fails, note the exact steps to reproduce and any error output.
4. Priority levels: **P0** = crash/data loss, **P1** = broken feature, **P2** = visual/UX.

---

## Phase 1: Startup & Core Navigation (P0)

These must all pass before proceeding.

- [ ] **1.1 Cold start** — Run `python nsa.py`. App window appears without errors in the terminal.
- [ ] **1.2 Login** — Create a new user profile. Name appears in the nav bar.
- [ ] **1.3 Restart persistence** — Close and reopen the app. The user profile is still there.
- [ ] **1.4 Main menu title** — Title reads "NEURAL SPEED ACADEMY" (no `\n` or broken characters).
- [ ] **1.5 Menu navigation** — From the main menu, visit every screen. No crashes.
  - [ ] Training Hub (dashboard)
  - [ ] Each exercise menu (15 total)
  - [ ] Training Paths
  - [ ] My Custom Paths
  - [ ] Stats
  - [ ] Settings
- [ ] **1.6 Back button** — Press Back on every screen. Returns to the previous screen.
  - [ ] Known issue to verify: Back button on Training Paths screens (Linux).
- [ ] **1.7 Keyboard shortcut** — Ctrl+Enter starts exercises from their config screens.

**Phase 1 result:** PASS / FAIL  **Notes:** _______________

---

## Phase 2: Settings & Persistence (P0–P1)

- [ ] **2.1 Color profile switch** — Change to each of the 11 profiles. UI updates immediately.
  - [ ] Dark
  - [ ] Light
  - [ ] High Contrast
  - [ ] Warm/Focus
  - [ ] Twilight
  - [ ] Soft Light
  - [ ] Silver
  - [ ] Monochrome
  - [ ] Ember
  - [ ] Dark Blue
  - [ ] Solarized
- [ ] **2.2 Profile persists** — Change profile, restart app. Same profile loads.
- [ ] **2.3 Locale switching** — Switch to each language. All labels render (no `[missing key]` text).
  - [ ] English
  - [ ] Deutsch
  - [ ] Français
  - [ ] Español
  - [ ] Italiano
  - [ ] Português
- [ ] **2.4 Text library** — Add a custom text in Settings. Save. Restart. Custom text still there.
- [ ] **2.5 Unsaved changes** — Edit text in Settings, navigate away. Confirmation dialog appears.
  - [ ] "Save" saves changes and navigates.
  - [ ] "Discard" discards text changes but does NOT revert color profile.
  - [ ] "Cancel" stays on Settings.
- [ ] **2.6 Exercise config persistence** — Open Schulte menu, change grid size to 6×6. Navigate away. Come back. Grid size is still 6×6.
- [ ] **2.7 Font rendering** — Text uses Inter (UI), JetBrains Mono (monospace), Source Serif 4 (serif). No fallback to system fonts.

**Phase 2 result:** PASS / FAIL  **Notes:** _______________

---

## Phase 3: Exercises — Smoke Test (P0–P1)

Run each exercise once with default settings. Verify it starts, runs without errors, and shows a results screen.

### Perception

- [ ] **3.1 Eye Priming** — Launches. Dot moves. Completes after ~45s.
  - Test each mode (select from presets):
  - [ ] Horizontal Saccades
  - [ ] Vertical Saccades
  - [ ] Diagonal Saccades
  - [ ] Expanding Saccades
  - [ ] Random Saccades *(new)*
  - [ ] Pursuit: Circle
  - [ ] Pursuit: Figure-8
  - [ ] Pursuit: Wave *(new)*
  - [ ] Pursuit: Lemniscate *(new)*
  - [ ] Pursuit: Spiral *(new)*
  - [ ] Verify: dot stays within screen bounds on all modes.
- [ ] **3.2 Flash Digits** — Shows digits briefly. Input field appears. Accepts answer.
- [ ] **3.3 Eye-Span** — Test horizontal, vertical, and mixed modes. Stimulus visible.
- [ ] **3.4 Peripheral Flash** — Flash appears. Feedback label doesn't overlap stimulus.
- [ ] **3.5 Slide Processing** — Slides display. Content matches current locale.

### Cognition

- [ ] **3.6 Schulte Grid** — Test sizes 3×3 through 7×7. Numbers visible on all color profiles.
  - [ ] Specifically test on Dark Blue profile — cells should have readable contrast.
- [ ] **3.7 Split Attention** — Test all 3 modes (Sequential, Simultaneous, Rapid).
  - [ ] Test eccentricity: set to "Narrow" — peripheral stimuli closer to center.
  - [ ] Test eccentricity: set to "Wide" — peripheral stimuli farther from center.
- [ ] **3.8 MOT** — Targets highlight, move, stop. Selection works. Results show.
- [ ] **3.9 Reaction Time — Simple** — Green dot appears. Click/press. Time recorded.
- [ ] **3.10 Reaction Time — Choice** — Colored shapes appear. Correct response required.
- [ ] **3.11 Reaction Time — Go/No-Go** — Green dot = click, red dot = don't click.
  - [ ] **Critical:** Red dot trials auto-advance after timeout (not stuck). *(was a bug)*
- [ ] **3.12 Rapid Decision Grid** — Grid renders. Answers register.
- [ ] **3.13 Sequence Memory** — Sequence plays. Input works.
- [ ] **3.14 Recall** — Items shown. Recall input works.

### Reading

- [ ] **3.15 Pacer** — Text renders. Pacer line moves at set WPM. Quiz at end.
- [ ] **3.16 RSVP** — Words flash at correct speed.
- [ ] **3.17 Chunking** — Chunks display at correct size and speed.
- [ ] **3.18 Spaced Repetition** — Cards show. Flip works. Rating buttons work.

**Phase 3 result:** PASS / FAIL  **Notes:** _______________

---

## Phase 4: Training Paths (P0–P1)

This area had the most changes. Test thoroughly.

### Basic Path Flow

- [ ] **4.1 Start a predefined path** — Pick "Daily Warmup". Step list shows. First exercise launches.
- [ ] **4.2 Complete an exercise in a path** — Finish the exercise. Path advances to next step.
- [ ] **4.3 Complete a full path** — Run all steps of "Quick Cognitive Check" (4 steps). Completion screen shows.
- [ ] **4.4 Resume a path** — Start a path, complete 2 steps, close app. Reopen. Path resumes at step 3.

### Custom Paths

- [ ] **4.5 Create a custom path** — Open path builder. Add 3 exercises. Enter a name. Save.
  - [ ] After saving, you land on "My Custom Paths" screen (not main paths).
  - [ ] The new path appears in the list.
- [ ] **4.6 Run a custom path to completion** — Start the custom path. Complete all steps.
  - [ ] Path marks as completed (was a bug — `finish_exercise` only checked `TRAINING_PATHS`).
- [ ] **4.7 Copy a predefined path** — Click COPY on any predefined path.
  - [ ] Path builder opens with steps pre-loaded.
  - [ ] Name ends with "(Copy)".
  - [ ] Save creates a new custom path.
- [ ] **4.8 Edit a custom path** — Click EDIT on a custom path.
  - [ ] Path builder opens with existing steps and name.
  - [ ] Change the name, add/remove a step. Save.
  - [ ] Changes persist. No duplicate path created.
- [ ] **4.9 Delete a custom path** — Click DELETE.
  - [ ] Confirmation dialog appears.
  - [ ] Cancel: path still exists.
  - [ ] Confirm: path removed. Progress cleared.

### Per-Step Config Panel

- [ ] **4.10 Config button appears** — On the path session screen, a ⚙ button shows next to ▶.
  - [ ] Only for exercises that have configurable params (not sequence_memory, etc.).
- [ ] **4.11 Config panel toggles** — Click ⚙. Panel appears with toggle buttons. Click again. Panel hides.
- [ ] **4.12 Config changes apply** — Change a param (e.g., grid size on a Schulte step). Launch. Exercise uses the new param.
- [ ] **4.13 Config on predefined path** — Change a param. Navigate away and back. Change does NOT persist (predefined paths are read-only).
- [ ] **4.14 Config on custom path** — Change a param. Navigate away and back. Change DOES persist.

### Custom Learning Material

- [ ] **4.15 Text prompt on add** — In path builder, add a Pacer/RSVP/Chunking step.
  - [ ] If custom texts exist in text library: dropdown appears with text choices.
  - [ ] If no custom texts: no dropdown, step added directly.
- [ ] **4.16 Text key in step label** — After selecting a custom text, the step label shows `[text name]`.
- [ ] **4.17 Custom text used at launch** — Run the step. Exercise uses the selected custom text.
- [ ] **4.18 Text restored after exercise** — After completing the exercise, the global training text reverts to the original.

**Phase 4 result:** PASS / FAIL  **Notes:** _______________

---

## Phase 5: Stats & Calendar (P1–P2)

- [ ] **5.1 Stats screen loads** — No crash. Shows XP, streak, exercise history.
- [ ] **5.2 Calendar layout** — 3-month grid with:
  - [ ] Weekday headers (Mo, Tu, We, Th, Fr, Sa, Su)
  - [ ] Day numbers in cells
  - [ ] Grid lines between cells
  - [ ] Active training days highlighted in accent color
  - [ ] Today has a distinct border
- [ ] **5.3 Calendar fits** — Calendar fits within the card. No overflow or clipping.
- [ ] **5.4 Empty calendar** — New user with no history. Calendar shows no highlighted days.
- [ ] **5.5 CSV export** — Export stats. File opens in a spreadsheet app. Data is correct.

**Phase 5 result:** PASS / FAIL  **Notes:** _______________

---

## Phase 6: Cross-Platform (P1–P2)

Test on each available platform.

### Windows

- [ ] **6.1** App launches. Fonts render correctly.
- [ ] **6.2** Timer resolution: exercises with precise timing (Reaction Time, Flash) feel responsive.
- [ ] **6.3** File dialogs (CSV export, text import) open native Windows dialogs.

### macOS

- [ ] **6.4** App launches. Fullscreen animation works.
- [ ] **6.5** Fonts load (Inter, JetBrains Mono, Source Serif 4).
- [ ] **6.6** File dialogs open native macOS sheets.

### Linux

- [ ] **6.7** App launches on X11.
- [ ] **6.8** App launches on Wayland (if available). No crash from `move()` calls.
- [ ] **6.9** Back button works on all screens (known issue reported on Linux).
- [ ] **6.10** File dialogs work.

**Phase 6 result:** PASS / FAIL  **Notes:** _______________

---

## Phase 7: Edge Cases (P2)

- [ ] **7.1 Rapid navigation** — Click through menus quickly (10+ screens in 5 seconds). No crash.
- [ ] **7.2 All color profiles in exercises** — Run one exercise on each of the 11 profiles. No unreadable text.
- [ ] **7.3 Long path name** — Create a custom path with a 50+ character name. UI doesn't break.
- [ ] **7.4 Empty custom paths** — "My Custom Paths" with no paths shows an empty message.
- [ ] **7.5 Multiple users** — Create a second user profile. Switch between them. Data is separate.
- [ ] **7.6 Window resize** — Resize the window. UI adapts. No clipped buttons or text.

**Phase 7 result:** PASS / FAIL  **Notes:** _______________

---

## Summary

| Phase | Result | Critical Issues |
|-------|--------|-----------------|
| 1. Startup & Navigation | | |
| 2. Settings & Persistence | | |
| 3. Exercises | | |
| 4. Training Paths | | |
| 5. Stats & Calendar | | |
| 6. Cross-Platform | | |
| 7. Edge Cases | | |

**Overall verdict:** READY FOR RELEASE / NEEDS FIXES

**Tested by:** _______________  **Date:** _______________
