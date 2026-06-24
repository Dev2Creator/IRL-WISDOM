<div align="center">

# IRL Wisdom™ 🗿

### Ancient lessons. Modern life. Better choices.

A warm, keyboard-driven wisdom CLI for mental models, cognitive biases, power laws, discipline, memorable facts, and daily perspective.

[![PyPI](https://img.shields.io/pypi/v/irl-wisdom?style=flat-square&color=E47C55&label=PyPI)](https://pypi.org/project/irl-wisdom/)
[![Python](https://img.shields.io/pypi/pyversions/irl-wisdom?style=flat-square&color=D7C0AA)](https://pypi.org/project/irl-wisdom/)
[![License](https://img.shields.io/github/license/Dev2Creator/IRL-WISDOM?style=flat-square&color=614B39)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Dev2Creator/IRL-WISDOM?style=flat-square&color=3478F6)](https://github.com/Dev2Creator/IRL-WISDOM/stargazers)

[Install](#install) · [Explore](#what-is-inside) · [Commands](#commands) · [Upgrade](#the-moai-upgrade-ritual)

</div>

---

    ██╗ ██████╗  ██╗
    ██║ ██╔══██╗ ██║        IRL WISDOM™
    ██║ ██████╔╝ ██║        ─────────────
    ██║ ██╔══██╗ ██║        One thoughtful idea,
    ██║ ██║  ██║ ███████╗   right when you need it.
    ╚═╝ ╚═╝  ╚═╝ ╚══════╝

IRL Wisdom turns a terminal window into a small daily ritual. Open the command palette, choose a path, and leave with one useful thought—not another infinite feed.

## Install

    pip install --upgrade irl-wisdom

Then open the interactive experience:

    irl-wisdom

Use the arrow keys to move, press Enter to choose, and let the stone do the rest.

## What is inside

| Path | What you get |
|---|---|
| Daily wisdom | A deterministic thought for the day |
| Mental models | Better tools for reasoning and decisions |
| Cognitive biases | Names for the ways judgment goes sideways |
| 48 Laws of Power | One law, a plain-English explanation, and a Moai takeaway |
| Discipline | A short push when motivation wanders off |
| Powerful facts | Compact facts worth remembering |
| Moai vibes | Unshakable perspective, terminal-sized |
| Favorites | A personal collection stored on your machine |

The interface includes a daily streak, saved favorites, clipboard support, responsive terminal sizing, and a warm burnt-orange command-palette aesthetic.

## Commands

    irl-wisdom daily
    irl-wisdom moai
    irl-wisdom power
    irl-wisdom models
    irl-wisdom biases
    irl-wisdom discipline
    irl-wisdom fact
    irl-wisdom upgrade

Add <code>--copy</code> or <code>-c</code> to supported knowledge commands:

    irl-wisdom models --copy

A few commands are deliberately missing from this list. Curiosity deserves rewards.

## The Moai upgrade ritual

IRL Wisdom can update itself without wrestling with Windows launcher locks:

    irl-wisdom upgrade

The Moai checks PyPI, compares versions, asks permission, and hands installation to a delayed helper after the current CLI exits.

For scripts and fearless stones:

    irl-wisdom upgrade --yes

## How it works

    irl-wisdom
    ├── Typer commands
    ├── Questionary command palette
    ├── Rich terminal rendering
    ├── Local JSON knowledge collections
    └── ~/.irl_wisdom_config.json
        ├── favorites
        └── daily streak

The package is intentionally lightweight: no account, database, telemetry, or cloud service is required. Favorites and streak state stay local.

## Development

    git clone https://github.com/Dev2Creator/IRL-WISDOM.git
    cd IRL-WISDOM
    python -m pip install -e .
    irl-wisdom

Build and validate a release:

    python -m build
    python -m twine check dist/*

## Author

Created by **Anika Mukherjee**
Email: [cuteypieanika@gmail.com](mailto:cuteypieanika@gmail.com)
GitHub: [@Dev2Creator](https://github.com/Dev2Creator)

## Copyright, trademark, and license

Copyright © 2026 Anika Mukherjee. All rights reserved.

**IRL Wisdom™** is a trademark of Anika Mukherjee.

The source code is licensed under the [GNU Affero General Public License v3 or later](LICENSE). See [COPYRIGHT](COPYRIGHT) for the project notice.

---

<div align="center">

Built for people who still believe one good idea can change the shape of a day. 🗿

</div>