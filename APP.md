# ChessHub — Application Specification

## Overview

**ChessHub** is an asynchronous, correspondence-style chess platform where players meet, play, and track their progress. Players make moves at their own pace — from minutes to days apart — and can resume games at any time. The platform includes a lobby for open challenges, direct invites, a friends/follow system, and an Elo-based leaderboard.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Framework | ASP.NET Core MVC (.NET 9) |
| Language | C# 12 |
| View engine | Razor (.cshtml) |
| Database | PostgreSQL (recommended) or MS SQL Server |
| ORM | Entity Framework Core |
| Real-time | SignalR |
| Authentication | ASP.NET Core Identity (local accounts — email + password) |
| Email (dev) | Mailpit (SMTP sink) |
| Chess rules | .NET chess library (e.g. Chess.NET) |
| Board UI | cm-chessboard (vanilla JS) |
| Interactivity | TypeScript + HTMX + SignalR JS client |
| Containerization | Docker Compose (DB + Mailpit) |

## Project Structure

```
ChessHub.sln
├── ChessHub.Web/          ← MVC app (Controllers, Views, wwwroot, Hubs)
├── ChessHub.Domain/       ← Entities, enums, value objects
├── ChessHub.Data/         ← EF Core DbContext, migrations, repositories
└── ChessHub.Services/     ← Business logic (chess engine, Elo, friends)
```

Dependency direction: `Web` → `Services` → `Data` → `Domain`.

## Database & Persistence

- **Provider**: PostgreSQL (via Npgsql), with MS SQL Server as a documented alternative.
- **Approach**: EF Core Code-First with migrations stored in `ChessHub.Data`.
- **Connection string**: configured via `appsettings.json` / environment variables, pointing to the Docker PostgreSQL container in development.

### Core Entities

```
User (extends IdentityUser)
  - EloRating
  - JoinDate
  - SendEmailOnMove (bool)
  - ProfileVisibility (enum: Public, FriendsOnly)

Game
  - WhitePlayerId, BlackPlayerId
  - CurrentFEN
  - Status (enum: WaitingForOpponent, InProgress, WhiteWon, BlackWon, Draw, Aborted)
  - CreatedAt, LastMoveAt
  - IsOpenInvite (bool)
  - DesiredColor (enum: White, Black, Random) — for open invite creator
  - ExpiresAt (nullable, for open invites)

Move
  - GameId, MoveNumber
  - FromSquare, ToSquare
  - PromotionPiece (nullable)
  - SAN (Standard Algebraic Notation)
  - Timestamp

Friendship
  - UserId, FriendId
  - CreatedAt

FriendRequest
  - SenderId, ReceiverId
  - Status (enum: Pending, Accepted, Rejected)
  - CreatedAt, ResolvedAt

Follow
  - FollowerId, FollowedId
  - CreatedAt

DirectInvite
  - SenderId, ReceiverId
  - DesiredColor
  - Status (enum: Pending, Accepted, Declined, Expired)
  - CreatedAt, ExpiresAt
```

## Authentication & Identity

- **ASP.NET Core Identity** with local accounts only (email + password).
- **Email confirmation required** — uses the default Identity flow. Confirmation link sent via email.
- Confirmation is enforced before: creating a game, joining a game, or sending friend requests. Browsing the lobby and leaderboard is allowed without confirmation.
- All protected endpoints use `[Authorize]`.
- Password reset via email (default Identity flow).

## Game Mechanics

### Time Model

- **Asynchronous only** — no clock, no countdown. Players move whenever they want.
- A game is never forfeited due to inactivity (no move deadlines in v1).
- The `LastMoveAt` timestamp is informational and displayed on the game page.

### Game Creation

**Open Invite** (appears in lobby):
1. Player creates a game, picks desired color (White / Black / Random).
2. The game appears in the public lobby with status `WaitingForOpponent`.
3. Any other logged-in, confirmed player can click "Join". The game starts immediately.
4. The invite expires after **72 hours** if unclaimed, or the creator can cancel it manually.

