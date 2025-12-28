# GyanMitra Website - Complete Development Guide

## For: Frontend Developer (React)

**Backend API:** Already implemented and documented  
**Platform:** Web (Desktop & Mobile Responsive)  
**Tech Stack:** React 18+, React Router, Tailwind CSS (recommended)  
**Time Estimate:** 60–80 hours  

**GyanMitra** is an AI-powered educational assistant that helps students (Grades 5–10) learn from NCERT textbooks through an intelligent chat interface.

---

## Table of Contents
- Project Overview  
- Technical Architecture  
- Design System & Color Palette  
- Module Breakdown (11 Modules)  
- API Routes Reference  
- Deployment Guide  

---

## 1. Project Overview

### What is GyanMitra?
**Key Features**
- AI Chat Interface – Students ask questions, get answers with citations  
- Multi-subject Support – Math, Science, Social Science, English, Hindi, Sanskrit  
- Conversation History – Save and resume conversations  
- Source Citations – Every answer includes NCERT textbook references  
- Multi-language Support – English, Hindi, Marathi, Urdu  
- Email Verification – Secure account system  
- Feedback System – Rate AI responses  

---

## 2. Technical Architecture

### Frontend Structure

```bash
gyanmitra-web/
├── public/
│   ├── index.html
│   ├── logo.svg
│   └── favicon.ico
├── src/
│   ├── components/        # Reusable UI components
│   ├── pages/            # Route pages
│   ├── services/         # API integration
│   ├── contexts/         # React Context (Auth, etc.)
│   ├── utils/            # Helper functions
│   ├── hooks/            # Custom React hooks
│   ├── styles/           # Global styles
│   ├── types/            # TypeScript interfaces
│   └── config/           # Configuration files
├── .env                  # Environment variables
└── package.json
```

| Layer     | Technology      | Purpose           |
| --------- | --------------- | ----------------- |
| Framework | React 18+       | UI framework      |
| Routing   | React Router v6 | Navigation        |
| State     | Context API     | Global state      |
| Styling   | Tailwind CSS    | Utility-first CSS |
| HTTP      | Axios           | API calls         |
| Forms     | React Hook Form | Form validation   |
| Icons     | Heroicons       | Icon library      |
| Toast     | React Hot Toast | Notifications     |

# Module Breakdown

## Module 1 – Project Setup & Configuration (2 hours)

### Purpose:
Set up the React project with all dependencies and folder structure.

### Tasks

1. Initialize React Project
 - Create React app with TypeScript
 - Install dependencies: React Router, Axios, Tailwind CSS
 - Configure Tailwind CSS
 - Set up absolute imports (@/ paths)

2. Environment Configuration
 - Create .env file
 - Add backend API URL
 - Configure API base URL

3. Folder Structure creation

Global Styles
 - Set up Tailwind CSS configuration
 - Create global CSS file
 - Define color variables
 - Set up fonts

Deliverables

✅ Working React development server

✅ Tailwind CSS configured

✅ Folder structure created

# Module 2 – Authentication System (8 hours)

### Purpose:
Build complete user authentication with login, registration, and email verification.

### Routes

/login          – Login page  
/register       – Registration page  
/verify-email?token=xxx – Email verification

### Backend API Routes
POST /api/auth/register  
POST /api/auth/login  
GET  /api/auth/verify-email?token=xxx  
GET  /api/auth/me

- File: src/services/authService.js

- Purpose: Handle all API calls related to authentication

### Methods to Implement

register(name, email, password, grade, subjects) → POST /auth/register

login(email, password) → POST /auth/login

verifyEmail(token) → GET /auth/verify-email

getCurrentUser() → GET /auth/me

logout() → Clear local storage

### Storage:
Store JWT token in localStorage

Store user data in localStorage

Include token in Authorization header


### File: src/contexts/AuthContext.jsx

Purpose: Manage global authentication state

### State to Manage

- user – Current user object

- isAuthenticated – Boolean

- isLoading – Loading state

### - Features

- login(email, password)

- register(...)

- logout()

- Auto-load user on app start

- Redirect to login if not authenticated

- Persist token across refreshes

### File: src/pages/LoginPage.jsx

Layout

┌───────────────────────────────────┐
│           [GyanMitra Logo]        │
│      Welcome Back to GyanMitra    │
│     Learn with NCERT AI Assistant │
│   [Email Input]                   │
│   [Password Input]                │
│   [Login Button]                  │
│   Don't have an account? [Sign Up]│
└───────────────────────────────────┘

