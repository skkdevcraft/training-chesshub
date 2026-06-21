**12 milestones** for a **60-hour solo training project**:

Each milestone:

* introduce only a few new concepts,
* leave the application in a working state,
* build on previous milestones,
* produce visible progress.

The trainee should be able to finish one milestone every 4–6 hours of focused work.

---

# Milestone 1 — Solution Setup & Architecture

## Overview

Create the solution structure, configure the development environment, and establish the architectural foundation.

### Goals

* Create the solution
* Create projects
* Configure project references
* Configure PostgreSQL
* Configure Docker
* Verify application starts successfully

---

## Builds Upon

None.

This is the foundation milestone.

---

## Documentation

### ASP.NET Core MVC

[https://learn.microsoft.com/en-us/aspnet/core/mvc/overview](https://learn.microsoft.com/en-us/aspnet/core/mvc/overview)

### Entity Framework Core

[https://learn.microsoft.com/en-us/ef/core/](https://learn.microsoft.com/en-us/ef/core/)

### PostgreSQL Provider

[https://www.npgsql.org/efcore/](https://www.npgsql.org/efcore/)

### Docker Compose

[https://docs.docker.com/compose/](https://docs.docker.com/compose/)

---

## Outcome

The application starts successfully.

The solution contains:

```text
ChessHub.Web
ChessHub.Application
ChessHub.Infrastructure
ChessHub.Domain
ChessHub.Data
```

PostgreSQL and Mailpit run through Docker.

---

## Where To Start

1. Create solution.
2. Create projects.
3. Add references.
4. Configure PostgreSQL connection.
5. Verify application runs.

---

# Milestone 2 — Identity & Authentication

## Overview

Implement user registration, login, logout, email confirmation, and password reset.

### Goals

* Configure ASP.NET Identity
* Extend IdentityUser
* Registration
* Login
* Logout
* Email confirmation
* Password reset

---

## Builds Upon

Milestone 1.

Requires:

* Solution structure
* Database

---

## Documentation

### ASP.NET Identity

[https://learn.microsoft.com/en-us/aspnet/core/security/authentication/identity](https://learn.microsoft.com/en-us/aspnet/core/security/authentication/identity)

### Authorization

[https://learn.microsoft.com/en-us/aspnet/core/security/authorization](https://learn.microsoft.com/en-us/aspnet/core/security/authorization)

### Identity UI

[https://learn.microsoft.com/en-us/aspnet/core/security/authentication/scaffold-identity](https://learn.microsoft.com/en-us/aspnet/core/security/authentication/scaffold-identity)

---

## Outcome

Users can:

* Register
* Confirm account
* Login
* Logout
* Reset password

---

## Where To Start

1. Add Identity.
2. Create ApplicationDbContext.
3. Extend IdentityUser.
4. Create first migration.

---

# Milestone 3 — User Profiles & Statistics

## Overview

Create user profiles and player statistics.

### Goals

* User profile page
* UserStatistics entity
* Profile route
* Display Elo and statistics

---

## Builds Upon

Milestone 2.

Requires authenticated users.

---

## Documentation

### Razor Views

[https://learn.microsoft.com/en-us/aspnet/core/mvc/views/overview](https://learn.microsoft.com/en-us/aspnet/core/mvc/views/overview)

### Routing

[https://learn.microsoft.com/en-us/aspnet/core/fundamentals/routing](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/routing)

---

## Outcome

Visiting:

```text
/players/{username}
```

shows player information.

---

## Where To Start

1. Create UserStatistics.
2. Create ProfileController.
3. Create profile page.

---

# Milestone 4 — Lobby & Open Games

## Overview

Implement open game creation and joining.

### Goals

* Game entity
* Open invite creation
* Lobby page
* Join game

---

## Builds Upon

Milestones 1–3.

Requires authenticated users.

---

## Documentation

### EF Relationships

[https://learn.microsoft.com/en-us/ef/core/modeling/relationships](https://learn.microsoft.com/en-us/ef/core/modeling/relationships)

### Model Binding

[https://learn.microsoft.com/en-us/aspnet/core/mvc/models/model-binding](https://learn.microsoft.com/en-us/aspnet/core/mvc/models/model-binding)

---

## Outcome

Users can:

* Create open games
* View lobby
* Join open games

---

## Where To Start

1. Create Game entity.
2. Create migration.
3. Create LobbyController.
4. Create CreateGame form.

---

# Milestone 5 — Chess Board & Move Storage

## Overview

Display the board and persist moves.

### Goals

* Integrate cm-chessboard
* Create Move entity
* Store FEN
* Store move history

---

## Builds Upon

Milestone 4.

Requires existing games.

---

## Documentation

### cm-chessboard

[https://github.com/shaack/cm-chessboard](https://github.com/shaack/cm-chessboard)

### JavaScript Interop

[https://learn.microsoft.com/en-us/aspnet/core/client-side/javascript](https://learn.microsoft.com/en-us/aspnet/core/client-side/javascript)

---

## Outcome

Players see a board and move list.

Moves persist to database.

---

## Where To Start

1. Render board.
2. Create Move table.
3. Save moves.
4. Load FEN.

---

# Milestone 6 — Chess Rules Integration

## Overview

Integrate a chess library and validate moves.

### Goals

* Legal move validation
* Checkmate
* Stalemate
* Draw detection

---

## Builds Upon

Milestone 5.

Requires move storage.

---

## Documentation

### NuGet Packages

[https://learn.microsoft.com/en-us/nuget/consume-packages](https://learn.microsoft.com/en-us/nuget/consume-packages)

### Dependency Injection

[https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection)

---

## Outcome

Only legal moves are accepted.

Games automatically end correctly.

---

## Where To Start

1. Evaluate chess library.
2. Create adapter service.
3. Validate moves server-side.

---

# Milestone 7 — SignalR Real-Time Updates

## Overview

Add real-time updates for games and lobby.

### Goals

* GameHub
* LobbyHub
* Push updates
* Real-time board refresh

---

## Builds Upon

Milestone 6.

Requires playable games.

---

## Documentation

### SignalR

[https://learn.microsoft.com/en-us/aspnet/core/signalr/introduction](https://learn.microsoft.com/en-us/aspnet/core/signalr/introduction)

### SignalR JavaScript Client

[https://learn.microsoft.com/en-us/aspnet/core/signalr/javascript-client](https://learn.microsoft.com/en-us/aspnet/core/signalr/javascript-client)

---

## Outcome

Opponent moves appear automatically.

Lobby updates without page refresh.

---

## Where To Start

1. Create hubs.
2. Create groups.
3. Broadcast move events.

---

# Milestone 8 — Notifications

## Overview

Implement notification system.

### Goals

* Notification entity
* Bell icon
* Notification page
* Read/unread functionality

---

## Builds Upon

Milestone 7.

Requires game events.

---

## Documentation

### Partial Views

[https://learn.microsoft.com/en-us/aspnet/core/mvc/views/partial](https://learn.microsoft.com/en-us/aspnet/core/mvc/views/partial)

### View Components

[https://learn.microsoft.com/en-us/aspnet/core/mvc/views/view-components](https://learn.microsoft.com/en-us/aspnet/core/mvc/views/view-components)

---

## Outcome

Users receive notifications for:

* Your turn
* Friend requests
* Invites
* Game ended

---

## Where To Start

1. Create Notification entity.
2. Create NotificationService.
3. Add navbar bell.

---

# Milestone 9 — Friends System

## Overview

Implement friendships and friend requests.

### Goals

* Friend requests
* Accept/reject
* Friends page

---

## Builds Upon

Milestone 8.

Uses notifications.

---

## Documentation

### Many-to-Many Relationships

[https://learn.microsoft.com/en-us/ef/core/modeling/relationships/many-to-many](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/many-to-many)

---

## Outcome

Users can:

* Send requests
* Accept requests
* Remove friends

---

## Where To Start

1. Create entities.
2. Create service.
3. Add UI.

---

# Milestone 10 — Direct Invites & Rematches

## Overview

Allow users to challenge specific opponents.

### Goals

* Direct invites
* Rematch requests
* Invite expiration

---

## Builds Upon

Milestone 9.

Uses notifications and games.

---

## Documentation

### Hosted Services

[https://learn.microsoft.com/en-us/aspnet/core/fundamentals/host/hosted-services](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/host/hosted-services)

---

## Outcome

Users can invite friends directly.

Completed games support rematches.

---

## Where To Start

1. Create DirectInvite entity.
2. Create invite workflow.
3. Add rematch workflow.

---

# Milestone 11 — Elo, Leaderboard & Achievements

## Overview

Add progression systems.

### Goals

* Elo calculation
* Leaderboard
* Achievements

---

## Builds Upon

Milestone 10.

Requires completed games.

---

## Documentation

### LINQ

[https://learn.microsoft.com/en-us/dotnet/csharp/linq/](https://learn.microsoft.com/en-us/dotnet/csharp/linq/)

### EF Querying

[https://learn.microsoft.com/en-us/ef/core/querying/](https://learn.microsoft.com/en-us/ef/core/querying/)

---

## Outcome

Players gain rating.

Leaderboard shows rankings.

Achievements unlock automatically.

---

## Where To Start

1. Create EloService.
2. Update ratings on game completion.
3. Create leaderboard.
4. Create achievements.

---

# Milestone 12 — Administration, Background Jobs & Polish

## Overview

Finish operational concerns and harden the application.

### Goals

* Admin role
* Admin area
* InviteCleanupService
* Validation
* Logging
* Error pages

---

## Builds Upon

Everything.

This is the final milestone.

---

## Documentation

### Role-Based Authorization

[https://learn.microsoft.com/en-us/aspnet/core/security/authorization/roles](https://learn.microsoft.com/en-us/aspnet/core/security/authorization/roles)

### Logging

[https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging)

### Error Handling

[https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling)

---

## Outcome

Application is feature-complete.

Admin can:

* View users
* Disable users
* View active games

System automatically expires old invites.

Custom:

* 403 page
* 404 page
* 500 page

exist.

---

## Where To Start

1. Create Admin role.
2. Create admin area.
3. Implement InviteCleanupService.
4. Add validation rules.
5. Add error pages.
6. Review Definition of Done checklist.

---

# Final Deliverable

At the end of Milestone 12, the trainee should have:

✅ Multi-project enterprise ASP.NET solution

✅ Identity-based authentication

✅ PostgreSQL persistence

✅ Playable asynchronous chess

✅ SignalR real-time updates

✅ Notifications

✅ Friend system

✅ Direct invites

✅ Elo rankings

✅ Achievements

✅ Background services

✅ Admin area

✅ Dockerized development environment

✅ Proper layering and separation of concerns

This sequence intentionally introduces concepts in roughly the same order they appear in a typical business application, which makes it a good approximation of real-world ASP.NET development.
