# Setting Up MCP Inspector for Debugging MCP Servers

The **Model Context Protocol (MCP) Inspector** is a powerful tool for testing and debugging MCP servers. It provides an interactive web UI that lets you explore:

* **Tools** – see input/output schemas and run them interactively.
* **Resources** – inspect available resources and their contents.
* **Prompts** – view and test prompt templates.
* **Notifications / Logs** – monitor server events in real time.

Whether you’re building in Python, JavaScript, or another language, Inspector makes it easy to verify your server’s behavior.

---

## 🚀 Quickstart (Python + stdio)

If your MCP server is written in Python and uses the **stdio** transport, you can start everything in one go:

```bash
npx @modelcontextprotocol/inspector fastmcp run my_server.py --transport stdio
```

This will:

1. Launch the MCP Inspector proxy.
2. Start your Python MCP server via stdio.
3. Open the Inspector UI at `http://localhost:6274` with an authentication token.

👉 No manual UI setup required — just run the command and start inspecting!

---

## Prerequisites

Before starting, make sure you have:

* **Node.js** (>=18, ideally 20+).
* A working **MCP server** (in this guide we focus on Python).
* The **stdio** transport enabled in your server implementation.

---

## Installing and Launching MCP Inspector

You don’t need a permanent install. Run Inspector directly with `npx`:

```bash
npx @modelcontextprotocol/inspector
```

This will start:

1. **Proxy** (default port `6277`) – manages the connection to your server.
2. **Web UI** (default port `6274`) – the browser interface.

Your terminal will display a secure URL such as:

```
http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=abcd1234...
```

Open that URL in your browser.

---

## Connecting Inspector to a Python MCP Server (stdio Transport)

If you prefer connecting manually through the UI:

1. Click **Connect**.
2. Select **Transport: stdio**.
3. Enter the command to run your MCP server. Examples:

   ```bash
   python path/to/my_server.py
   ```

   Or, if installed as a CLI:

   ```bash
   my-server
   ```
4. Add any required **arguments** or **environment variables**.
5. Click **Connect**.

Inspector will launch your server as a subprocess and communicate via stdio.

---

## Verifying the Connection

If successful, the Inspector UI will show tabs for:

* **Tools** – list of server tools with schemas; try them with sample inputs.
* **Resources** – browse available resources, URIs, metadata.
* **Prompts** – view and test prompt templates.
* **Notifications / Logs** – see server events in real time.

---

## Security Notes

* Inspector binds to **localhost** by default. Do not expose it to untrusted networks.
* Each session generates an **auth token**. Keep this private.
* Ports can be overridden via environment variables if needed.

---

## Conclusion

With MCP Inspector, you can quickly:

* Explore your server’s exposed functionality.
* Debug tool and resource behaviors.
* Test prompts and monitor real-time logs.

It’s an essential companion when developing or troubleshooting MCP servers — especially when using Python and stdio transport.

---

Would you like me to also add a **troubleshooting section** (e.g. “common errors and fixes” for stdio servers), so your blog readers don’t get stuck if Inspector can’t connect?
