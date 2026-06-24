# Copyright © 2026 Anika Mukherjee
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import os
import subprocess
import sys
import urllib.request
import random
import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import typer
import questionary
import pyperclip
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich import print as rprint

app = typer.Typer(help="IRL Wisdom™ — ancient lessons for modern life.")
console = Console(highlight=False)

ACCENT_BRIGHT = "#F29265"
CREAM = "#D7C0AA"
MUTED = "#614B39"
BORDER = "#6B4E36"
SELECTED = "#3478F6"

DATA_DIR = Path(__file__).parent / "data"
CONFIG_FILE = Path.home() / ".irl_wisdom_config.json"

try:
    VERSION = version("irl-wisdom")
except PackageNotFoundError:
    VERSION = "dev"


def menu_style():
    """Shared prompt styling for a consistent command-palette feel."""
    return questionary.Style([
        ("qmark", f"fg:{ACCENT_BRIGHT} bold"),
        ("question", f"fg:{CREAM} bold"),
        ("answer", f"fg:{ACCENT_BRIGHT} bold"),
        ("pointer", "fg:#9CBFFF bold"),
        ("highlighted", f"bg:{SELECTED} fg:#FFFFFF bold"),
        ("selected", f"fg:{CREAM}"),
        ("instruction", f"fg:{MUTED}"),
    ])

def command_choice(command, description, value):
    """Pad command rows so the blue selection bar spans the palette."""
    width = max(48, console.width - 4)
    label = f"/{command:<11}{description}"
    return questionary.Choice(label.ljust(width), value=value)


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"favorites": [], "streak_date": "", "streak_count": 0}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def load_data(filename):
    path = DATA_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

datasets = {
    "wisdom": load_data("wisdom.json"),
    "moai": load_data("moai.json"),
    "power": load_data("48laws.json"),
    "facts": load_data("facts.json"),
    "mental_models": load_data("mental_models.json"),
    "biases": load_data("biases.json"),
    "discipline": load_data("discipline.json"),
}

def get_random_item(array):
    return random.choice(array) if array else None

def get_daily_item(array):
    if not array: return None
    now = datetime.datetime.now()
    day_of_year = now.timetuple().tm_yday
    return array[day_of_year % len(array)]

def handle_direct_command(text, copy):
    if copy:
        pyperclip.copy(text)
        rprint(f"[{ACCENT_BRIGHT}]• Copied to clipboard[/{ACCENT_BRIGHT}]")

def handle_copy_and_save(text, raw_data):
    action = questionary.select(
        "/",
        choices=[
            command_choice("copy", "Copy this to your clipboard", "copy"),
            command_choice("save", "Add this to your favorites", "save"),
            command_choice("back", "Return to the command palette", "menu"),
            command_choice("exit", "Leave IRL Wisdom™", "exit"),
        ],
        style=menu_style(),
        qmark="",
        instruction="(↑/↓ to move • enter to select)",
    ).ask()

    if action is None or action == "exit":
        raise typer.Exit()
    if action == "copy":
        pyperclip.copy(text)
        rprint(f"[{ACCENT_BRIGHT}]• Copied to clipboard[/{ACCENT_BRIGHT}]")
        return handle_copy_and_save(text, raw_data)
    if action == "save":
        config = load_config()
        config["favorites"].append(raw_data)
        save_config(config)
        rprint(f"[{ACCENT_BRIGHT}]• Saved to favorites[/{ACCENT_BRIGHT}]")
        return handle_copy_and_save(text, raw_data)
    run_interactive_menu()


