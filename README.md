# LSP-rumdl

This is a helper package that automatically installs and updates [rumdl](https://github.com/rvben/rumdl) for you.

## Requirements

To use this package, you must have:

- The [LSP](https://packagecontrol.io/packages/LSP) package
- It's recommended to also install the [LSP-json](https://packagecontrol.io/packages/LSP-json) package which will provide auto-completion and validation for this package's settings.

## Configuration

There are multiple ways to configure the package and the language server.

- Global configuration: `Preferences > Package Settings > LSP > Servers > LSP-rumdl`
- Project-specific configuration:
  From the Command Palette run `Project: Edit Project` and add your settings in:

	```js
	{
		"settings": {
			"LSP": {
				"LSP-rumdl": {
					"initializationOptions": {
						"settings": {
							// Put your settings here
						}
					}
				}
			}
		}
	}
	```
