const { spawn } = require("child_process");
const fs = require("fs");
const { agentDir, resolvePython, venvPython } = require("./agent-paths");

const python = resolvePython();

if (!fs.existsSync(venvPython())) {
  console.error(
    "\nVirtual environment not found. Run first:\n  npm run install:agent\n"
  );
  process.exit(1);
}

const child = spawn(python, ["agent.py"], {
  cwd: agentDir,
  stdio: "inherit",
  shell: false,
});

child.on("exit", (code) => process.exit(code ?? 0));
