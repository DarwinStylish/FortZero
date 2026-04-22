"""Terminal shell boot flow for PR8."""

from __future__ import annotations

import logging

from fortzero.content.campaign_loader import CampaignLoader
from fortzero.content.models import CampaignDefinition, MissionDefinition
from fortzero.core.bootstrap import BootstrapContext
from fortzero.events.bus import EventBus
from fortzero.events.event_log import EventLogger
from fortzero.events.models import DomainEvent, EventTypes
from fortzero.mission.orchestrator import MissionOrchestrator
from fortzero.narrative.narrative_engine import NarrativeEngine
from fortzero.profile.service import ProfileService
from fortzero.session.service import SessionService
from fortzero.shell.banner import render_banner
from fortzero.state.state_manager import StateManager


def print_separator() -> None:
    print("-" * 72)


def prompt_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty.")


def prompt_mode(default: str = "agent") -> str:
    while True:
        raw = input(f"Preferred mode [agent/spectre] (default: {default}): ").strip().lower()
        if not raw:
            return default
        if raw in {"agent", "spectre"}:
            return raw
        print("Invalid mode. Enter 'agent' or 'spectre'.")


def render_header(context: BootstrapContext) -> None:
    print(render_banner())
    print(f"App: {context.config.app.name}")
    print(f"Environment: {context.config.app.env}")
    print(f"Offline mode: {context.config.app.offline_mode}")
    print()


def choose_profile() -> str:
    while True:
        print_separator()
        print("PROFILE ACCESS")
        print("1. Create new profile")
        print("2. Load existing profile")
        print("3. Exit")
        choice = input("Select option: ").strip()

        if choice == "1":
            return "create"
        if choice == "2":
            return "load"
        if choice == "3":
            return "exit"

        print("Invalid option.")


def create_profile_flow(profile_service: ProfileService) -> str:
    print_separator()
    print("CREATE PROFILE")
    alias = prompt_non_empty("Enter operator alias: ")
    mode = prompt_mode()

    profile = profile_service.create_profile(alias=alias, preferred_mode=mode)
    print(f"Profile created for operator: {profile.alias}")
    return profile.alias


def load_profile_flow(profile_service: ProfileService) -> str | None:
    profiles = profile_service.list_profiles()

    print_separator()
    print("LOAD PROFILE")

    if not profiles:
        print("No profiles found.")
        return None

    for index, profile in enumerate(profiles, start=1):
        print(
            f"{index}. {profile.alias} | "
            f"preferred_mode={profile.preferred_mode} | "
            f"last_opened_at={profile.last_opened_at}"
        )

    raw = input("Select profile number: ").strip()
    if not raw.isdigit():
        print("Invalid selection.")
        return None

    selected = int(raw)
    if selected < 1 or selected > len(profiles):
        print("Selection out of range.")
        return None

    return profiles[selected - 1].alias


def choose_campaign(
    campaign_loader: CampaignLoader,
    context: BootstrapContext,
) -> tuple[CampaignDefinition, list[MissionDefinition]] | None:
    campaigns_root = context.paths.content_dir / "campaigns"
    loaded = campaign_loader.discover_campaigns(campaigns_root)

    print_separator()
    print("CAMPAIGNS")

    if not loaded:
        print("No campaigns available.")
        return None

    for index, (campaign, missions) in enumerate(loaded, start=1):
        print(f"{index}. {campaign.title} ({campaign.id})")
        print(f"   {campaign.description}")
        print(f"   Missions: {len(missions)}")

    raw = input("Select campaign number (or press Enter to go back): ").strip()
    if not raw:
        return None

    if not raw.isdigit():
        print("Invalid selection.")
        return None

    selected = int(raw)
    if selected < 1 or selected > len(loaded):
        print("Selection out of range.")
        return None

    return loaded[selected - 1]


def print_world_state_summary(state_manager: StateManager, profile_alias: str) -> None:
    world_state = state_manager.world_service.load(profile_alias)

    print_separator()
    print("WORLD STATE")
    print(f"Completed missions: {', '.join(world_state.completed_missions) or 'None'}")
    print(f"Unlocked missions: {', '.join(world_state.unlocked_missions) or 'None'}")
    print(f"Discovered intel: {', '.join(world_state.discovered_intel) or 'None'}")
    print(f"Acquired access: {', '.join(world_state.acquired_access) or 'None'}")