**Direct Invite** (point-to-point):
1. Player selects an opponent by username and picks desired color.
2. A `DirectInvite` is created with status `Pending` and a 24-hour expiration.
3. The recipient sees the invite as a notification. They can Accept or Decline.
4. On accept: game is created, both players are notified.
5. On decline or expiry: sender is notified.

### Move Validation

- Every move is validated server-side by the .NET chess library against the current FEN.
- Invalid moves are rejected with an error message.
- The library auto-detects: check, checkmate, stalemate, threefold repetition, 50-move rule, insufficient material.

### Game Endings

| Ending | Trigger | Result |
|--------|---------|--------|
| Checkmate | Auto-detected by engine | Winner declared |
| Stalemate | Auto-detected by engine | Draw |
| Resignation | Player clicks "Resign" | Opponent wins |
| Draw offer | Player offers → opponent accepts | Draw |
| Threefold repetition | Auto-detected by engine | Draw |
| 50-move rule | Auto-detected by engine | Draw |
| Insufficient material | Auto-detected by engine | Draw |

**Draw offer mechanics:**
- A player clicks "Offer Draw" during their turn.
- The opponent sees the offer. It stands until: the opponent accepts, the opponent makes a move (implicit decline), or the offering player withdraws it.

### Rematch

- After a game ends, both players see a "Rematch" button.
- Clicking it sends a rematch request to the opponent.
- If accepted, a new game is created with **colors swapped** (previous White gets Black and vice versa).
- If declined, players return to whatever page they were on.

### Game State on Resume

- When opening a game, the server loads the current FEN directly (instant board reconstruction).
- The full move history is loaded separately for display as a scrollable list with SAN notation.
- The FEN is the materialized state; moves are the source of truth. The FEN can always be rebuilt by replaying moves.

## Real-Time Updates (SignalR)

### Hubs

**GameHub** (`/hubs/game`):
- Groups: one group per game (`game-{gameId}`).
- Events pushed:
  - `MoveMade` — opponent made a move (includes SAN, FEN, move number).
  - `GameEnded` — game concluded (result, reason).
  - `DrawOffered` / `DrawOfferWithdrawn` / `DrawAccepted`.
  - `RematchOffered` / `RematchAccepted` / `RematchDeclined`.

**LobbyHub** (`/hubs/lobby`):
- Events pushed:
  - `GameCreated` — new open-invite game appeared.
  - `GameJoined` — an open-invite game was claimed (removed from lobby).
  - `GameCanceled` — an open invite was canceled or expired.

### Client Integration

