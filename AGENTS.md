# Project Instructions for Codex

## 1. Project Identity and Long-Term Vision

Build an ambitious Roblox open-world cops-versus-criminals game with a distinctive Indian identity. Use Jailbreak and Mad City as references for gameplay accessibility, polish, and stylised visual quality. Develop original systems, environments, assets, and presentation; do not copy their proprietary assets, scripts, maps, or implementations.

Begin development exclusively in Kolkata. Design foundations that can later support approximately three to four interconnected cities, including Mumbai, Delhi, and potentially Chennai. Treat later cities as expansion possibilities, not instructions to build them immediately.

Keep all cities within one continuous Roblox world and one gameplay place. Players must be able to travel naturally between cities without teleporting between separate Roblox places. Use world streaming and deliberate world layout to support this requirement. Do not replace it with separate city places without an explicit change in creative direction from the user.

Create condensed, gameplay-friendly interpretations of cities rather than geographically accurate, full-scale reproductions. Preserve recognisable landmarks, neighbourhood character, and useful spatial relationships while prioritising navigation, driving, pursuit, exploration, and enjoyable gameplay. Do not require a complete city or map before implementing playable systems.

## 2. Roles, Responsibilities, and Agent Autonomy

The human user is the creative director. They communicate ideas, priorities, desired experiences, and feedback in natural language. Codex is the primary and effectively sole technical developer.

Own the complete technical implementation, including:

- Luau programming, architecture, networking, persistence, and game systems.
- Roblox Studio development, terrain, world construction, and asset integration.
- 3D modelling, procedural asset generation, optimisation, and animation.
- UI/UX, input handling, sound integration, lighting, and visual effects.
- Multiplayer gameplay, combat, robberies, police mechanics, vehicles, economy, and progression.
- Testing, debugging, profiling, maintenance, technical research, and development tooling.

Make reasonable technical decisions autonomously within the agreed creative direction. Resolve routine implementation details, investigate errors, and complete necessary technical work without transferring it to the user. Ask for direction when a meaningful creative choice, conflicting requirement, or genuinely ambiguous scope cannot be resolved from the conversation and project records.

Use available tools honestly. Never claim that an asset was generated, a Studio change was applied, a capability exists, a test passed, or an implementation is complete without evidence. When a tool or account limitation requires human action, explain the exact limitation and request only the minimum action needed. Continue useful independent work where possible.

Respect higher-priority instructions and the user's current scope. Follow these project instructions for routine development; they do not authorise unrelated work, destructive changes, public publication, purchases, or external communication.

## 3. Development Workflow and Decision-Making

- Understand the requested player experience, relevant existing systems, and applicable project instructions before making changes. Inspect only what is needed for the active task.
- Build through small, playable, testable increments. Complete coherent slices of functionality and incorporate feedback before broadening their scope.
- Choose the simplest design that satisfies current needs and allows foreseeable city expansion. Avoid speculative systems, premature abstraction, and unnecessary framework adoption.
- Reuse suitable existing modules, configurations, assets, and conventions before introducing alternatives. Preserve established functionality and user work.
- Separate configurable gameplay values from system logic when tuning or reuse warrants it. Do not introduce configuration layers for values that have no practical reason to vary.
- Consider networking, security, persistence, mobile controls, streaming, and performance while designing a feature, rather than postponing them until integration.
- Investigate root causes before applying fixes. Keep changes focused, handle relevant edge cases, and leave unrelated refactoring for a justified task.
- Use Roblox Studio MCP, Blender, Blender Python, Rojo, Git, open-source libraries, asset-generation tools, or other suitable tools when available and useful. Select tools autonomously without mandating a particular framework, workflow, or dependency in advance.
- Verify unfamiliar or version-sensitive APIs and tool capabilities against current authoritative documentation. Evaluate dependencies before adopting them.
- Use version control when established or appropriate to the task. Keep changes reviewable, protect uncommitted user work, and avoid destructive history or file operations without clear authorisation.
- Work only on the `main` Git branch. Do not create or switch to task branches or worktrees unless the user explicitly changes this instruction. Commit and push completed work on `main`.
- Report what changed, the evidence supporting completion, and material limitations. Distinguish implemented behaviour from plans, placeholders, and unverified assumptions.

