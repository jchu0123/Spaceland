# Spaceland Planetarium Guide

A small Python planetarium guide with a space-themed web interface. Visitors can explore the Sun, all eight planets, and the Moon, each with 24 NASA-sourced facts, or ask the guide questions and compare worlds. It can use Zetaris Lightning as a fact store and Meterless as an optional local language-model endpoint. The bundled catalogs keep answers available when either service is offline.

## Run it

Use Python 3.11 or newer and Java 17 or newer. Put the Zetaris JDBC driver at `jdbc/ndp-jdbc-driver-2.4.3.1-7eff043-driver.jar`; the jar is intentionally ignored by Git.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python planetarium.py --web
```

Open `http://127.0.0.1:8000` to explore the planetarium. The web server binds to localhost by default; use `--host` and `--port` to choose a different address. The original command-line guide is still available:

```powershell
python planetarium.py
```

## Deploy to Vercel

Import this repository into Vercel with the project root as the Root Directory. Vercel detects `app.py` as the Python ASGI entrypoint and serves the same interface and question API. No custom build command or entrypoint setting is needed. The bundled fact catalogs work without environment variables; Zetaris and Meterless remain optional.

Example command-line questions:

```powershell
python planetarium.py --ask "Tell me about Jupiter"
python planetarium.py --ask "Compare Earth and Mars"
python planetarium.py --ask "What is Saturn's atmosphere like?"
python planetarium.py --ask "Give me facts about all planets"
```

The interactive prompt accepts the same questions. Every object card has 24 facts, covering orbital and physical properties, temperature, composition, surface features, magnetic fields, exploration, water, and weather. Short questions such as `saturn's rings`, `earth gravity`, or `Jupiter moons` select the matching fact; broader questions show the full card. Moon counts reflect the cited NASA pages and may change as discoveries are confirmed. Gas-giant gravity is labeled at the 1-bar level. The Sun and Moon facts are stored in `data/solar_bodies.json`; planet facts remain in `data/planets.json`.

## Zetaris Lightning

The app uses the supplied `com.zetaris.lightning.jdbc.LightningDriver` jar directly through JayDeBeApi. Set `ZETARIS_URL`, `ZETARIS_USER`, `ZETARIS_PASSWORD`, and `ZETARIS_JAR` in the ignored `.env` file. The password is deliberately not included in this repository. JPype needs a Java runtime; set `JAVA_HOME` in `.env` if it cannot locate the JVM automatically.

To create and seed the optional `planetarium_facts` table:

```powershell
python seed_zetaris.py
```

The seeder creates the table if needed, skips existing planet rows, and sends one SQL statement per JDBC `execute` call. Zetaris stores the original 12 database columns; the assistant merges those records with the expanded bundled catalog so the full 24 facts remain available without a database migration. It reads rows with a parameterized `SELECT`; if the database or table is unavailable, it uses the bundled NASA catalog instead. The seeder does not delete or overwrite existing rows.

## Meterless and NVIDIA

The intent router is a small deterministic Python implementation inspired by Meterless Scout Intent's Sense/Route pattern: it identifies planet-fact, comparison, all-planets, or clarification requests before selecting data. Meterless describes Scout as an implementation spec, not a published Python runtime package, so this project does not claim to import `@meterless/scout`.

When a Meterless-compatible OpenAI API endpoint is running, configure `METERLESS_BASE_URL`, `METERLESS_MODEL`, and `METERLESS_TOKEN_FILE` (or `METERLESS_API_KEY`) in `.env`. The default endpoint is `http://127.0.0.1:8088/v1`; `meterless/local` asks the Meterless provider to use a local model. The model receives only selected catalog facts and is instructed not to add outside facts. If it is unreachable or unconfigured, the assistant returns its deterministic, sourced answer.

On Windows with an NVIDIA GPU, Meterless Nightshift can use its CUDA-backed local-model path. Start/configure that Meterless provider separately and point this assistant at its endpoint. This Python project does not itself load CUDA or claim GPU inference; NVIDIA acceleration happens in the configured Meterless model runtime. The catalog and fallback answer path work without a GPU or Meterless installation.

## Tests

```powershell
python -m unittest discover -s tests -v
```

Tests cover the eight-planet catalog, the Sun and Moon, 24 facts per object, concise fact queries, intent routing, source links, and operation without Zetaris or Meterless.

## Fact sources

- [NASA Solar System planets](https://science.nasa.gov/solar-system/planets/)
- [Sun](https://science.nasa.gov/sun/facts/)
- [Moon](https://science.nasa.gov/moon/facts/)
- [Mercury](https://science.nasa.gov/mercury/facts/)
- [Venus](https://science.nasa.gov/venus/venus-facts/)
- [Earth](https://science.nasa.gov/earth/facts/)
- [Mars](https://science.nasa.gov/mars/facts/)
- [Jupiter](https://science.nasa.gov/jupiter/facts/)
- [Saturn](https://science.nasa.gov/saturn/facts/)
- [Uranus](https://science.nasa.gov/uranus/facts/)
- [Neptune](https://science.nasa.gov/neptune/facts/)