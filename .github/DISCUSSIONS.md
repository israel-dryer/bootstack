# GitHub Discussions setup for bootstack

Use this file as the maintainer checklist and source text for the pinned starter discussion.

## Recommended categories

Create these categories after enabling Discussions:

| Emoji | Name | Format | Description |
| --- | --- | --- | --- |
| 📣 | Announcements | Announcement | Project updates, releases, migration notes, and important changes from the maintainer. |
| ❓ | Q&A | Question and Answer | Usage questions, troubleshooting, and "how do I build this?" topics. |
| 💡 | Ideas & Feedback | Open-ended discussion | Early ideas, API suggestions, design feedback, and feature exploration. |
| 🧪 | Show and Tell | Open-ended discussion | Apps, examples, experiments, recipes, and patterns built with bootstack. |

Avoid creating broad categories such as General, Bug Reports, Feature Requests, or Documentation. Keep those workflows separate:

- Issues are for confirmed bugs, documentation defects, and accepted or scoped implementation work.
- Discussions are for questions, early ideas, examples, and community feedback.

## Pinned starter discussion

Suggested title:

```text
Start here: Questions, bugs, ideas, and support
```

Suggested body:

```markdown
Welcome to bootstack Discussions.

Please choose the right place so issues stay focused and actionable:

- **Q&A** — usage questions, troubleshooting, and "how do I build this?" topics.
- **Ideas & Feedback** — early feature ideas, API suggestions, and design feedback.
- **Show and Tell** — apps, screenshots, examples, experiments, recipes, and patterns built with bootstack.
- **Issues** — confirmed bugs, documentation defects, and scoped work items.

Before posting, please check the documentation and search existing issues/discussions.

If you have a reproducible bug, open a bug report issue and include your bootstack version, Python version, operating system, reproduction steps, and a minimal code sample.

If you are not sure whether something is a bug, start in Q&A.
```

## Manual GitHub setup steps

1. Open the repository settings.
2. In the Features section, enable Discussions.
3. Open the Discussions tab.
4. Edit the default categories to match the recommended category list above.
5. Make sure the category slugs match the discussion form filenames:
   - Q&A -> `q-a`
   - Ideas & Feedback -> `ideas-feedback`
   - Show and Tell -> `show-and-tell`
6. Create the pinned starter discussion from the text above.