## 4. Roblox Architecture and Luau Coding Standards

### Structure and responsibilities

Organise code by clear responsibilities and cohesive features. Keep authoritative server logic, client presentation and input, and genuinely shared definitions separate. Use Roblox containers according to their replication and execution behaviour. Keep secrets, trusted rules, and sensitive logic out of replicated containers.

Use modules with explicit interfaces and ownership. Keep dependencies understandable, avoid circular dependencies and uncontrolled global state, and separate reusable mechanics from city-specific content. Provide clear initialisation and cleanup paths. Add architectural layers only when they solve a demonstrated problem.

Represent city-specific locations, robbery sites, vehicle spawn points, and similar content through consistent data or authored metadata where appropriate. Use stable identifiers where content must survive renaming or persistence. Foundational systems must support adding locations and cities without duplicating or rewriting core gameplay logic.

Choose one clear source of truth for each kind of project content once the actual workflow is established. If filesystem code and Studio are synchronised, document which side owns each asset or script and avoid edits that the next synchronisation will overwrite. Do not assume Rojo, a repository layout, a framework, or an existing synchronisation setup before it has been chosen.

### Luau implementation

- Use descriptive, consistent names, explicit module interfaces, and small functions with clear purposes. Follow established project formatting once it exists.
- Prefer strict type checking for new modules where practical. Define useful types at system boundaries and for shared data; do not silence errors with broad casts or pervasive `any`.
- Keep business rules readable. Comment intent, invariants, and non-obvious platform constraints rather than narrating straightforward code.
- Use appropriate Roblox APIs and avoid deprecated patterns. Give asynchronous operations explicit ownership, cancellation or timeout behaviour where relevant, and observable failures.
- Avoid unbounded waits, busy loops, repeated full-world scans, and unnecessary per-frame work. Use events and scoped queries when suitable.
- Disconnect event connections and release temporary instances, tasks, and references when their owner ends. Account for respawning, player departure, destroyed objects, and interrupted actions.
- Treat errors according to their impact. Use protected calls around fallible external or persistence operations where needed, provide useful context, and do not swallow failures or wrap all logic indiscriminately.
- Make repeated setup and teardown safe where a system can be restarted or re-entered. Prevent duplicate connections, rewards, spawns, and background tasks.

## 5. World Building and 3D Asset Creation

Construct Kolkata with a consistent scale for players, vehicles, doors, roads, interiors, and cover. Use gameplay needs to determine distances and building dimensions. Reserve space and sensible connection points for future expansion without constructing future cities prematurely.

Develop reusable building kits, road components, props, materials, and placement conventions. Support variation in facades, rooftops, shopfronts, signage, and street furniture so reuse preserves local character. Avoid large collections of unrelated imported assets with inconsistent scale or style.

Organise world content predictably by city, district, location, and function as the project grows. Keep visible geometry, collision geometry, interactive objects, and gameplay metadata understandable. Use names, tags, attributes, and model boundaries consistently where they simplify authoring and runtime discovery.

For created or imported assets:

- Use clean geometry, sensible pivots and orientation, consistent units, and intentional material assignments.
- Prefer reusable meshes and shared textures where they preserve visual quality. Remove hidden or unnecessary geometry and unused imported content.
- Choose detail according to player proximity, silhouette, interaction, and importance. Spend geometry where players can perceive it.
- Build simplified collision geometry appropriate to walking, driving, combat, and interiors. Check snagging, gaps, inaccessible spaces, and vehicle clearance.
- Keep static scenery anchored and reserve moving assemblies for objects that need motion. Define assembly structure deliberately.
- Validate imported scale, normals, materials, collisions, and appearance in Roblox Studio. An export succeeding does not establish that an asset works in the game.
- Preserve editable source assets and generation scripts when they are needed for reproducible maintenance, using the project's chosen asset workflow.
- Save final original asset preview PNGs in the asset's folder and track them in Git. Keep downloaded photographic references separate from original renders; retain their source manifests without redistributing photos without permission.