- The SignalR JavaScript client connects on page load (authenticated via the Identity cookie).
- Incoming events update the chessboard (make opponent's move visible), show toast notifications, and trigger HTMX partial-refreshes for lists (lobby, game history, notifications).

## Lobby

- Accessible at `/lobby` (requires login).
- Displays all open-invite games with: creator username, creator Elo, desired color, time since created.
- Real-time updated via SignalR (new games appear, claimed games disappear).
- Each row has a "Join" button (hidden for games created by the current user).
- The page also shows a "Create Open Game" button and a "Invite Player" form (username input + color picker).

## Leaderboard

- Accessible at `/leaderboard` (public, no login required).
- Ranked by **Elo rating** descending.
- Columns: Rank, Username, Elo, Games Played, Win/Loss/Draw.
- Default view: top 50. Paginated for more.
- Optionally filterable by time period (all-time, last 30 days, last 7 days) — nice-to-have for v1.

## Elo Rating System

- Every player starts at **1200 Elo**.
- After each game (non-draw), Elo is recalculated using the standard formula:
  - Expected score for player A: `Ea = 1 / (1 + 10^((Rb - Ra) / 400))`
  - New rating: `Ra' = Ra + K * (Sa - Ea)` where `K = 32` and `Sa` is actual score (1 = win, 0 = loss, 0.5 = draw).
- Both players' ratings are updated in a single database transaction alongside the game result.
- Elo history is not tracked in v1 (current rating only).

## Friends & Follows

### Friendship (bidirectional, mutual)
1. User A sends a friend request to User B.
2. User B sees the request in their notifications and can Accept or Reject.
3. On acceptance, a `Friendship` row is created (bidirectional — A↔B).
4. Either user can unfriend at any time (removes the `Friendship` row).

### Follow (unidirectional)
1. User A follows User B — no approval needed.
2. A `Follow` row is created. User B is notified.
3. User A can unfollow at any time.
4. Following does not imply friendship and vice versa. They are independent.

## Notifications

### On-Site Badge
- A bell icon in the navigation bar displays a count of unread notifications.
- Notification types:
  - **Your turn** — an opponent moved in one of your games.
  - **Friend request** — received/sent status change.
  - **Game invite** — someone invited you to a direct game.
  - **Game ended** — a game you participated in concluded.
  - **New follower** — someone followed you.
- Clicking the bell shows a dropdown list of recent notifications.

### Email Notifications
- User-configurable toggle: `SendEmailOnMove` (default: true).
- Email is sent when: it's the user's turn (opponent moved), a game they're in ended, they received a friend request, or they received a direct game invite.
- Uses ASP.NET's `IEmailSender`. In development, emails are captured by Mailpit and viewable at `http://localhost:8025`.

## User Profile

**Public profile** (`/players/{username}`):
- Username, join date.
- Current Elo rating.
- Win / Loss / Draw record.
- Total games played.
- Friends list (visible to all logged-in users).
- **Game history** — paginated list of completed games. Each row shows: opponent, result, date, and a "Replay" button that navigates to a read-only game view.
- **Open games** — list of in-progress games (your turn highlighted). Each has a "Resume" button.

**Private settings** (`/account/settings`):
- Change email / password (default Identity UI).
- Email notification toggle.
- Profile visibility (Public vs. Friends-only).

## Spectating

- Any logged-in, confirmed user can navigate to `/games/{id}` and watch an in-progress game.
- Spectators see: the current board state, whose turn it is, and the move history in SAN notation.
- Spectators **cannot** interact — no moves, no chat, no draw offers.
- Board updates in real-time via the GameHub (spectators join the game's SignalR group in read-only mode).

## Local Development Setup

### Prerequisites
- .NET 9 SDK
- Docker Desktop (or Podman)
- Node.js (for TypeScript compilation)

### Quick Start
```bash
# 1. Start infrastructure
docker compose up -d    # PostgreSQL + Mailpit

# 2. Apply migrations
cd ChessHub.Data
dotnet ef database update

# 3. Run the app
cd ChessHub.Web
dotnet run
```

- App: `http://localhost:5000`
- Mailpit UI: `http://localhost:8025` (catch dev emails)

### docker-compose.yml (conceptual)
Services: `postgres` (port 5432) and `mailpit` (SMTP on 1025, UI on 8025). The app connects to these via `appsettings.Development.json`.

## Pages Map

| Route | Page | Auth Required |
|-------|------|:---:|
| `/` | Landing / home page | No |
| `/account/login` | Login | No |
| `/account/register` | Registration | No |
| `/account/settings` | User settings | Yes |
| `/lobby` | Lobby (open games + invite form) | Yes |
| `/leaderboard` | Leaderboard | No |
| `/players/{username}` | Player profile | No* |
| `/games/{id}` | Game page (play / spectate) | Yes |
| `/games/{id}/replay` | Replay completed game | Yes |
| `/friends` | Friends list + pending requests | Yes |
| `/notifications` | Full notifications page | Yes |

*Public profiles visible to all; friends-only profiles require login and friendship.

## Out of Scope (v1)

- Timed/real-time games
- In-game chat
- Engine analysis / computer evaluation
- Anti-cheating detection
- Tournament mode
- Mobile app (responsive web only)
- OAuth / social login
- Push notifications
- Elo history chart

---

*This specification is a living document. Amend as decisions are made during implementation.*