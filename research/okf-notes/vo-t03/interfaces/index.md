# interfaces notes

## Documents

* [Tauri commands](./tauri-commands.md) - Every command registered in generate_handler, with inputs, outputs and declaring file.
* [Channel event messages](./pipeline-events.md) - The tagged event enums sent from Rust to the webview over Tauri channels.
* [Sidecar HTTP routes](./sidecar-http-routes.md) - Routes served by the FastAPI sidecar and the code that calls them.
* [Sidecar command-line arguments](./sidecar-cli-arguments.md) - The options the host passes to the sidecar process.
* [External HTTP endpoints](./external-http-endpoints.md) - Third-party URLs the code calls, with the file that calls each.
