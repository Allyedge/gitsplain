# Gitsplain

[![GitHub License](https://img.shields.io/github/license/Allyedge/gitsplain)](https://github.com/Allyedge/gitsplain)
[![GitHub Release](https://img.shields.io/github/v/release/Allyedge/gitsplain)](https://github.com/Allyedge/gitsplain)

A tool to summarise and explain your code changes, make it make sense!

## Installation

```sh
# Install Gitsplain.
# Replace <VERSION> and <ASSET_NAME> with values from the desired release
VERSION="v0.1.0"; ASSET_NAME="gitsplain-ubuntu-latest"; \
INSTALL_DIR="$HOME/.local/bin"; \
mkdir -p "$INSTALL_DIR"; \
echo "Downloading Gitsplain ${VERSION} (${ASSET_NAME})..."; \
curl -sL "https://github.com/Allyedge/gitsplain/releases/download/${VERSION}/${ASSET_NAME}" -o "${INSTALL_DIR}/gitsplain" && \
chmod +x "${INSTALL_DIR}/gitsplain" && \
echo "Installed Gitsplain to ${INSTALL_DIR}/gitsplain"; \
echo "Make sure ${INSTALL_DIR} is in your PATH, then run 'gitsplain --help' in a new terminal."
```

## Usage

```sh
# Run Gitsplain
> gitsplain

# Get help with Gitsplain
> gitsplain --help
```