Design robbery interiors and interactive landmarks together with their approach routes, entrances, exits, pursuit paths, and surrounding streets. Avoid decorative construction that prevents the intended gameplay from working.

## 6. Visual Direction and Landmark Fidelity

Target polished low-to-mid-poly environments with coherent materials, attractive lighting, clean geometry, readable silhouettes, and distinctive Indian architecture. Use visual consistency as the standard for detail decisions. Avoid unnecessary realism and generic city assets that erase regional identity.

Make the setting recognisably Indian through architecture, road and street layouts, vehicles, shopfronts, public transport cues, cultural details, street furniture, and signage. Keep those elements grounded in the specific city. Use references and verify unfamiliar details instead of relying on stereotypes or invented local text.

Treat Victoria Memorial, Howrah Bridge, and other important landmarks as recognisable architectural subjects. Research reliable visual references before modelling them. Preserve the defining silhouette, proportions, major structural elements, and architectural character while adapting scale and geometry to the game's stylised world.

Allow landmarks substantially more geometric and architectural detail than ordinary buildings when their gameplay and visual importance justify it. Review them from relevant street, approach, and distant viewpoints. Keep surrounding ordinary buildings simpler so the world remains readable and affordable to render.

Important landmarks may become elaborate robbery or heist locations when requested. Do not assume every landmark is a robbery target. Keep recognisable exterior features compatible with any authorised gameplay adaptation.

Maintain a coherent palette, material language, lighting approach, UI style, and effects language as these are established. Evaluate assets in the actual game environment, including typical camera distances and mobile screens. Use lighting and effects to support atmosphere and gameplay clarity.

## 7. Multiplayer Security and Gameplay Systems

### Trust and remote boundaries

Make the server authoritative for money, inventory, progression, damage, arrests, wanted state, rewards, purchases, and other consequential gameplay state. Treat client messages as requests. Clients may provide responsive input, prediction, animation, camera behaviour, and presentation, with server validation and reconciliation where needed.

For every RemoteEvent and RemoteFunction:

- Define its purpose, accepted payload, caller permissions, and authoritative result.
- Validate types, structure, size, finite numeric values, ranges, identifiers, and referenced instances. Confirm that instance arguments belong to the expected context.
- Validate action eligibility, state transitions, distance, timing, equipment ownership, and other relevant prerequisites against server-observed state.
- Apply appropriate per-player and per-action rate limits and bound processing cost. Reject duplicate, stale, malformed, and impossible requests safely.
- Do not accept client-supplied prices, rewards, damage totals, ownership, or success claims as authoritative.
- Avoid allowing a client request to select arbitrary code, object paths, or unrestricted server actions.

Keep remote handling focused and observable. Use RemoteFunctions only when a request and response are actually needed; avoid server-critical flows that can be held up by an unresponsive client.

### Gameplay integrity

Model robberies, arrests, combat actions, purchases, and reward claims with explicit valid states and transitions. Handle simultaneous interactions, interruption, death, respawn, player departure, and repeated requests. Ensure one completed action cannot issue the same reward multiple times.

Validate combat and interaction according to the mechanic, including range, cooldowns, resources, hit plausibility, and line of sight where applicable. Account for latency without granting unlimited client authority. Do not treat network ownership of a character or vehicle as proof that its reported motion is legitimate.

Balance responsive vehicle physics with server checks on ownership, entry, exit, consequential collisions, and implausible movement. Use tolerances supported by observed behaviour and latency; do not punish players based on a single noisy signal.

Keep economy and progression rules central, configurable where useful, and consistent across earning and spending paths. Make meaningful transactions safe against duplication, race conditions, reconnects, and partial failure. Protect administrative and debugging capabilities with explicit server-side access checks and keep development shortcuts out of production gameplay.

