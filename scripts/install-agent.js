const { spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const {
  agentDir,
  isWin,
  systemPython,
  venvDir,
  venvPip,
  venvPython,
} = require("./agent-paths");

function run(cmd, args, options = {}) {
  const result = spawnSync(cmd, args, {
    cwd: agentDir,
    stdio: "inherit",
    shell: false,
    ...options,
  });
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

function createVenv() {
  const candidates = isWin
    ? [
        [systemPython(), ["-m", "venv", venvDir()]],
        ["py", ["-3", "-m", "venv", venvDir()]],
      ]
    : [
        [systemPython(), ["-m", "venv", venvDir()]],
        ["python", ["-m", "venv", venvDir()]],
      ];

  for (const [cmd, args] of candidates) {
    console.log(`Creating virtual environment (${cmd})...`);
    const result = spawnSync(cmd, args, {
      cwd: agentDir,
      stdio: "inherit",
      shell: false,
    });
    if (result.status === 0 && fs.existsSync(venvPython())) {
      return;
    }
  }

  console.error(
    "\nCould not create .venv. Install Python 3 and ensure it is on PATH.\n" +
      (isWin
        ? "Windows: https://www.python.org/downloads/ — check 'Add python.exe to PATH'\n"
        : "macOS/Linux: install python3 (e.g. brew install python)\n")
  );
  process.exit(1);
}

console.log("\nInstalling Python agent dependencies into agent/.venv\n");

if (!fs.existsSync(venvPython())) {
  createVenv();
}

const requirements = path.join(agentDir, "requirements.txt");
run(venvPip(), ["install", "--prefer-binary", "-r", requirements]);

console.log("\nDone. Start the agent with: npm run start:agent\n");
