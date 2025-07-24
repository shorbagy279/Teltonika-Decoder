# Teltonika‑Decoder

A simple Python library to decode Teltonika device messages (AVL data and text codecs)  
from raw hexadecimal frames into structured Python objects.

## Features

- **AVL data** (codecs 0x08, 0x8E, 0x10): GPS, speed, altitude, IO, etc.
- **Text messages** (0x0C, 0x0D, 0x0E): plain texts, alarms, and IMEI payload.
- Pure‑Python, zero dependencies beyond the standard library.
- Type‑annotated, with clear docstrings and examples.

## Installation

Clone the repo and (optionally) install in editable mode:

```bash
git clone https://github.com/shorbagy279/Teltonika-Decoder
cd Teltonika-Decoder
pip install -e .