def print_header():
    console.clear()

    title_file = DATA_DIR / "title.ansi"
    if title_file.exists():
        with open(title_file, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            visible = [line for line in lines if line.strip()]
            min_spaces = min((len(line) - len(line.lstrip())) for line in visible)
            left_aligned = "\n".join(line[min_spaces:] for line in lines)
            title_renderable = Text.from_ansi(left_aligned)
    else:
        title_renderable = Text("IRL WISDOM", style=f"bold {ACCENT_BRIGHT}")

    config = load_config()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    streak_date = config.get("streak_date")
    streak_count = config.get("streak_count", 0)

    if streak_date != today:
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        streak_count = streak_count + 1 if streak_date == yesterday else 1
        config.update(streak_date=today, streak_count=streak_count)
        save_config(config)

    console.print(title_renderable)
    console.print(Text("✦  Ancient lessons. Modern life. Better choices.  ✦", style=CREAM))
    console.print()

    stats_text = (
        f"[{MUTED}]Streak     [/{MUTED}][{ACCENT_BRIGHT}]{streak_count} days[/{ACCENT_BRIGHT}]\n"
        f"[{MUTED}]Favorites  [/{MUTED}][{CREAM}]{len(config.get('favorites', []))} saved[/{CREAM}]\n"
        f"[{MUTED}]Today      [/{MUTED}][{CREAM}]{today}[/{CREAM}]"
    )
    console.print(Panel(
        stats_text,
        border_style=BORDER,
        box=box.SQUARE,
        expand=True,
        width=min(74, max(48, console.width - 2)),
        padding=(0, 1),
    ))

    status = Text()
    status.append("● ", style=ACCENT_BRIGHT)
    status.append("wisdom    ", style=MUTED)
    status.append("Ready — choose a command below", style=CREAM)
    console.print(status)

    version_line = Text("IRL Wisdom™ ", style=MUTED)
    version_line.append(f"v{VERSION}", style=f"bold {ACCENT_BRIGHT}")
    console.print(version_line)
    console.print()


@app.command()
def daily(copy: bool = typer.Option(False, "--copy", "-c", help="Copy output to clipboard")):
    """Get your daily dose of wisdom"""
    item = get_daily_item(datasets["wisdom"])
    print_cinematic(item, title="Daily Wisdom", color="cyan")
    handle_direct_command(item, copy)

@app.command()
def moai(copy: bool = typer.Option(False, "--copy", "-c")):
    """Get some solid moai vibes 🗿"""
    item = get_random_item(datasets["moai"])
    print_cinematic(item, title="Moai Vibes 🗿", color="white")
    handle_direct_command(item, copy)

def format_power_law(item):
    """Create a portable plain-text version for copy and favorites."""
    return (
        f"{item['law']}\n\n"
        f"PLAINLY\n{item['description']}\n\n"
        f"MOAI WAY\n{item['moai']}"
    )


def print_power_law(item):
    """Render a power law as a short, friendly Moai lesson."""
    lesson = Text()
    lesson.append(item["law"], style=f"bold {ACCENT_BRIGHT}")
    lesson.append("\n\nPLAINLY\n", style=f"bold {MUTED}")
    lesson.append(item["description"], style=CREAM)
    lesson.append("\n\n🗿 MOAI WAY\n", style=f"bold {ACCENT_BRIGHT}")
    lesson.append(item["moai"], style=CREAM)
    console.print(Panel(
        lesson,
        title=f"[{ACCENT_BRIGHT}] Power, Simplified [/{ACCENT_BRIGHT}]",
        title_align="left",
        border_style=BORDER,
        box=box.SQUARE,
        padding=(1, 2),
    ))
    console.print()


@app.command()
def power(copy: bool = typer.Option(False, "--copy", "-c")):
    """Learn a law in plain English, the Moai way."""
    item = get_random_item(datasets["power"])
    print_power_law(item)
    handle_direct_command(format_power_law(item), copy)

@app.command()
def fact(copy: bool = typer.Option(False, "--copy", "-c")):
    """Get a powerful fact"""
    item = get_random_item(datasets["facts"])
    print_cinematic(item, title="Powerful Fact", color="yellow")
    handle_direct_command(item, copy)

@app.command()
def models(copy: bool = typer.Option(False, "--copy", "-c")):
    """Learn a mental model"""
    item = get_random_item(datasets["mental_models"])
    text = f"{item['name']}\n\n{item['description']}"
    copy_text = f"{item['name']}: {item['description']}"
    print_cinematic(text, title="Mental Model", color="blue")
    handle_direct_command(copy_text, copy)

@app.command()
def biases(copy: bool = typer.Option(False, "--copy", "-c")):
    """Learn a cognitive bias"""
    item = get_random_item(datasets["biases"])
    text = f"{item['name']}\n\n{item['description']}"
    copy_text = f"{item['name']}: {item['description']}"
    print_cinematic(text, title="Cognitive Bias", color="magenta")
    handle_direct_command(copy_text, copy)

@app.command()
def discipline(copy: bool = typer.Option(False, "--copy", "-c")):
    """Stay hard."""
    item = get_random_item(datasets["discipline"])
    print_cinematic(item, title="Discipline", color="white")
    handle_direct_command(item, copy)

# Hidden commands: absent from --help, but waiting for curious humans.
@app.command(name="42", hidden=True)
def answer_to_everything():
    """The answer, naturally."""
    print_cinematic(
        "42. The harder part was asking the right question.",
        title="Mostly Harmless",
        color="green",
    )


@app.command(hidden=True)
def oracle():
    """Consult the extremely unofficial oracle."""
    prophecies = [
        "The tab you keep avoiding contains the answer.",
        "A small decision today will become an excellent story later.",
        "Your future self requests water and one finished task.",
        "The bug is not where you are looking. It is one function above.",
        "Proceed. The path only appears after the first awkward step.",
    ]
    print_cinematic(get_random_item(prophecies), title="The Oracle Whispers", color="magenta")


@app.command(hidden=True)
def zen():
    """A tiny terminal koan."""
    print_cinematic(
        "Before enlightenment: fix the bug.\nAfter enlightenment: fix the bug.",
        title="Terminal Koan",
        color="white",
    )


@app.command(hidden=True)
def flip():
    """Let fate choose."""
    result = random.choice(("HEADS — begin.", "TAILS — begin anyway."))
    print_cinematic(result, title="The Coin Has Spoken", color="yellow")


@app.command(hidden=True)
def matrix():
    """A glitch in the wisdom."""
    print_cinematic(
        "Wake up.\nThe comfortable assumption has you.\nFollow the uncomfortable question.",
        title="SIGNAL FOUND",
        color="green",
    )


@app.command(hidden=True)
def whoami():
    """Identity is complicated."""
    print_cinematic(
        "A work in progress with root access to exactly one life.",
        title="Identity",
        color="cyan",
    )


@app.command(hidden=True)
def midnight():
    """Different wisdom for different hours."""
    hour = datetime.datetime.now().hour
    if hour < 5:
        message = "The night is honest, but sleep is also wisdom."
    elif hour < 12:
        message = "Begin before your doubts finish loading."
    elif hour < 18:
        message = "The day is half-written. Edit boldly."
    else:
        message = "Close one loop before opening another."
    print_cinematic(message, title="After Hours", color="blue")


@app.command(hidden=True)
def egg():
    """You found the least hidden hidden thing."""
    print_cinematic(
        "You found an egg. +1 curiosity. No achievements were harmed.",
        title="Secret Unlocked",
        color="yellow",
    )


def version_tuple(value):
    """Turn a normal release number into a comparable integer tuple."""
    try:
        return tuple(int(part) for part in value.split("."))
    except ValueError:
        return (0,)


def latest_pypi_version():
    """Return the latest published version without adding a new dependency."""
    request = urllib.request.Request(
        "https://pypi.org/pypi/irl-wisdom/json",
        headers={"User-Agent": f"IRL-Wisdom/{VERSION}"},
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        return json.load(response)["info"]["version"]


def launch_upgrade_helper(target_version):
    """Upgrade after this process exits so Windows can release the CLI launcher."""
    pip_command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "--disable-pip-version-check",
        f"irl-wisdom=={target_version}",
    ]
    helper = (
        "import subprocess, sys, time; "
        "time.sleep(1.5); "
        "raise SystemExit(subprocess.call(sys.argv[1:]))"
    )
    creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    subprocess.Popen(
        [sys.executable, "-c", helper, *pip_command],
        creationflags=creation_flags,
    )


@app.command()
def upgrade(
    yes: bool = typer.Option(False, "--yes", "-y", help="Upgrade without confirmation"),
):
    """Ask the Moai to upgrade IRL Wisdom™."""
    print_cinematic(
        "The stone remembers. The package evolves.",
        title="Moai Upgrade Ritual",
        color="white",
    )

    try:
        latest = latest_pypi_version()
    except Exception:
        rprint(
            f"[{CREAM}]The Moai cannot see PyPI through the mist. "
            f"Check your connection and try again.[/{CREAM}]"
        )
        raise typer.Exit(code=1)

    if version_tuple(latest) <= version_tuple(VERSION):
        rprint(
            f"[{ACCENT_BRIGHT}]🗿 Peak stillness achieved.[/{ACCENT_BRIGHT}] "
            f"[{CREAM}]IRL Wisdom™ v{VERSION} is already current.[/{CREAM}]"
        )
        return

    rprint(
        f"[{MUTED}]Current stone  [/{MUTED}][{CREAM}]v{VERSION}[/{CREAM}]\n"
        f"[{MUTED}]New monolith  [/{MUTED}][{ACCENT_BRIGHT}]v{latest}[/{ACCENT_BRIGHT}]"
    )
    approved = yes or questionary.confirm(
        "Roll the new stone into place?",
        default=True,
        style=menu_style(),
        qmark="🗿",
    ).ask()
    if not approved:
        rprint(f"[{MUTED}]The Moai waits. No files were changed.[/{MUTED}]")
        return

    launch_upgrade_helper(latest)
    rprint(
        f"[{ACCENT_BRIGHT}]🗿 Upgrade entrusted to the stone.[/{ACCENT_BRIGHT}]\n"
        f"[{CREAM}]This CLI will close; pip will install v{latest} in a moment.[/{CREAM}]"
    )
    raise typer.Exit()


def show_favorites():
    config = load_config()
    favorites = config.get("favorites", [])
    if not favorites:
        rprint(f"[{CREAM}]No favorites saved yet.[/{CREAM}]")
    else:
        for index, favorite in enumerate(favorites, start=1):
            first_line = favorite["text"].splitlines()[0]
            rprint(
                f"[{ACCENT_BRIGHT}][{index}] {favorite['type'].upper()}:[/{ACCENT_BRIGHT}] "
                f"[{CREAM}]{first_line}[/{CREAM}]"
            )

    action = questionary.select(
        "/",
        choices=["/clear      Clear favorites", "/back       Return to menu"],
        style=menu_style(),
        qmark="",
    ).ask()

    if action and action.startswith("/clear"):
        config["favorites"] = []
        save_config(config)
        rprint(f"[bold {ACCENT_BRIGHT}]• Favorites cleared[/bold {ACCENT_BRIGHT}]")
    run_interactive_menu()


def print_cinematic(text, title, color):
    styled_text = Text(text, style=CREAM)
    console.print(Panel(
        styled_text,
        title=f"[{ACCENT_BRIGHT}] {title} [/{ACCENT_BRIGHT}]",
        title_align="left",
        border_style=BORDER,
        box=box.SQUARE,
        padding=(1, 2),
    ))
    console.print()


@app.callback(invoke_without_command=True)
def interactive_menu(ctx: typer.Context):
    """Open the interactive command palette."""
    if ctx.invoked_subcommand is None:
        run_interactive_menu()


def run_interactive_menu():
    print_header()

    answer = questionary.select(
        "/",
        choices=[
            command_choice("daily", "Start with today's piece of wisdom", "daily"),
            command_choice("moai", "Get a dose of unshakable perspective", "moai"),
            command_choice("power", "Study one of the 48 laws of power", "power"),
            command_choice("models", "Add a mental model to your toolkit", "models"),
            command_choice("biases", "Catch a cognitive bias in the wild", "biases"),
            command_choice("discipline", "Build resolve for the work ahead", "discipline"),
            command_choice("fact", "Learn one surprisingly useful fact", "fact"),
            command_choice("upgrade", "Ask the Moai to upgrade the CLI", "upgrade"),
            command_choice("favorites", "Revisit the ideas you kept", "favorites"),
            command_choice("exit", "Leave IRL Wisdom™", "exit"),
        ],
        style=menu_style(),
        qmark="",
        instruction="(↑/↓ to move • enter to select)",
    ).ask()

    if answer is None:
        raise typer.Exit()

    if answer == "daily":
        item = get_daily_item(datasets["wisdom"])
        print_cinematic(item, title="Daily Wisdom", color="cyan")
        handle_copy_and_save(item, {"type": "wisdom", "text": item})
    elif answer == "moai":
        item = get_random_item(datasets["moai"])
        print_cinematic(item, title="Moai Vibes 🗿", color="white")
        handle_copy_and_save(item, {"type": "moai", "text": item})
    elif answer == "power":
        item = get_random_item(datasets["power"])
        copy_text = format_power_law(item)
        print_power_law(item)
        handle_copy_and_save(copy_text, {"type": "power", "text": copy_text})
    elif answer == "models":
        item = get_random_item(datasets["mental_models"])
        text = f"{item['name']}\n\n{item['description']}"
        copy_text = f"{item['name']}: {item['description']}"
        print_cinematic(text, title="Mental Model", color="blue")
        handle_copy_and_save(copy_text, {"type": "mental_model", "text": copy_text})
    elif answer == "biases":
        item = get_random_item(datasets["biases"])
        text = f"{item['name']}\n\n{item['description']}"
        copy_text = f"{item['name']}: {item['description']}"
        print_cinematic(text, title="Cognitive Bias", color="magenta")
        handle_copy_and_save(copy_text, {"type": "bias", "text": copy_text})
    elif answer == "discipline":
        item = get_random_item(datasets["discipline"])
        print_cinematic(item, title="Discipline", color="white")
        handle_copy_and_save(item, {"type": "discipline", "text": item})
    elif answer == "fact":
        item = get_random_item(datasets["facts"])
        print_cinematic(item, title="Powerful Fact", color="yellow")
        handle_copy_and_save(item, {"type": "fact", "text": item})
    elif answer == "upgrade":
        upgrade()
    elif answer == "favorites":
        show_favorites()
    elif answer == "exit":
        raise typer.Exit()

if __name__ == "__main__":
    app()
