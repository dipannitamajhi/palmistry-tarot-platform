# Palmistry & Tarot Intelligence Platform

An AI-powered web platform that analyzes palm images and tarot card spreads to generate personalized, self-reflection insights — covering personality, relationships, career, and life trends.

Built as an 8-week internship project for **Infosys Springboard**.

---

## Features

- **Authentication & roles** — JWT-based login/registration with four roles: User, Tarot Reader, Spiritual Consultant, and Administrator, each with role-based access control.
- **Palm Analysis Engine** — Upload a palm photo and get automatic detection of the Life, Head, Heart, and Fate lines using a custom-trained YOLO object detection model, with an OpenCV-based fallback for lines the model can't confidently find.
- **Tarot Reading Engine** — Full 78-card tarot deck with 6 spread types (Single Card, Three Card, Relationship, Career, Celtic Cross, Life Path).
- **AI Interpretation Engine** — Generates personalized readings using the OpenAI API when configured, with an automatic deterministic (rule-based) fallback so the app always works even without an API key.
- **Weighted Insight Scoring** — Combines palm analysis confidence, tarot interpretation relevance, personality alignment, user context, and reading consistency into a single insight score.
- **Dashboards & Analytics** — Personal reading history for users; platform-wide analytics (reading volume, top themes, user breakdown) for staff roles.
- **Notifications** — Reading reminders, insight updates, and platform announcements.
- **Reports & Export** — Export readings as PDF or Excel.