def run_mission_flow(
    profile_alias: str,
    preferred_mode: str,
    campaign: CampaignDefinition,
    missions: list[MissionDefinition],
    orchestrator: MissionOrchestrator,
    narrative_engine: NarrativeEngine,
    event_bus: EventBus,
    session_id: int,
    state_manager: StateManager,
) -> None:
    print_separator()
    print(f"CAMPAIGN: {campaign.title}")
    print(campaign.description)
    print("MISSIONS:")

    launch_contexts = [orchestrator.launch_context(profile_alias, mission) for mission in missions]

    for index, context in enumerate(launch_contexts, start=1):
        availability = "AVAILABLE" if context.available else f"LOCKED: {context.reason}"
        print(f"{index}. {context.mission.title} [{context.mission.id}] - {availability}")

    raw = input("Select mission number (or press Enter to go back): ").strip()
    if not raw:
        return

    if not raw.isdigit():
        print("Invalid selection.")
        return

    selected = int(raw)
    if selected < 1 or selected > len(launch_contexts):
        print("Selection out of range.")
        return

    launch = launch_contexts[selected - 1]
    mission = launch.mission

    if not launch.available:
        event_bus.publish(
            DomainEvent(
                event_type=EventTypes.MISSION_BLOCKED,
                source="shell.mission_select",
                profile_alias=profile_alias,
                mission_id=mission.id,
                session_id=session_id,
                payload={"reason": launch.reason},
            )
        )
        print(f"Mission blocked: {launch.reason}")
        return

    run_id, run_state = orchestrator.start_run(profile_alias, mission)

    narrative_engine.render_mission_intro(mission, preferred_mode)

    print_separator()
    print(f"MISSION STARTED: {mission.title}")
    print(f"Mission ID: {mission.id}")
    print("Objectives:")

    while True:
        for index, objective in enumerate(run_state.objectives, start=1):
            status = "DONE" if objective.completed else "OPEN"
            optional = "OPTIONAL" if objective.optional else "REQUIRED"
            print(f"{index}. [{status}] [{optional}] {objective.title} - {objective.description}")

        print()
        print("Mission Actions")
        print("1. Mark objective complete")
        print("2. Finish mission check")
        print("3. Abort to menu")

        action = input("Select option: ").strip()

        if action == "1":
            raw_obj = input("Select objective number: ").strip()
            if not raw_obj.isdigit():
                print("Invalid objective selection.")
                continue

            obj_index = int(raw_obj)
            if obj_index < 1 or obj_index > len(run_state.objectives):
                print("Objective selection out of range.")
                continue

            objective = run_state.objectives[obj_index - 1]
            changed = orchestrator.complete_objective(run_id, run_state, objective.id)
            if changed:
                print(f"Objective completed: {objective.title}")
            else:
                print("Objective could not be completed.")
        elif action == "2":
            completed = orchestrator.finalize_if_complete(run_id, run_state)
            if completed:
                print("Mission completed successfully.")
                print_world_state_summary(state_manager, profile_alias)
                return
            print("Required objectives are still incomplete.")
        elif action == "3":
            print("Returning to menu without completing mission.")
            return
        else:
            print("Invalid option.")

        print_separator()