### Design Specs

- Container: max-width 400 px, centered, padding 40 px

- Logo: 60 px height, margin-bottom 32 px

- Title: 28 px bold, primary color

- Subtitle: 14 px secondary text

- Form: white card, shadow, padding 24 px, radius 12 px

- Inputs: height 48 px, border 1 px #E0E0E0, radius 8 px, font 14 px

- Button: full-width 48 px high, gradient bg, white text, radius 8 px

- Hover: slight scale effect

### Form Validation

- Email: required & valid

- Password: required (min 6 chars)
Show errors in red below inputs.

### Success Flow

- On submit → call authService.login()

- Show spinner while loading

- Store token + update context

- Redirect to /chat on success

- Show error toast on fail

### File: src/pages/RegisterPage.jsx

### Layout

┌───────────────────────────────────┐
│         [GyanMitra Logo]          │
│      Create Your Account          │
│     Start learning with AI        │
│  [Full Name]  [Email]  [Password] │
│  [Select Grade (5–10)]            │
│  [Select Subjects Math…]          │
│  [Register Button]                │
│  Already have account? [Login]    │
└───────────────────────────────────┘

### Grade Selector

- Display as pill buttons (5–10)

- Single selection

- Active grade → gradient background

- Inactive → border only

### Subject Selector

- Display as checkbox labels

- Multiple selection allowed

- Options: Math, Science, Social Science, English, Hindi, Sanskrit

### Form Validation

- Name: min 3 chars

- Email: valid

- Password: min 6 chars

- Grade & ≥ 1 subject required

### Success Flow

- Call authService.register()

- On success → “Registration successful! Check email to verify.”

- Redirect to /login after 3 s

- On error → show toast
  
### File: src/pages/VerifyEmailPage.jsx

Layout
┌───────────────────────────────────┐
│         [GyanMitra Logo]          │
│     Verifying Your Email...       │
│     [Loading Spinner]             │
│     ✅ Email Verified Successfully!│
│     You can now login             │
│     [Go to Login]                 │
└───────────────────────────────────┘

### Logic

- Extract token from URL

- Call authService.verifyEmail(token)

- Show spinner while verifying

- On success → success icon + message

- On error → error message + “Go to Register” button

### Design

- Centered content

- Large icon (checkmark / error)

- Title 24 px

- Button below message

### Module 2 Exit Criteria
✅ User can register with email

✅ Email verification works

✅ User can login

✅ Protected routes work

✅ Auth persists across refresh

✅ Logout works

✅ Validation + error handling implemented

## Module 3 – Main Chat Interface

Purpose: Build the core AI chat interface where students interact with the assistant.


Backend API: POST /api/query

File: src/services/chatService.js

Methods

- sendQuery(query, grade, subject, language, conversationId) → POST /query
Parse response → extract answer, citations, conversationId.
Handle errors gracefully.


### File: src/pages/ChatPage.jsx

Layout (Desktop)
┌────────────────────────────────────────────────────┐
│ [GyanMitra] [Profile] [Logout] – Header           │
├─────┬──────────────────────────────────────────────┤
│Sidebar│Welcome to GyanMitra! Your AI Assistant     │
│History│[Quick Question Cards]                      │
│ [+]  │[Input Bar Ask Anything…][Send]              │
└─────┴──────────────────────────────────────────────┘

### Layout Breakdown

- Sidebar (Left): 280 px width, conversation list, New Chat button.

- Main Area: messages, empty state, input bar at bottom.

- Header: 60 px high, logo left, profile dropdown right, logout option.

### File: src/components/chat/SubjectSelector.jsx

- Layout: [Math ▼] Grade 8
- Design: Dropdown menu for subject selection, grade readonly, changes context when switched.

### File: src/components/chat/MessageBubble.jsx

User Message


                 ┌────────────────────────┐
                 │What is photosynthesis?│
                 │                11:32  │
                 └────────────────────────┘

Gradient background, white text, radius 16 px (8 px bottom-right), padding 12×16, max-width 70%.

AI Message
┌────────────────────────────────────────┐
│Photosynthesis is the process by which…│
│Sources: [1] NCERT Science Grade 8…    │
│Was this helpful? 👍 👎  11:32          │
└────────────────────────────────────────┘

White background, border #E0E0E0, radius 16 px (8 px bottom-left).