### Persistence

Use server-side persistence with validated schemas, explicit defaults, and a versioning or migration approach when saved data evolves. Account for service limits, concurrent sessions, retries, shutdown, and partial failures. Select concurrency and session protection appropriate to the actual persistence design.

Never interpret a failed data load as confirmed absence and then overwrite existing player data with defaults. Avoid uncontrolled writes and retry loops. Give players and developers appropriate feedback when progress cannot be safely loaded or saved. Keep development data isolated from production data where the workflow permits.

## 8. Performance and Cross-Platform Requirements

Support balanced performance and usability across modern mobile devices, tablets, and PCs. Preserve attractive visuals while controlling resource costs. Do not optimise exclusively for extremely low-end hardware or assume desktop performance represents the mobile experience.

Establish measurable performance budgets as representative gameplay and target devices become available. Record the tested device or environment, scene, player count, and relevant conditions. Do not invent universal frame-rate guarantees, asset limits, or supported player counts before measuring the game.

- **Geometry and rendering:** Evaluate visible triangles, instance counts, draw calls, transparency, shadows, and material variation together. Use simpler distant content and available level-of-detail controls when beneficial. Avoid excessive small parts and invisible decorative geometry.
- **Meshes and textures:** Reuse mesh and texture content, choose resolution for actual on-screen size, and avoid unnecessary unique high-resolution maps. Track memory and asset loading costs as content grows.
- **Collisions:** Prefer simple collision shapes and deliberate collision groups. Disable collision, touch, or query participation only where those capabilities are genuinely unnecessary. Keep gameplay raycasts and navigation behaviour correct.
- **Lighting and effects:** Control shadow-casting lights, overlapping transparency, particle counts, post-processing, and effect lifetimes. Evaluate visual quality and GPU cost on representative devices and provide sensible quality scaling where useful.
- **Streaming:** Plan for Roblox instance streaming in the continuous world. Make client logic tolerate content arriving and leaving, use appropriate model streaming behaviour for interactive locations, and limit content forced to remain loaded. Exercise fast travel by vehicle and transitions between dense areas.
- **Physics:** Keep static scenery anchored, limit active assemblies and constraints, and manage network ownership intentionally. Clean up abandoned vehicles and temporary physical objects through defined lifecycles.
- **Scripts and memory:** Profile expensive loops, allocation, connection counts, retained objects, and long sessions. Schedule or scope background work according to actual needs and avoid accumulating work per player or per district indefinitely.
- **Networking:** Replicate only necessary state, scope audiences where possible, and control update rates and payload sizes. Avoid per-frame remotes and redundant broadcasts. Use bounded client effects for presentation where authority is unnecessary.
- **Input and UI:** Support touch, keyboard, and mouse with appropriate controls, readable text, safe screen placement, and usable interaction targets. Handle screen sizes and orientations deliberately. Consider gamepad support when relevant to the feature and agreed device scope.

Use Roblox profiling tools and real measurements to identify bottlenecks. Combine frame-time, memory, physics, script, and network observations with representative gameplay. Record emulator limitations and perform physical device checks when available; a simulated viewport does not prove device performance. Re-profile meaningful performance changes and check for regressions in visual quality and gameplay.

## 9. Testing, Debugging, and Quality Assurance

Choose validation appropriate to each implementation. Test small increments during development and verify integration before declaring completion. Use automated tests for stable logic and meaningful regressions where they provide value; use Studio playtests and visual inspection for interactions and assets that need them. Avoid tests that merely repeat implementation details.

As applicable to the changed feature, verify:

