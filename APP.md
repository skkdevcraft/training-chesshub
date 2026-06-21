# ChessHub — Application Specification (Training Edition)

## Overview

**ChessHub** is an asynchronous, correspondence-style chess platform where players meet, play, and track their progress. Players make moves at their own pace and can resume games at any time.

The project is intended as an educational ASP.NET Core application demonstrating:

* ASP.NET Core MVC
* Razor Views
* ASP.NET Core Identity
* Entity Framework Core
* PostgreSQL
* SignalR
* Layered Architecture
* Domain Modeling
* Authorization
* Background Services
* Docker-based local development

The goal is to follow enterprise development practices while remaining achievable for a single developer.

---

# Technology Stack

| Layer                  | Technology                 |
| ---------------------- | -------------------------- |
| Framework              | ASP.NET Core MVC (.NET 10) |
| Language               | C#                         |
| View Engine            | Razor (.cshtml)            |
| Database               | PostgreSQL                 |
| ORM                    | Entity Framework Core      |
| Authentication         | ASP.NET Core Identity      |
| Real-time              | SignalR                    |
| Email                  | Mailpit (development)      |
| Chess Rules            | .NET chess library         |
| Board UI               | cm-chessboard              |
| Frontend Interactivity | HTMX + TypeScript          |
| Containerization       | Docker Compose             |

---

# Solution Structure

```text
ChessHub.sln

├── ChessHub.Web
├── ChessHub.Application
├── ChessHub.Infrastructure
├── ChessHub.Domain
└── ChessHub.Data
```

## Dependency Direction

```text
Web
 ↓
Application
 ↓
Infrastructure
 ↓
Data
 ↓
Domain
```

### Domain

Contains:

* Entities
* Enums
* Value Objects

No EF Core references.

### Application

Contains:

* Business services
* Interfaces
* Domain workflows

Examples:

```text
GameService
FriendshipService
NotificationService
EloService
AchievementService
```

### Infrastructure

Contains:

* Email implementation
* Chess library adapters
* External integrations

### Data

Contains:

* DbContext
* EF Core configuration
* Migrations

### Web

Contains:

* MVC Controllers
* Razor Views
* SignalR Hubs
* View Models

---

# Database & Persistence

## Provider

PostgreSQL via Npgsql.

## Approach

EF Core Code First.

Migrations stored in `ChessHub.Data`.

---

# Core Entities

## User

Extends IdentityUser.

```text
EloRating
JoinDate
SendEmailOnMove
CreatedAt
UpdatedAt
```

Default Elo:

```text
1200
```

---

## UserStatistics

```text
UserId
GamesPlayed
Wins
Losses
Draws
```

---

## Game

```text
WhitePlayerId
BlackPlayerId

CurrentFEN

Status
CreatedAt
UpdatedAt
LastMoveAt

IsOpenInvite
DesiredColor
ExpiresAt

RowVersion
```

Status:

```text
WaitingForOpponent
InProgress
WhiteWon
BlackWon
Draw
Aborted
```

---

## Move

```text
GameId
MoveNumber

FromSquare
ToSquare
PromotionPiece

SAN

Timestamp
```

---

## Friendship

```text
UserId
FriendId
CreatedAt
```

---

## FriendRequest

```text
SenderId
ReceiverId

Status

CreatedAt
ResolvedAt
```

Status:

```text
Pending
Accepted
Rejected
```

---

## DirectInvite

```text
SenderId
ReceiverId

DesiredColor

Status

CreatedAt
ExpiresAt
```

Status:

```text
Pending
Accepted
Declined
Expired
```

---

## Notification

```text
Id
UserId

Type
Message

IsRead

CreatedAt
```

Notification Types:

```text
YourTurn
FriendRequest
GameInvite
GameEnded
AchievementUnlocked
System
```

---

## Achievement

```text
Id
Name
Description
```

Example achievements:

```text
First Victory
5 Games Played
10 Games Played
Reach 1400 Elo
```

---

# Authentication & Identity

Uses ASP.NET Core Identity.

Authentication method:

```text
Email + Password
```

Features:

* Registration
* Login
* Logout
* Email Confirmation
* Password Reset

Email confirmation required before:

* Creating games
* Joining games
* Sending friend requests

---

# Game Mechanics

## Time Model

Asynchronous only.

No clocks.

No time controls.

No automatic losses due to inactivity.

---

## Open Games

### Creation

Player selects:

```text
White
Black
Random
```

An open game is created.

Status:

```text
WaitingForOpponent
```

Visible in the lobby.

---

### Joining

Any confirmed user may join.

The game immediately becomes:

```text
InProgress
```

---

### Expiration

Open games expire after:

```text
72 hours
```

if unclaimed.

---

## Direct Invites

Player selects:

```text
Opponent Username
Desired Color
```

Invite status:

```text
Pending
```

Recipient may:

```text
Accept
Decline
```

Direct invites expire after:

```text
24 hours
```

---

## Move Validation

Every move is validated server-side.

The chess library is responsible for:

* Legal move validation
* Check detection
* Checkmate detection
* Stalemate detection
* Threefold repetition
* Fifty-move rule
* Insufficient material

Invalid moves are rejected.

---

## Draw Offers

Player may offer a draw during their turn.

The offer remains active until:

* Accepted
* Withdrawn
* Opponent makes a move

---

## Resignation

Player may resign at any time.

Opponent wins immediately.

---

## Rematch

After game completion:

* Either player may offer a rematch.
* If accepted, a new game is created.
* Colors are swapped.

---

## Replay

Completed games support replay mode.

Controls:

```text
First Move
Previous Move
Next Move
Last Move
Auto Play
```

