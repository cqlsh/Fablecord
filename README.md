<h1 align="center">Fablecord</h1>

<p align="center">
  A Discord API wrapper for Python with no dependencies beyond the standard library, built to be fast.
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img alt="Python 3.13+" src="https://img.shields.io/badge/python-3.13%2B-3776ab.svg?logo=python&logoColor=white"></a>
  <a href="https://github.com/cqlsh/Fablecord/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
  <a href="https://github.com/microsoft/pyright"><img alt="pyright strict" src="https://img.shields.io/badge/pyright-strict-informational.svg"></a>
  <a href="https://github.com/cqlsh/Fablecord/actions/workflows/wheels.yml"><img alt="Wheels" src="https://github.com/cqlsh/Fablecord/actions/workflows/wheels.yml/badge.svg"></a>
  <img alt="Dependencies: none" src="https://img.shields.io/badge/dependencies-none-success.svg">
  <img alt="Status: pre-alpha" src="https://img.shields.io/badge/status-pre--alpha-orange.svg">
</p>

<p align="center">
  <a href="#why-another-one">Why</a> ·
  <a href="#what-is-different">What is different</a> ·
  <a href="#what-is-measured-so-far">Numbers</a> ·
  <a href="#where-things-stand">Status</a> ·
  <a href="#what-it-will-look-like">Example</a> ·
  <a href="#how-it-is-put-together">Layout</a> ·
  <a href="#installing">Install</a>
</p>

---

## Why another one

There are good Discord libraries for Python already. discord.py has carried the ecosystem for a decade and it is the reference this project measures itself against. But it grew up around aiohttp, it does a fair amount of work per event that nobody asked for, and some of its hot paths still scan lists when a dict would do.

Fablecord starts over with a few firm ideas:

- **No dependencies.** The HTTP/1.1 client, the WebSocket client, rate limiting, compression, all of it lives in this repository and runs on `asyncio`, `ssl`, `json` and `zlib`. Nothing to pin, nothing to audit twice. Two hot spots of the WebSocket client also exist in C. They are optional, the Python versions do the same job.
- **Do the work only when someone wants it.** Events are decoded only when a listener exists or the cache needs them. Messages build their embeds and attachments when you touch them. A presence update does not copy a member object just in case you wanted a `before`.
- **Constant time where it matters.** Message lookups, role lists, channel lists and permission math are cached and invalidated, not recomputed on every access.
- **Typed all the way down.** The whole library passes pyright in strict mode. Your editor knows what every attribute is.

## What is different

The short version, for people who know discord.py:

| | discord.py | Fablecord |
|---|---|---|
| Dependencies | aiohttp | none |
| Heartbeat | a thread | an asyncio task with loop block detection |
| Events nobody listens to | fully decoded and parsed | dropped after a peek at the event name |
| Presence updates | copy the member every time | mutate in place unless a `before` listener exists |
| Message cache lookup | linear scan over a deque | O(1) LRU |
| Role and channel lists | rebuilt and sorted on every access | cached, invalidated on change |
| Shard startup | one identify at a time | parallel within Discord's `max_concurrency` buckets |
| Type checking | typed, with escape hatches | pyright strict, ships `py.typed` |

Most of that table is about layers that do not exist yet, so take it as the plan. What exists is measured below.

## What is measured so far

Each layer is benchmarked before it is committed, against discord.py 2.7.1, Hikari 2.6.0 and aiohttp 3.14.3, which both of them sit on, installed side by side and doing the same job. The rival column is whichever of them was fastest at that job, the ratio is its number divided by Fablecord's. The HTTP and WebSocket rows run against a local server over loopback. The WebSocket rows are the best of five rounds with the C helpers loaded, the HTTP rows are the average of 3000 requests in a row, or of 20 rounds with 100 at once. One machine, an i7-11700F with Windows 11 and Python 3.13.14, so read the ratios rather than the absolute times.

| | fastest rival | Fablecord | ratio |
|---|---|---|---|
| HTTP: GET 1.4 KB of JSON on a kept-alive connection | aiohttp, 133.8 µs | 79.0 µs | 1.7x |
| HTTP: 100 requests at once, per request | aiohttp, 94.4 µs | 42.0 µs | 2.2x |
| HTTP: memory held per request in flight | aiohttp, 4.9 KB | 1.6 KB | 3.1x |
| Upload body: JSON plus a 1 KB file | discord.py, 56.4 µs | 4.9 µs | 12x |
| Upload body: JSON plus ten 100 KB files | discord.py, 997.4 µs | 47.3 µs | 21x |
| WebSocket: receive 100 B of text | aiohttp, 0.76 µs | 0.25 µs | 3.1x |
| WebSocket: receive 1.4 KB of text | aiohttp, 1.82 µs | 1.15 µs | 1.6x |
| WebSocket: send 100 B, a heartbeat | aiohttp, 1.45 µs | 0.75 µs | 1.9x |
| Parse an ISO 8601 timestamp from a payload | discord.py, 181.5 ns | 97.5 ns | 1.9x |
| `<t:...:R>` markup from a message ID | discord.py, 899.8 ns | 235.4 ns | 3.8x |
| Creation time of a snowflake | Hikari, 418.6 ns | 299.6 ns | 1.4x |

Enums and flags were measured operation by operation against both libraries, 392 rows in total: 337 faster than the better rival, 25 within five percent, 30 slower.

