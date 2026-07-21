# Trupeer exploratory-testing bug report

> Replace each template below with only issues reproduced during the recorded exploratory session. Do not submit speculative bugs.

## Environment

- Browser: `REPLACE_WITH_BROWSER_AND_VERSION`
- OS: `REPLACE_WITH_OS_AND_VERSION`
- Account tier: Free
- Date tested: `REPLACE_WITH_DATE`

## Bugs Found

### `[BUG-001] Microphone permission not requested when creating a new video`

- **Severity:** High
- **Preconditions:** User is logged in, on dashboard, and initiates video creation
- **Steps to reproduce:**
  1. Navigate to the Trupeer dashboard
  2. Click on "Create Video" button to start a new recording
- **Expected result:** Browser should display a popup requesting microphone permission
- **Actual result:** No microphone permission popup appears; recording flow continues without requesting access
- **Evidence:** Part 1 recording timestamp when Create Video is clicked
- **Reproducibility:** Always

### `[BUG-002] Error Fetching Video Data after AI processing`

- **Severity:** Critical
- **Preconditions:** User recorded a video and submitted to Trupeer AI for processing
- **Steps to reproduce:**
  1. Record a video using the Create Video feature
  2. Submit the recording to Trupeer AI for video generation
  3. Wait for processing
- **Expected result:** Video data loads successfully and editor opens with the recorded content
- **Actual result:** After loading time, error appears: "Error Fetching Video Data - Failed to load video data. Please try again."
- **Evidence:** Part 1 recording timestamp during AI processing phase
- **Reproducibility:** Always

### `[BUG-003] Unable to complete video creation after recording - Error during AI audio addition`

- **Severity:** Critical
- **Preconditions:** User has recorded a video and initiates the AI processing phase
- **Steps to reproduce:**
  1. Record a video using the Create Video feature
  2. Submit the recording for AI processing (audio addition/generation)
  3. Wait for the AI processing to complete
- **Expected result:** Video is successfully processed with AI audio and ready for editing/export
- **Actual result:** Error occurs during the AI audio addition phase; unable to proceed to video editor or complete video creation
- **Evidence:** Error message displayed during AI processing phase (screenshot/logs)
- **Reproducibility:** Consistent

## Severity guide

| Severity | Use when |
| --- | --- |
| Critical | Data loss, account compromise, or core product unavailable for most users |
| High | A primary workflow (recording, editing, exporting) is blocked without a reasonable workaround |
| Medium | A feature is broken but a reasonable workaround exists |
| Low | Minor functional impact or unclear edge-case impact |