Replay is read-only.

---

# Elo Rating

Starting rating:

```text
1200
```

Formula:

```text
Ea = 1 / (1 + 10^((Rb - Ra) / 400))

Ra' = Ra + K * (Sa - Ea)

K = 32
```

Updated when a game ends.

Draws use:

```text
Sa = 0.5
```

---

# Concurrency Requirements

Only one move may be accepted for a turn.

Game updates must be transactional.

Suggested implementation:

```text
RowVersion
```

on the Game entity.

If concurrent submissions occur:

* One succeeds
* One fails gracefully

---

# Real-Time Updates (SignalR)

## GameHub

Route:

```text
/hubs/game
```

Group:

```text
game-{gameId}
```

Events:

```text
MoveMade
GameEnded

DrawOffered
DrawWithdrawn
DrawAccepted

RematchOffered
RematchAccepted
RematchDeclined
```

---

## LobbyHub

Route:

```text
/hubs/lobby
```

Events:

```text
GameCreated
GameJoined
GameCancelled
```

---

# Lobby

Route:

```text
/lobby
```

Requires authentication.

Displays:

* Open games
* Creator username
* Creator Elo
* Desired color
* Time since creation

Actions:

* Join Game
* Create Game
* Invite Player

Updates in real time.

---

# Leaderboard

Route:

```text
/leaderboard
```

Public.

Sorted by Elo descending.

Columns:

```text
Rank
Username
Elo
Games Played
Wins
Losses
Draws
```

Default:

```text
Top 50
```

Pagination required.

---

# Friends

## Friend Request

User A sends request.

User B may:

```text
Accept
Reject
```

Accepted requests create a Friendship.

---

## Unfriend

Either side may remove friendship.

---

# Notifications

## Navigation Badge

Navbar bell icon.

Displays unread count.

---

## Notification Types

```text
Your Turn
Friend Request
Game Invite
Game Ended
Achievement Unlocked
```

---

## Notification Page

Route:

```text
/notifications
```

Features:

* View notifications
* Mark as read
* Mark all as read

---

## Email Notifications

Only one email type:

```text
Your Turn
```

Controlled by:

```text
SendEmailOnMove
```

Uses:

```text
IEmailSender
```

Development email delivery:

```text
Mailpit
```

---

# User Profiles

Route:

```text
/players/{username}
```

Public.

Displays:

* Username
* Join Date
* Elo Rating
* Statistics
* Achievements
* Friends List
* Completed Games
* Active Games

---

# User Settings

Route:

```text
/account/settings
```

Allows:

* Change Email
* Change Password
* Toggle Email Notifications

---

# Achievement System

Achievements are automatically unlocked.

Examples:

```text
First Victory
5 Games Played
10 Games Played
Reach 1400 Elo
```

Unlocking an achievement creates a notification.

---

# Admin Area

Route:

```text
/admin
```

Requires:

```text
Administrator role
```

Capabilities:

* View users
* Disable user account
* Re-enable user account
* View active games

---

# Background Services

## InviteCleanupService

Runs hourly.

Responsibilities:

* Expire open games
* Expire direct invites
* Generate related notifications

Implemented using:

```text
BackgroundService
```

---

# Validation Rules

## Username

Requirements:

```text
3–20 characters
letters
numbers
underscore
unique
```

---

## Friend Requests

Rules:

```text
Cannot friend yourself
Cannot send duplicate request
Cannot friend existing friend
```

---

## Invites

Rules:

```text
Cannot invite yourself
Cannot join your own game
Cannot create duplicate pending invite
```

---

# Authorization Rules

Only game participants may:

```text
Make Move
Offer Draw
Withdraw Draw
Resign
Request Rematch
```

Only administrators may:

```text
Access Admin Area
Disable Accounts
```

---

# Logging

Use built-in ASP.NET logging.

Log:

```text
User Registration
User Login
Game Creation
Game Completion
Unexpected Exceptions
```

---

# Error Handling

Custom pages required:

```text
403 Forbidden
404 Not Found
500 Internal Server Error
```

User-friendly views.

---

# Local Development Setup

## Prerequisites

```text
.NET 10 SDK
Docker Desktop
Node.js
```

---

## Docker Services

```text
PostgreSQL
Mailpit
```

---

## Startup

```bash
docker compose up -d

dotnet ef database update

dotnet run
```

---

# Pages Map

| Route                 | Page          | Auth  |
| --------------------- | ------------- | ----- |
| `/`                   | Home          | No    |
| `/account/login`      | Login         | No    |
| `/account/register`   | Registration  | No    |
| `/account/settings`   | Settings      | Yes   |
| `/lobby`              | Lobby         | Yes   |
| `/leaderboard`        | Leaderboard   | No    |
| `/players/{username}` | Profile       | No    |
| `/games/{id}`         | Game          | Yes   |
| `/games/{id}/replay`  | Replay        | Yes   |
| `/friends`            | Friends       | Yes   |
| `/notifications`      | Notifications | Yes   |
| `/admin`              | Admin         | Admin |

---

# Definition of Done

A feature is considered complete only when:

* Domain model exists
* Database migration exists
* Validation implemented
* Authorization implemented
* Business logic implemented
* UI implemented
* Logging added where appropriate
* Feature works end-to-end

---

# Out of Scope (v1)

* Timed games
* Blitz chess
* Bullet chess
* Spectating
* In-game chat
* Chess engine analysis
* Anti-cheat detection
* Tournament mode
* Mobile applications
* Social login
* Push notifications
* Elo history charts
* AI opponents

---

*This specification is a living document and may be amended during implementation as new requirements emerge.*
