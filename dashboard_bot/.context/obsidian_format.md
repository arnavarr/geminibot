# Obsidian Daily Note Format

## Template Structure

When creating Daily Notes, use the following format:

```markdown
---
date: {{YYYY-MM-DD}}
created: {{ISO8601_TIMESTAMP}}
tags: [daily-note]
---

# {{WEEKDAY}}, {{MONTH}} {{DAY}}, {{YEAR}}

## 🎯 Critical Alerts

> [!warning] Priority Items
> List any critical or high-priority items that need immediate attention.

- 🔴 [OD-XXX](link) - Critical issue description
- 🔴 [VUL-XXX](link) - Security alert description

## 📋 Pending Tasks

### High Priority
- [ ] [OD-XXX] Task summary - Status
- [ ] [ODC-XXX] Component task - In Progress

### Medium Priority
- [ ] [OD-XXX] Medium task description
- [ ] [SUP-XXX] Support ticket

### In Review
- [ ] [OD-XXX] PR awaiting review

## 📧 Important Emails

> Emails requiring action or response

1. **From:** sender@example.com
   **Subject:** Meeting reminder
   **Action:** Respond by EOD

2. **From:** alerts@jira.com
   **Subject:** [OD-123] Assigned to you
   **Action:** Review task

## 📝 Notes

*Space for meeting notes, thoughts, and action items*



---

## 🔄 Activity Log

*Auto-generated updates throughout the day*

```

## Guidelines

### Icons

- 🎯 Critical/Focus items
- 📋 Tasks
- 📧 Email
- 📝 Notes
- 🔄 Updates
- ✅ Completed
- 🔴 Highest/Critical priority
- 🟠 High priority
- 🟡 Medium priority
- 🟢 Low priority

### Jira Links

Format Jira issue links as: `[KEY-123](https://company.atlassian.net/browse/KEY-123)`

### Task Checkboxes

Use standard markdown checkboxes:

- `- [ ]` Incomplete
- `- [x]` Completed

### Timestamps

When appending updates, include a timestamp header:

```markdown
### 14:30 - Update Title
Content here...
```
