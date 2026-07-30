# Citizen Compass – Phase 2 Vision and Technical Specification

## Project Vision

Citizen Compass is intended to become a continuously updated, authoritative Star Citizen information platform. The long-term goal is to maintain a living database that automatically synchronizes with publicly available game data whenever possible, reducing manual maintenance while improving data accuracy.

The platform should be designed so that future improvements require minimal restructuring, allowing new game content to be integrated as Star Citizen continues development.

---

# Primary Objectives

## 1. Automated Data Synchronization

Design an automated pipeline capable of collecting and updating Star Citizen information from approved or publicly available sources.

The synchronization system should:

* Detect newly released game data.
* Detect changes to existing game data.
* Preserve historical information where appropriate.
* Flag conflicting information for manual review.
* Update the Citizen Compass database automatically.
* Regenerate affected website pages without requiring manual editing.

The automation should be modular so additional data sources can be added over time.

---

# Phase 2 Website

The second phase transforms Citizen Compass from a searchable database into an interactive encyclopedia.

Each game object should become an interactive page rather than a static article.

Examples include:

* Ships
* Components
* Weapons
* Armor
* Clothing
* Paints
* Vehicles
* FPS weapons
* Attachments
* Commodities
* Missions
* Manufacturers

Each object should have a dedicated data model that can expand over time.

---

# Ship Viewer

Every ship should eventually include a fully interactive 3D model.

Desired capabilities include:

* Rotate
* Zoom
* Pan
* Toggle landing gear
* Toggle doors
* Toggle cargo ramps
* Toggle turrets
* Toggle component visibility
* Toggle interior visibility
* Highlight hardpoints
* Highlight weapon mounts
* Highlight missile racks
* Highlight shield generators
* Highlight power plants
* Highlight coolers
* Highlight quantum drives
* Highlight fuel tanks

Selecting a hardpoint should display:

* Component name
* Component size
* Compatible replacements
* Current statistics
* Manufacturer
* Description
* Gameplay notes

The viewer should be designed so additional interaction can be added later.

---

# Ship Paint Library

Citizen Compass should eventually contain a visual catalog of every ship paint available in Star Citizen.

Important design requirement:

The goal is not necessarily to redistribute original game assets.

Instead, the system should display a visual representation showing how each paint appears on the associated ship.

Each paint page should include:

* Paint name
* Manufacturer
* Compatible ships
* Release version
* Availability
* Preview images or rendered representations
* Color palette
* Finish description (matte, gloss, metallic, etc.)

If direct preview assets are unavailable, placeholder renders or community-authorized imagery may be used until better representations are available.

---

# Character Equipment Viewer

Citizen Compass should eventually provide a visual catalog for wearable equipment.

Supported categories include:

* Helmets
* Undersuits
* Chest armor
* Arms
* Legs
* Boots
* Gloves
* Clothing
* Jackets
* Hats
* Utility items
* Backpacks

The preferred implementation is a fully articulated character viewer.

However, if this is not initially possible, a static mannequin is an acceptable first milestone.

Possible implementation stages:

Stage 1

Static T-pose mannequin.

Stage 2

Multiple static poses.

Stage 3

Interactive rotatable character.

Stage 4

Animated character viewer.

The system architecture should allow upgrades without replacing the database structure.

---

# Asset Discovery

The project should investigate whether publicly accessible game resources or metadata contain references to:

* Meshes
* Materials
* Icons
* Texture references
* Equipment identifiers
* Paint identifiers
* Preview images
* Localization strings
* Component metadata

The goal is not to bypass game protections or obtain restricted assets.

Instead, the project should identify lawful, technically feasible methods of referencing or displaying information that is already publicly available or that can be generated independently.

If official preview assets are unavailable, the system should support placeholders until suitable representations can be created.

---

# Long-Term Architecture Goals

Citizen Compass should ultimately function as a structured knowledge platform rather than a collection of manually written pages.

Desired characteristics include:

* Automatically updated
* Highly searchable
* Modular
* Expandable
* Version-aware
* Cross-referenced
* Interactive
* Data-driven
* API-friendly
* AI-readable

Every entity in the database should have a unique identifier and be linked to related entities to support advanced search, recommendations, and future AI features.

---

# Guiding Principle

The project should favor sustainable automation and modular design over short-term manual solutions. Features should be implemented in stages, allowing placeholders where necessary while maintaining an architecture that supports richer interactive content as additional lawful data sources and visual representations become available.

---

# Development Philosophy

Citizen Compass is envisioned as a long-term project with ambitious end goals. It is understood from the outset that many of these goals cannot and should not be implemented immediately.

The project is intended to evolve through a series of well-defined milestones, where each completed stage serves as the foundation for the next. Every feature should be designed with future expansion in mind, even if its initial implementation is intentionally simple.

## Guiding Principles

### Build in Stages

Every major feature should be decomposed into achievable phases. The first implementation does not need to be the final implementation; it needs to establish a stable, extensible foundation.

Example progression:

* Collect the data.
* Organize and normalize the data.
* Store the data consistently.
* Display the data accurately.
* Add interactivity.
* Improve visual presentation.
* Automate updates.
* Optimize performance.
* Expand functionality.

Each phase should be independently functional while supporting the requirements of future phases.

### Architecture Before Features

Whenever practical, time should first be spent designing the system before implementing it.

This includes defining:

* Overall architecture
* Data structures
* Relationships between systems
* File organization
* Database schema
* Automation workflows
* Future expansion paths

A clear design reduces rework and allows new capabilities to be added with minimal disruption.

### Simplicity First

When multiple solutions are available, preference should be given to the one that is:

* Easier to understand
* Easier to maintain
* Easier to automate
* Easier to document
* Easier to extend

Complexity should only be introduced when it provides a meaningful long-term benefit.

### Think Beyond the Current Task

Development should not focus solely on the immediate objective. Every decision should consider how it will affect future features, integrations, and scalability.

Before implementing any significant feature, consider:

* Will this scale as the database grows?
* Can this process be automated later?
* Will future AI systems understand this structure?
* Does this create unnecessary technical debt?
* Can another developer continue the work with minimal explanation?

### Document Everything

Significant architectural decisions, assumptions, workflows, and implementation details should be documented as they are made.

Documentation is considered a core project asset rather than an afterthought. It should allow another developer—or another AI—to understand the project, continue development, or reconstruct the system with minimal loss of context.

## Long-Term Goal

The objective is not simply to build a website, but to create a sustainable knowledge platform whose architecture supports continuous growth. Each milestone should bring the project closer to that vision while remaining useful and stable on its own.
