"""Terminal shell boot flow for PR2."""

from __future__ import annotations

import logging

from fortzero.core.bootstrap import BootstrapContext
from fortzero.profile.service import ProfileService
from fortzero.profile.store import ProfileStore, ProfileStoreError
from fortzero.session.service import SessionService
from fortzero.shell.banner import render_banner


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


def run_main_menu(alias: str, preferred_mode: str) -> None:
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

        if choice == "1":
            print_separator()
            print("CAMPAIGNS")
            print("No campaigns available yet. Rootborne arrives in later PRs.")
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

    profile_store = ProfileStore(context.paths.profiles_dir)
    profile_service = ProfileService(profile_store)
    session_service = SessionService()

    while True:
        action = choose_profile()

        if action == "exit":
            logger.info("User exited before session start")
            print("FortZero shutdown complete.")
            return 0

        if action == "create":
            alias = create_profile_flow(profile_service)
        else:
            alias = load_profile_flow(profile_service)
            if alias is None:
                continue

        try:
            profile = profile_service.load_profile(alias)
        except ProfileStoreError as exc:
            logger.error("Failed to load profile: %s", exc)
            print(f"Profile error: {exc}")
            continue

        session = session_service.start(profile)
        logger.info("Session started for operator '%s'", session.profile.alias)

        print_separator()
        print(f"Session initialized for operator: {session.profile.alias}")
        run_main_menu(session.profile.alias, session.profile.preferred_mode)
        logger.info("Session ended for operator '%s'", session.profile.alias)
        print("Returning to profile access.")