Where it does not win, and why. Most of the 30 slower enum and flag rows are enum equality, where Hikari's members are ints and compare in C, at 0.84x to 0.94x; the rest are a few lookups and flag conversions just under the five percent line. Parsing an HTTP response on its own is behind llhttp, aiohttp's C parser, at around 0.9x; the requests above are faster because of everything around the parser. WebSocket sends of 4 KB come out at around 0.9x on Windows, where asyncio's proactor transport only resumes a paused writer once its buffer is empty; under the selector loop the same row is 1.3x ahead. And without the C helpers the WebSocket client still receives faster than aiohttp, 1.4x at 100 B, but it sends slower, because aiohttp masks in Cython: 0.97x at 100 B, 0.56x at 600 B, 0.30x at 4 KB.

The benchmark scripts are not in the repository yet. They will land in `benchmarks/` so anyone can rerun the numbers.

## Where things stand

This is early. Really early. Nothing logs in to Discord yet, and the example below is the shape I am building towards, not something you can run today. The transport can already talk to Discord: in my own checks, which are not in the repository yet, the HTTP client fetched `/gateway` over TLS and the WebSocket client reads the gateway's Hello. There is no client on top of it.

- [x] Package skeleton, version info, `MISSING` sentinel, snowflake, time and markdown helpers, base exceptions
- [x] Enums and flags: 60 enums and 13 bit fields, intents and permissions among them. Values Discord adds later do not raise
- [x] Transport: an HTTP/1.1 client with a keep-alive pool and multipart bodies, and an RFC 6455 WebSocket client, both on raw `asyncio` protocols
- [x] Optional C helpers for the WebSocket client, wheels for Linux, macOS and Windows on x86_64 and arm64 built in CI
- [ ] REST: routes, rate limit buckets, one endpoint module per resource
- [ ] Gateway: session state machine, heartbeat, compression, sharding
- [ ] Events, models and the cache
- [ ] Application commands and interactive components
- [ ] Voice, which needs libopus and is its own adventure

## What it will look like

```python
import fablecord

client = fablecord.Client(intents=fablecord.Intents.default())

@client.listen()
async def on_message(event: fablecord.MessageCreate) -> None:
    if event.message.content == "!ping":
        await event.message.reply("pong")

client.run("your token here")
```

Events are typed objects rather than loose positional arguments, listeners are registered on the client, and everything you can `await` is documented as such.

Buttons, selects and modals work the way discord.py's `ui` module taught everyone, with less ceremony around it:

```python
class Confirm(fablecord.ui.View):
    @fablecord.ui.button(label="Confirm", style=fablecord.ButtonStyle.success)
    async def confirm(self, interaction: fablecord.Interaction, button: fablecord.ui.Button) -> None:
        await interaction.respond("Done.", ephemeral=True)
        self.stop()

await channel.send("Are you sure?", view=Confirm())
```

If you have written a `View` before, you already know how this works. The differences are in the details: persistent views need no registration dance, every callback is fully typed, and the new layout components are first class rather than bolted on.

## How it is put together

The layout follows discord.py, so `fablecord.Guild` will live in `guild.py` where you would look for it. Packages are used where discord.py has one too, or where it has one oversized file instead, plus the transport underneath. This is the target layout: today `net/`, `_speedups/`, `enums/`, `flags/`, `errors/` and `utils/` exist, the rest follows with the layers in the list above.

```
src/fablecord/
├── net/            HTTP/1.1, multipart and WebSocket, knows nothing about Discord
├── _speedups/      optional C helpers for net/, each with a Python fallback
├── http/           routes, rate limits, one endpoint module per resource
├── gateway/        connection, heartbeat, compression, session state machine
├── events/         typed events and their parsers
├── enums/          one module per area
├── flags/          intents, permissions and the other bit fields
├── errors/         the exception tree
├── utils/          snowflakes, time, markdown
├── app_commands/   application commands
├── ui/             views, buttons, selects and modals with callbacks
├── voice/          later
└── *.py            one module per model: guild.py, channel.py, member.py, message.py ...
```

`net/`, `http/` and `gateway/` are stacked, each one only talks to the one below it. `net/` could be lifted out and used for something that has nothing to do with Discord.

## Installing

Not on PyPI yet. When it is, this will be the whole story:

```
pip install fablecord
```

Until then, if you want to poke at the source:

```
git clone https://github.com/cqlsh/Fablecord.git
cd Fablecord
python -m venv .venv
.venv\Scripts\activate
pip install --group dev -e .
```

On Linux and macOS the activation line is `source .venv/bin/activate`, and `--group` needs pip 25.1 or newer. If a C compiler is installed, the editable install builds the C helpers into `src/fablecord/_speedups/`; if not, the install still succeeds and everything runs on the Python paths. pip only shows the build output with `-v`, so add it to see whether the helpers were built.

Python 3.13 or newer is required. There is no plan to support older versions, the library leans on recent `asyncio` and typing features on purpose.

## Contributing

Not yet, honestly. The foundation is still being poured and the shape of things changes daily. Once the gateway is up and there is something to break, issues and pull requests are very welcome. The ground rules will be simple: no new dependencies, pyright strict stays clean, and every change that touches a hot path brings a benchmark with it.

## License

MIT. See [LICENSE](https://github.com/cqlsh/Fablecord/blob/main/LICENSE).