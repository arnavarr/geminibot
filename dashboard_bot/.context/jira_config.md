# Jira Configuration

## Projects

| Key | Name | Description |
|-----|------|-------------|
| OD | Operations Dashboard | Main product development |
| ODC | OD Components | Shared component library |
| VUL | Vulnerabilities | Security scanning and remediation |
| SUP | Support | Customer support tickets |

## Favorite JQL Queries

### Morning Review (Critical)

```jql
project IN (OD, ODC, VUL) 
  AND assignee = currentUser() 
  AND status NOT IN (Done, Closed, Resolved) 
  AND priority IN (Highest, High, Critical)
  ORDER BY priority DESC, updated DESC
```

### All My Open Tasks

```jql
project IN (OD, ODC, VUL, SUP) 
  AND assignee = currentUser() 
  AND status NOT IN (Done, Closed, Resolved)
  ORDER BY updated DESC
```

### Recently Updated (Last 24h)

```jql
project IN (OD, ODC) 
  AND updatedDate >= -1d 
  AND assignee = currentUser()
  ORDER BY updated DESC
```

### Waiting for Review

```jql
project IN (OD, ODC) 
  AND status = "In Review" 
  AND assignee = currentUser()
  ORDER BY updated DESC
```

### Security Alerts (High Priority)

```jql
project = VUL 
  AND priority IN (Highest, High, Critical) 
  AND status NOT IN (Done, Closed)
  ORDER BY priority DESC, created DESC
```

## Priority Mapping

| Priority | Emoji | Action Required |
|----------|-------|-----------------|
| Critical/Highest | 🔴 | Immediate attention |
| High | 🟠 | Address today |
| Medium | 🟡 | This week |
| Low | 🟢 | When time permits |

## Status Categories

- **To Do**: Not started
- **In Progress**: Currently working
- **In Review**: Awaiting approval
- **Blocked**: Needs intervention
- **Done/Closed**: Completed