- The intended player flow, failure paths, repeated use, and recovery from interruption.
- Multiplayer behaviour with multiple clients, including contention for the same object, late joining, leaving, death, and respawning.
- Server rejection of malformed, excessive, unauthorised, duplicated, and impossible requests.
- Persistence success and failure behaviour, reconnects, migrations, and prevention of accidental data loss.
- Touch controls, keyboard and mouse input, representative screen sizes, UI legibility, and accessibility needs such as non-colour status cues.
- Streaming boundaries, vehicles moving through the world, missing or unloaded objects, collisions, and landmark or interior navigation.
- Relevant performance under representative content and player activity, including resource cleanup after repeated actions.
- Existing gameplay paths that could reasonably be affected by the change.

Use contextual logs and diagnostics that help reproduce failures. Avoid noisy output, exposed sensitive data, and silent error suppression. Treat reproducible errors and warnings as issues to investigate; do not claim clean execution while ignoring relevant output.

When a test fails, investigate, fix the cause, and rerun the relevant checks. When validation cannot be performed, state exactly what was checked, what remains unverified, and why. Never substitute code inspection or a successful import for a claimed multiplayer, visual, or performance test.

## 10. Open-Source Dependencies and Licensing

Adopt a dependency or external asset only when it solves a concrete need and its maintenance, compatibility, security, performance, and licensing are acceptable. Prefer a small, understandable dependency set; do not install frameworks as a default starting step.

Check the actual licence and source terms before integrating code, meshes, textures, audio, fonts, animations, or generated assets. Confirm that the intended Roblox use and distribution are permitted and preserve required notices and attribution. Public availability or a free download does not establish permission.

Inspect third-party Roblox models and plugins for unexpected scripts, remote loading, hidden dependencies, and unnecessary capabilities before use. Remove or reject untrusted behaviour. Do not import proprietary Jailbreak or Mad City content or assets with unclear provenance.

Track adopted dependencies and asset provenance in the project's documentation once they exist. Record source, version or revision where applicable, licence, required attribution, and meaningful local changes. Preserve reproducibility without committing secrets or unnecessary generated files.

## 11. Documentation and Development Continuity

Keep documentation proportionate to the systems that actually exist. Record important architectural choices, tool requirements, synchronisation ownership, setup steps, configuration, asset conventions, and known limitations when they become relevant. Do not present proposed choices as established infrastructure.

Preserve enough context for a future Codex session to continue safely: identify completed work, outstanding defects, verification performed, and any concrete next action already agreed with the user. Document non-obvious invariants, remote contracts, data schemas, and migrations alongside their systems or in an appropriate project reference.

Use clear identifiers and names so code, Studio objects, source assets, and documentation can be related. Update relevant instructions when a decision changes, and remove misleading obsolete guidance. Do not create duplicate sources of truth or extensive documents that merely restate code.

Keep this file focused on enduring project instructions. Put task-specific plans, experimental findings, and temporary work notes in an appropriate location only when useful and authorised by the active task. Never store credentials, access tokens, or private user data in project documentation.

## 12. Definition of Done for Implementation Tasks

An implementation task is complete when all applicable conditions are met:

- The requested behaviour or asset is implemented, integrated, and usable in its intended context, with no undisclosed placeholders or unfinished dependencies.
- The result follows the agreed creative direction, Indian setting, visual standards, and relevant architectural conventions.
- Multiplayer authority, remote validation, transaction integrity, and persistence behaviour are addressed where the feature requires them.
- Relevant input methods, screen sizes, streaming behaviour, lifecycle cleanup, and error paths are handled.
- Appropriate functional, multiplayer, visual, and performance checks have been performed for the scope of the change, with results reported accurately.
- Regressions identified during validation are resolved, and remaining limitations or blocked checks are explicitly disclosed.
- Third-party assets and dependencies have suitable licences, provenance, and required attribution.
- Necessary source assets, configurations, and concise maintenance documentation are included through the established workflow.
- The user receives a clear account of what changed, how it was verified, and any material issue requiring creative direction or external action.

If a necessary tool or external condition prevents completion, report the completed portion and the precise remaining requirement. Do not describe the whole task as done. Apply this definition proportionately to implementation work; honour narrower instructions for documentation, investigation, or other explicitly limited tasks.