### File: src/components/chat/CitationCard.jsx
┌────────────────────────────────────┐
│[1] NCERT Science Grade 8           │
│  Chapter 7: Nutrition in Plants    │
│  Page 92                           │
│  "Plants make their own food…"     │
│  [View Details →]                  │
└────────────────────────────────────┘

### File: src/components/chat/InputBar.jsx

┌────────────────────────────────────────────┐
│Ask anything about NCERT textbooks…  [Send]│
└────────────────────────────────────────────┘

Fixed bottom, white bg, border-top 1 px #E0E0E0, padding 16 px.
Input has radius 24 px, padding 12×20, send button 48 px circle with gradient bg.
Enter key submits; disable while loading

### File: src/components/chat/EmptyState.jsx

Centered in chat area with large icon (96 px, gradient), title 28 px, subtitle 16 px, quick question cards (300 px wide, border, hover shadow+scale).
Click → send as query.

Module 3 Exit Criteria

✅ User can send messages

✅ AI responses display correctly

✅ Citations show properly

✅ Subject selector works

✅ Empty state shows

✅ Loading states work

✅ Messages scroll properly

✅ Input validation works


## **Module 4 – Conversation History (6 hours)**

**Purpose:**  
Display list of past conversations in sidebar with ability to load and continue them.

**Backend API Routes**
```bash
GET /api/conversations?page=1&limit=10  
GET /api/conversations/:id  
DELETE /api/conversations/:id
```
### File: src/services/conversationService.js

Methods

- getConversations(page, limit) → GET /conversations

- getConversationById(id) → GET /conversations/:id

- deleteConversation(id) → DELETE /conversations/:id

### File: src/components/chat/Sidebar.jsx

Layout
┌─────────────────────┐
│  [+ New Chat]       │
├─────────────────────┤
│  Today              │
│  ┌────────────────┐ │
│  │ What is...     │ │
│  │ 2 hours ago    │ │
│  └────────────────┘ │
│  Yesterday          │
│  ┌────────────────┐ │
│  │ Explain...     │ │
│  │ Yesterday      │ │
│  └────────────────┘ │
│  [Load More]        │

└─────────────────────┘

### Design

- Sidebar bg: #FAFAFA

- Border-right: 1 px solid #E0E0E0

- “New Chat” button: full width, primary gradient background, white text, 12 px radius, margin 16 px

