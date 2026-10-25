# Spaceland Planetarium Guide

A small Python assistant for planetarium visitors. It answers questions about all eight planets using one consistent set of 12 NASA-sourced facts per planet. It can use Zetaris Lightning as a fact store and Meterless as an optional local language-model endpoint. The bundled catalog keeps answers available when either service is offline.

## Run it

Use Python 3.11 or newer and Java 17 or newer. Put the Zetaris JDBC driver at `jdbc/ndp-jdbc-driver-2.4.3.1-7eff043-driver.jar`; the jar is intentionally ignored by Git.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python planetarium.py
```

Example questions:

```powershell
python planetarium.py --ask "Tell me about Jupiter"
python planetarium.py --ask "Compare Earth and Mars"
python planetarium.py --ask "What is Saturn's atmosphere like?"
python planetarium.py --ask "Give me facts about all planets"
```

The interactive prompt accepts the same questions. Each planet card has 12 fields: position, classification, diameter, mean solar distance, orbital period, rotation period, axial tilt, reference gravity, known moons, rings, atmosphere, and a notable fact. Moon counts reflect the cited NASA pages and may change as discoveries are confirmed. Gas-giant gravity is labeled at the 1-bar level.

## Zetaris Lightning

The app uses the supplied `com.zetaris.lightning.jdbc.LightningDriver` jar directly through JayDeBeApi. Set `ZETARIS_URL`, `ZETARIS_USER`, `ZETARIS_PASSWORD`, and `ZETARIS_JAR` in the ignored `.env` file. The password is deliberately not included in this repository. JPype needs a Java runtime; set `JAVA_HOME` in `.env` if it cannot locate the JVM automatically.

To create and seed the optional `planetarium_facts` table:

```powershell
python seed_zetaris.py
```

The seeder creates the table if needed, skips existing planet rows, and sends one SQL statement per JDBC `execute` call. The assistant reads rows with a parameterized `SELECT`; if the database or table is unavailable, it uses the bundled NASA catalog instead. The seeder does not delete or overwrite existing rows.

## Meterless and NVIDIA

The intent router is a small deterministic Python implementation inspired by Meterless Scout Intent's Sense/Route pattern: it identifies planet-fact, comparison, all-planets, or clarification requests before selecting data. Meterless describes Scout as an implementation spec, not a published Python runtime package, so this project does not claim to import `@meterless/scout`.

When a Meterless-compatible OpenAI API endpoint is running, configure `METERLESS_BASE_URL`, `METERLESS_MODEL`, and `METERLESS_TOKEN_FILE` (or `METERLESS_API_KEY`) in `.env`. The default endpoint is `http://127.0.0.1:8088/v1`; `meterless/local` asks the Meterless provider to use a local model. The model receives only selected catalog facts and is instructed not to add outside facts. If it is unreachable or unconfigured, the assistant returns its deterministic, sourced answer.

On Windows with an NVIDIA GPU, Meterless Nightshift can use its CUDA-backed local-model path. Start/configure that Meterless provider separately and point this assistant at its endpoint. This Python project does not itself load CUDA or claim GPU inference; NVIDIA acceleration happens in the configured Meterless model runtime. The catalog and fallback answer path work without a GPU or Meterless installation.

## Tests

```powershell
python -m unittest discover -s tests -v
```

Tests cover the eight-planet, 12-field catalog, intent routing, source links, and operation without Zetaris or Meterless.

## Fact sources

- [NASA Solar System planets](https://science.nasa.gov/solar-system/planets/)
- [Mercury](https://science.nasa.gov/mercury/facts/)
- [Venus](https://science.nasa.gov/venus/venus-facts/)
- [Earth](https://science.nasa.gov/earth/facts/)
- [Mars](https://science.nasa.gov/mars/facts/)
- [Jupiter](https://science.nasa.gov/jupiter/facts/)
- [Saturn](https://science.nasa.gov/saturn/facts/)
- [Uranus](https://science.nasa.gov/uranus/facts/)
- [Neptune](https://science.nasa.gov/neptune/facts/)