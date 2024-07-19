# Language Support for Evergreen.lxl

This repository provides plugins for language support in Evergreen.

Plugins consist of query files from [`nvim-treesitter`](https://github.com/nvim-treesitter/nvim-treesitter),
and a shared library containing the parser and scanner if needed.

Updates from upstream are fetched daily.

# Installation

Do note that some language plugins may have dependencies on other ones.
If not using a package manager, you will have to download the plugins for them as well.

It is recommended to use a package manager if possible –
it greatly simplifies dealing with dependencies, and provides automatic updates.

## Plugin manager (recommended)

### lpm / ppm

Add this repository to your sources:
```sh
lpm repo add https://github.com/Evergreen-lxl/evergreen-languages.git:main
ppm repo add https://github.com/Evergreen-lxl/evergreen-languages.git:main
```

To install support for languages `foo` and `bar`:
```sh
lpm install evergreen_foo evergreen_bar
ppm install evergreen_foo evergreen_bar
```

### Miq

Add this repository to your sources in your user module:
```lua
config.plugins.miq.repos = {
	'https://github.com/Evergreen-lxl/evergreen-languages.git:main',
}
```

To install support for languages `foo` and `bar`:
```lua
config.plugins.miq.plugins = {
	'evergreen_foo',
	'evergreen_bar',
}
```

## Manual

### Prebuilt plugins

The downloads for supported platforms can be found here:
 - [Windows x86_64](https://github.com/Evergreen-lxl/evergreen-languages/releases/tag/x86_64-windows)
 - [Linux x86_64](https://github.com/Evergreen-lxl/evergreen-languages/releases/tag/x86_64-linux)
 - [Linux aarch64](https://github.com/Evergreen-lxl/evergreen-languages/releases/tag/aarch64-linux)
 - [macOS x86_64](https://github.com/Evergreen-lxl/evergreen-languages/releases/tag/x86_64-darwin)
 - [macOS aarch64](https://github.com/Evergreen-lxl/evergreen-languages/releases/tag/aarch64-darwin)

Unzip the file contents into a folder inside your plugins folder.

### From source

For platforms not currently supported, you can download the source packages from [here](https://github.com/Evergreen-lxl/evergreen-languages/releases/tag/srcpkg).

Unzip the file contents into a folder inside your plugins folder.

If a makefile is present, run `make all` to build the shared library.
Otherwise, building is not required.

# Licensing

`evergreen-languages` is licensed under the MIT license.  
`nvim-treesitter` is licensed under the Apache-2.0 license.

You should receive these two licences, as well as the license of the Tree-sitter grammar for the language when downloading a plugin.