- Conversation Cards: white bg (hover #F5F5F5), radius 8 px, padding 12 px, margin 8 px 16 px
 - Title 14 px bold, truncate 1 line
 - Timestamp 11 px light text
 - Active conversation: primary border 2 px
 - Hover → cursor pointer, delete icon (X) visible

- Grouping: “Today”, “Yesterday”, “Last 7 Days”, “Older” (headers 12 px uppercase bold secondary color padding 16 px)


### Task 4.3 – Load Conversation Logic

Flow

1. User clicks conversation card

2. Call conversationService.getConversationById(id)

3. Show loading spinner in chat area

4. Transform messages to UI format

5. Display all messages in chat

6. Update current conversationId

7. Highlight active conversation in sidebar

8. Click delete → Confirm dialog → Remove from list

Module 4 Exit Criteria

✅ Conversations list in sidebar

✅ Grouped by date

✅ Clicking conversation loads it

✅ Delete conversation works

✅ Pagination (Load More) works

✅ Active conversation highlighted

✅ New chat button creates new

## Module 5 – Feedback System (4 hours)

Purpose:
Allow users to rate AI responses with thumbs up/down.

Backend API Route

- POST /api/feedback

File: src/services/feedbackService.js

### Methods

submitFeedback(conversationId, messageIndex, rating) → POST /feedback

### File: src/components/chat/FeedbackButtons.jsx

Design

Was this helpful?  👍 👎

### Specs

- Font size: 11 px secondary text

- Buttons 32 × 32 px circle, transparent bg (hover #F5F5F5)

- Icons 16 px thumbs up/down

- Gap 8 px between buttons

### Logic

1. User clicks button

2. Call feedbackService.submitFeedback()

3. Highlight selected button (primary color)

4. Store feedback in localStorage (to avoid re-show)

5. Disable both buttons after selection

6. Fade out after 1.5 s

### Module 5 Exit Criteria

✅ Feedback buttons show on AI messages

✅ Click sends feedback to backend

✅ Visual feedback on click

✅ Buttons disappear after feedback

✅ Don’t show if feedback already given


### Module 6 – User Profile & Settings (5 hours)

Purpose:
User profile page with account details and settings.

Route: /profile

File: src/pages/ProfilePage.jsx

Layout

┌────────────────────────────────────────┐
│ [Header: Profile]                      │
├────────────────────────────────────────┤
│  [Avatar Icon]  John Doe  john@example.com  Grade 8  Subjects: Math, Science  [Edit Profile]  
│  [Account Settings Card] Preferred Language: English ▼  [Save Changes]  
│  [Logout Button (Card)] Red Background  
└────────────────────────────────────────┘


### Design

- Max-width 600 px centered, sections as white cards

- Avatar 80 px circle (initials or icon)

- Name 16 px bold, email 14 px secondary

- Edit button secondary style

- Logout button red background

### Module 6 Exit Criteria

✅ Profile displays user info

✅ Edit profile works

✅ Change language works

✅ Logout button works


# Module 7: Responsive Design (6 hours)

Purpose:

Make entire website responsive for mobile and tablet.

Breakpoints:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

Mobile Layout Changes:

Chat Page:

[=] GyanMitra [[]] | Header

AI Message  
User Message

[Input Bar]

Changes:

- Hide sidebar by default
- Show hamburger menu (⇨)
- Clicking hamburger opens sidebar as overlay
- Message bubbles: max-width 85%
- Input bar: full width
- Profile dropdown menu

Module 7 Exit Criteria:
- ✔ Mobile layout works
- ✔ Sidebar is toggleable on mobile
- ✔ Touch-friendly button sizes
- ✔ Text readable on mobile
- ✔ No horizontal scroll

# Module 8: Error Handling & Loading States (4 hours)

Purpose:

Handle all error scenarios and show proper loading states.

Task 8.1: Loading States

Scenarios:

1. Initial page load → Skeleton loader  
2. Sending message → Loading spinner in send button  
3. Loading conversation → Skeleton in chat area  
4. Loading history → Skeleton in sidebar

Task 8.2: Error States

Scenarios:

1. Network error → "Check your connection" banner  
2. Server error → "Something went wrong" message  
3. Auth error → Redirect to login  
4. Invalid input → Form validation errors  

Error Boundary:

- Catch React errors  
- Show fallback UI  
- Log to console/monitoring  

Module 8 Exit Criteria:

- ✔ All loading states implemented  
- ✔ All error scenarios handled  
- ✔ Error boundary catches crashes  
- ✔ User-friendly error messages  

# Module 9: Accessibility (3 hours)

Purpose:

Make website accessible to all users.

Checklist:

- ✔ Keyboard navigation works  
- ✔ Focus indicators visible  
- ✔ ARIA labels on buttons  
- ✔ Alt text on images  
- ✔ Color contrast meets WCAG AA  
- ✔ Screen reader compatible  
- ✔ Skip to main content link  

# Module 10: Performance Optimization (4 hours)

Purpose:

Optimize website performance.

Optimizations:

1. Code splitting (lazy load routes)
2. Memoize expensive components
3. Debounce input fields
4. Optimize images
5. Minimize bundle size
6. Cache API responses
7. Prefetch on hover

Module 10 Exit Criteria:

- ✔ Lighthouse score > 90
- ✔ First Contentful Paint < 1.5s
- ✔ Time to Interactive < 3.0s
- ✔ Bundle size < 300KB (gzipped)

5. API Routes Reference

Base URL:
https://api.gyamritra.com/api

Authentication:
All authenticated routes require:

Headers: {
Authorization: "Bearer <jwt_token>" }

Endpoints:

| Method    | Route    | Purpose   | Auth Required |
|---|---|---|---|
| POST    | /auth/register    | User registration | No    |
| POST    | /auth/login    | User login    | No    |
| GET    | /auth/verify-email?token=xxx | Verify email | No    |

| Method    | Route    | Purpose    | Auth Required |
|---|---|---|---|
| GET    | /auth/me    | Get current user   | Yes    |
| POST    | /query    | Submit question    | Yes    |
| GET    | /conversations    | List conversations  | Yes    |
| GET    | /conversations/:id    | Get conversation    | Yes    |
| DELETE    | /conversations/:id    | Delete conversation  | Yes    |
| POST    | /feedback    | Submit feedback  | Yes    |
| GET    | /health    | Health check    | No    |

# 6. Deployment Guide
Environment Variables:
REACT_APP_API_URL=https://api.gyanmitra.com/api
REACT_APP_WEBSITE_URL=https://gyanmitra.com# GyanMitra
