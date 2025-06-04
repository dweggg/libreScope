# libreScope
Powerful data visualization tool based on PyQt6. Infinitely customizable.

## Why?
When working with embedded systems it's typical to have some sort of data-based communication like CAN bus, USB, or a simple serial protocol. More often than not, engineers need to visualize, log, and analyze this data quickly and flexibly. Existing tools are often too rigid, too simple, or too complex, too expensive, or simply bad.

**libreScope** aims to fill this gap by providing a modern, extensible, and user-friendly data visualization platform that you can adapt yourself to whatever protocol you need. The only work you (or ChatGPT) have to put in is providing the link between your data and the app. Since it's built in Python you can expect a library to do most of the work. I'm still unsure if the right approach is to include all the protocols in here or think of them as separate forks...

## Features

- **Real-time plotting** of multiple signals, features like XY plots, cursors, etc.
- **Flexible tiling layout**: split, merge, and arrange plots as needed
- **CSV logging** and log file loading
- **Cross-platform** (Linux, Windows, macOS)
- **Plugin-ready architecture** for new protocols and visualizations

## Contributing

Contributions are yet not accepted but they will in the near future.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgements

Inspired by MCUViewer, and the needs of embedded systems engineers everywhere.