def run_main_menu(
    alias: str,
    preferred_mode: str,
    event_bus: EventBus,
    session_id: int,
    campaign_loader: CampaignLoader,
    orchestrator: MissionOrchestrator,
    narrative_engine: NarrativeEngine,
    state_manager: StateManager,
    context: BootstrapContext,
) -> None:
    event_bus.publish(
        DomainEvent(
            event_type=EventTypes.MENU_OPENED,
            source="shell.main_menu",
            profile_alias=alias,
            session_id=session_id,
            payload={"preferred_mode": preferred_mode},
        )
    )

    while True:
        print_separator()
        print(f"OPERATOR: {alias}")
        print(f"Preferred mode: {preferred_mode}")
        print()
        print("MAIN MENU")
        print("1. Campaigns")
        print("2. Reports")
        print("3. Settings")
        print("4. Exit")
        choice = input("Select option: ").strip()

        event_bus.publish(
            DomainEvent(
                event_type=EventTypes.MENU_SELECTED,
                source="shell.main_menu",
                profile_alias=alias,
                session_id=session_id,
                payload={"selection": choice},
            )
        )

        if choice == "1":
            selection = choose_campaign(campaign_loader, context)
            if selection is not None:
                campaign, missions = selection
                run_mission_flow(
                    alias,
                    preferred_mode,
                    campaign,
                    missions,
                    orchestrator,
                    narrative_engine,
                    event_bus,
                    session_id,
                    state_manager,
                )
        elif choice == "2":
            print_separator()
            print("REPORTS")
            print("No reports available yet.")
        elif choice == "3":
            print_separator()
            print("SETTINGS")
            print("Settings UI arrives in a later PR. Preferred mode is stored in profile.")
        elif choice == "4":
            print("Exiting FortZero shell.")
            return
        else:
            print("Invalid option.")


def run_shell(context: BootstrapContext, logger: logging.Logger) -> int:
    render_header(context)

    event_bus = EventBus()
    state_manager = StateManager(context.paths.db_file, event_bus=event_bus)
    profile_service = ProfileService(state_manager)
    session_service = SessionService(state_manager)
    campaign_loader = CampaignLoader()
    orchestrator = MissionOrchestrator(
        event_bus,
        state_manager.mission_run_repository,
        state_manager.world_service,
    )
    narrative_engine = NarrativeEngine(context.paths.content_dir)

    event_logger = EventLogger(state_manager.event_repository, logger)
    event_bus.subscribe_all(event_logger.handle)

    event_bus.publish(
        DomainEvent(
            event_type=EventTypes.APP_BOOTSTRAPPED,
            source="shell.run_shell",
            payload={"env": context.config.app.env, "offline_mode": context.config.app.offline_mode},
        )
    )

    while True:
        action = choose_profile()

        if action == "exit":
            event_bus.publish(
                DomainEvent(
                    event_type=EventTypes.USER_EXITED,
                    source="shell.profile_access",
                    payload={"stage": "pre_session"},
                )
            )
            logger.info("User exited before session start")
            print("FortZero shutdown complete.")
            return 0

        if action == "create":
            alias = create_profile_flow(profile_service)
            event_bus.publish(
                DomainEvent(
                    event_type=EventTypes.PROFILE_CREATED,
                    source="shell.profile_access",
                    profile_alias=alias,
                    payload={"action": "create"},
                )
            )
        else:
            alias = load_profile_flow(profile_service)
            if alias is None:
                continue

        try:
            profile = profile_service.load_profile(alias)
        except RuntimeError as exc:
            logger.error("Failed to load profile: %s", exc)
            print(f"Profile error: {exc}")
            continue

        event_bus.publish(
            DomainEvent(
                event_type=EventTypes.PROFILE_LOADED,
                source="shell.profile_access",
                profile_alias=profile.alias,
                payload={"preferred_mode": profile.preferred_mode},
            )
        )

        session = session_service.start(profile)

        event_bus.publish(
            DomainEvent(
                event_type=EventTypes.SESSION_STARTED,
                source="shell.session",
                profile_alias=session.profile.alias,
                session_id=session.session_id,
                payload={"preferred_mode": session.profile.preferred_mode},
            )
        )

        logger.info(
            "Session started for operator '%s' with session_id=%s",
            session.profile.alias,
            session.session_id,
        )

        print_separator()
        print(f"Session initialized for operator: {session.profile.alias}")
        run_main_menu(
            session.profile.alias,
            session.profile.preferred_mode,
            event_bus,
            session.session_id,
            campaign_loader,
            orchestrator,
            narrative_engine,
            state_manager,
            context,
        )
        session_service.end(session)

        event_bus.publish(
            DomainEvent(
                event_type=EventTypes.SESSION_ENDED,
                source="shell.session",
                profile_alias=session.profile.alias,
                session_id=session.session_id,
                payload={"active": session.active},
            )
        )

        logger.info(
            "Session ended for operator '%s' with session_id=%s",
            session.profile.alias,
            session.session_id,
        )
        print("Returning to profile access.")
