const path = require("path");
const fs = require("fs");

const agentDir = path.join(__dirname, "..", "agent");
const isWin = process.platform === "win32";

function venvDir() {
  return path.join(agentDir, ".venv");
}

function venvPython() {
  return isWin
    ? path.join(venvDir(), "Scripts", "python.exe")
    : path.join(venvDir(), "bin", "python");
}

function venvPip() {
  return isWin
    ? path.join(venvDir(), "Scripts", "pip.exe")
    : path.join(venvDir(), "bin", "pip");
}

function systemPython() {
  return isWin ? "python" : "python3";
}

function resolvePython() {
  const venv = venvPython();
  return fs.existsSync(venv) ? venv : systemPython();
}

module.exports = {
  agentDir,
  isWin,
  venvDir,
  venvPython,
  venvPip,
  systemPython,
  resolvePython,
};
