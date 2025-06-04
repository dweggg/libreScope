![License](https://img.shields.io/github/license/dweggg/libreScope)

# libreScope
Powerful data visualization tool based on PyQt6. Infinitely customizable.

## Why?
When working with embedded systems it's typical to have some sort of data-based communication. More often than not, engineers need to visualize, log, and analyze this data quickly and flexibly. Existing tools are often too rigid, too simple, too complex, too expensive, or simply bad. Basically this aims to be a portable Grafana for embedded devs. The idea is that the tool serves as a RX node mostly but equip it with TX capabilities. For now, it will be just text input.

**libreScope** aims to fill this gap by providing a modern, extensible, and user-friendly data visualization platform that you can adapt yourself to whatever protocol you need. The only work you (or ChatGPT) have to put in is providing the link between your data and the app. Since it's built in Python you can expect a library to do most of the work. I'm still unsure if the right approach is to include all the protocols in here or think of them as separate forks...

## Roadmap
- Fully abstract the communication protocol
- Redo the protocol as kind of a plugin rather than letting it stay buried between other files
- Define a clear purpose and curate a few examples (CAN & serial are a must for me at least)

## Contributing

Contributions are yet not accepted but they will in the near future. I want to get something rolling first.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgements

Inspired by MCUViewer, and the needs of embedded systems engineers everywhere.
