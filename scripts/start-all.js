const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");
const { agentDir, resolvePython, venvPython } = require("./agent-paths");

const rootDir = path.join(__dirname, "..");
const apiDir = path.join(rootDir, "api");

function die(msg) {
  console.error(`\n${msg}\n`);
  process.exit(1);
}

if (!fs.existsSync(path.join(apiDir, "node_modules"))) {
  die("API dependencies missing. Run:\n  npm run install:api");
}

if (!fs.existsSync(venvPython())) {
  die("Agent virtual env missing. Run:\n  npm run install:agent");
}

const python = resolvePython();
const children = [];

function spawnProc(label, cmd, args, cwd) {
  const child = spawn(cmd, args, { cwd, stdio: "inherit", shell: false });
  child.on("exit", (code, signal) => {
    if (signal) {
      console.log(`\n[${label}] stopped (${signal})`);
    } else if (code && code !== 0) {
      console.log(`\n[${label}] exited with code ${code}`);
    }
    shutdown(code ?? 0);
  });
  children.push({ label, child });
  return child;
}

function shutdown(exitCode = 0) {
  for (const { child } of children) {
    if (!child.killed) child.kill("SIGTERM");
  }
  setTimeout(() => process.exit(exitCode), 300);
}

console.log("\nStarting BMC Control-M UI + agent...\n");
console.log("  UI     → http://localhost:3000");
console.log("  Agent  → http://localhost:5001/api/chat");
console.log("\nPress Ctrl+C to stop both.\n");

spawnProc("ui", "node", ["index.js"], apiDir);
spawnProc("agent", python, ["server.py"], agentDir);

process.on("SIGINT", () => {
  console.log("\nStopping...");
  shutdown(0);
});

process.on("SIGTERM", () => shutdown(0));
