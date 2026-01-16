## Brief overview
Guidelines for managing web servers during development tasks. These rules ensure proper cleanup of server processes after completing tasks.

## Server management
- Always stop/kill any web server that was started during task execution before completing the task
- If a server is left running in a terminal, explicitly mention this to the user or document how to stop it
- When delegating subtasks that may start servers, include instructions for proper cleanup
- Use process management tools (e.g., `pkill`, `kill`, `Ctrl+C`) to terminate servers cleanly
- For background server processes, track the process ID or use process management utilities to ensure complete termination

## Task completion checklist
- [ ] Verify all spawned server processes are terminated
- [ ] Clean up any temporary files or logs created by the server
- [ ] Document any servers that should remain running for the user
- [ ] Confirm port availability is restored

## Project context
- This rule applies to all development tasks that involve starting web servers, proxy servers, or any long-running background services
- For this Python proxy project, servers are typically started via `uvicorn`, `hypercorn`, or similar ASGI/WSGI servers
