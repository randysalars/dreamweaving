#!/usr/bin/env node
/**
 * Diagnose "spawn python3 ENOENT" in container/Nix environments.
 *
 * Usage:
 *   node scripts/node/diagnose-python-spawn.mjs
 *
 * Optional env:
 *   PYTHON_EXECUTABLE=/absolute/path/to/python3
 *   PYTHON_SPAWN_DEBUG=1
 */

import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const DEBUG = process.env.PYTHON_SPAWN_DEBUG === "1";

function ts() {
  return new Date().toISOString();
}

function log(msg, obj) {
  const suffix = obj ? `\n${JSON.stringify(obj, null, 2)}` : "";
  // eslint-disable-next-line no-console
  console.error(`[diagnose-python-spawn ${ts()}] ${msg}${suffix}`);
}

function splitPath(value) {
  return (value || "").split(":").filter(Boolean);
}

function safeStat(p) {
  try {
    const s = fs.statSync(p);
    return { exists: true, isFile: s.isFile(), mode: s.mode };
  } catch (e) {
    return { exists: false, error: e?.code || String(e) };
  }
}

function isExecutable(p) {
  try {
    fs.accessSync(p, fs.constants.X_OK);
    return true;
  } catch {
    return false;
  }
}

function findOnPath(cmd, PATH) {
  for (const dir of splitPath(PATH)) {
    const full = path.join(dir, cmd);
    if (fs.existsSync(full)) return full;
  }
  return null;
}

function summarizeEnv() {
  const env = process.env;
  const PATH = env.PATH || "";
  return {
    node: {
      version: process.version,
      execPath: process.execPath,
      argv0: process.argv0,
      platform: process.platform,
      arch: process.arch,
    },
    os: {
      release: os.release(),
      type: os.type(),
      homedir: os.homedir(),
    },
    process: {
      cwd: process.cwd(),
      pid: process.pid,
      ppid: process.ppid,
      uid: typeof process.getuid === "function" ? process.getuid() : null,
      gid: typeof process.getgid === "function" ? process.getgid() : null,
    },
    env: {
      PATH,
      PYTHON_EXECUTABLE: env.PYTHON_EXECUTABLE || null,
      SHELL: env.SHELL || null,
      npm_config_user_agent: env.npm_config_user_agent || null,
    },
    pathDirs: splitPath(PATH),
  };
}

function printCandidateChecks() {
  const env = process.env;
  const PATH = env.PATH || "";

  const commonCandidates = [
    env.PYTHON_EXECUTABLE,
    findOnPath("python3", PATH),
    findOnPath("python", PATH),
    "/nix/var/nix/profiles/default/bin/python3",
    "/root/.nix-profile/bin/python3",
    "/usr/bin/python3",
    "/usr/local/bin/python3",
    "/bin/python3",
    "/app/.venv/bin/python",
    "/app/venv/bin/python",
    path.resolve("venv/bin/python"),
    path.resolve("venv/bin/python3"),
  ].filter(Boolean);

  const deduped = [...new Set(commonCandidates)];

  const checks = deduped.map((p) => ({
    path: p,
    stat: safeStat(p),
    executable: safeStat(p).exists ? isExecutable(p) : false,
  }));

  log("python candidate checks", { checks });
  return checks;
}

function runSpawn(executable, args, opts = {}) {
  const env = opts.env ?? process.env;
  const cwd = opts.cwd ?? process.cwd();

  return new Promise((resolve) => {
    const startedAt = Date.now();
    const child = spawn(executable, args, {
      cwd,
      env,
      stdio: ["ignore", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";
    let spawnError = null;

    child.on("error", (e) => {
      spawnError = {
        name: e?.name,
        message: e?.message,
        code: e?.code,
        errno: e?.errno,
        syscall: e?.syscall,
        path: e?.path,
        spawnargs: e?.spawnargs,
      };
      log("spawn error event", {
        executable,
        args,
        cwd,
        PATH: env?.PATH,
        error: spawnError,
      });
    });

    child.stdout?.on("data", (buf) => (stdout += buf.toString()));
    child.stderr?.on("data", (buf) => (stderr += buf.toString()));

    child.on("close", (code, signal) => {
      const durationMs = Date.now() - startedAt;
      if (DEBUG) {
        log("spawn close event", {
          executable,
          args,
          code,
          signal,
          durationMs,
          stdout,
          stderr,
          spawnError,
        });
      }
      resolve({ executable, args, code, signal, durationMs, stdout, stderr, spawnError });
    });
  });
}

async function main() {
  log("starting", summarizeEnv());
  printCandidateChecks();

  const PATH = process.env.PATH || "";
  const attempts = [];

  // Attempt 1: plain command (this is what your app is doing)
  attempts.push(await runSpawn("python3", ["--version"]));

  // Attempt 2: fallback to python
  attempts.push(await runSpawn("python", ["--version"]));

  // Attempt 3+: try absolute paths that frequently exist in Nix/container environments
  const absoluteCandidates = [
    process.env.PYTHON_EXECUTABLE,
    "/nix/var/nix/profiles/default/bin/python3",
    "/root/.nix-profile/bin/python3",
    "/usr/bin/python3",
    "/usr/local/bin/python3",
    "/bin/python3",
  ].filter(Boolean);

  for (const abs of absoluteCandidates) {
    if (fs.existsSync(abs)) {
      attempts.push(await runSpawn(abs, ["--version"]));
    } else if (DEBUG) {
      log("skipping missing absolute candidate", { abs });
    }
  }

  // Attempt 4: if python3 is on PATH but not resolved by Node for some reason, show what we *would* pick.
  const resolvedOnPath = findOnPath("python3", PATH) || findOnPath("python", PATH);
  log("resolvedOnPath()", { resolvedOnPath });

  log("summary", {
    ok: attempts.some((a) => a.code === 0),
    attempts: attempts.map((a) => ({
      executable: a.executable,
      code: a.code,
      signal: a.signal,
      durationMs: a.durationMs,
      spawnError: a.spawnError,
      stdout: a.stdout.trim(),
      stderr: a.stderr.trim(),
    })),
    interpretation: [
      "If python3/python attempts have spawnError.code=ENOENT, the executable isn't available in PATH (or isn't installed).",
      "If an absolute candidate works but python3 does not, your PATH in the app process is missing the directory containing python3.",
      "If python runs but python3 does not, switch your spawn to 'python' or set PYTHON_EXECUTABLE.",
    ],
    nextSteps: [
      "Nix: add python3 to your environment (e.g., 'nix-env -iA nixpkgs.python3' or include pkgs.python3 in replit.nix/nixpacks).",
      "App: set PYTHON_EXECUTABLE to an absolute python path and spawn that.",
    ],
  });
}

main().catch((e) => {
  log("FATAL", { message: e?.message, stack: e?.stack });
  process.exitCode = 1;
});

