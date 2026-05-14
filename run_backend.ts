import { spawn } from "child_process";
import path from "path";
import fs from "fs";

export function startDjango() {
  const backendDir = path.join(process.cwd(), "backend");
  
  const runCommand = (cmd: string, args: string[]) => {
    console.log(`Running: ${cmd} ${args.join(" ")}`);
    const logStream = fs.createWriteStream(path.join(process.cwd(), 'backend.log'), { flags: 'a' });
    const proc = spawn(cmd, args, {
      cwd: backendDir,
      stdio: ["inherit", "pipe", "pipe"],
    });

    if (proc.stdout) proc.stdout.pipe(logStream);
    if (proc.stderr) proc.stderr.pipe(logStream);

    return new Promise<number>((resolve) => {
      proc.on("close", (code) => {
        resolve(code || 0);
      });
      proc.on("error", (err) => {
        console.error(`Failed to start ${cmd}:`, err);
        resolve(-1);
      });
    });
  };

  const cleanupExisting = async () => {
    console.log("Cleaning up existing Django processes...");
    const { execSync } = await import('child_process');
    try {
      // Find and kill processes running Django runserver on 8000
      // Use pkill -9 -f for more reliability
      try {
        execSync("pkill -9 -f 'manage.py runserver'").toString();
      } catch (e) {
        // pkill exits with code 1 if no process matched
      }
      
      // Fallback manual cleanup using ps
      const psOutput = execSync("ps aux | grep 'manage.py runserver' | grep -v grep").toString();
      const lines = psOutput.split('\n');
      for (const line of lines) {
        const parts = line.trim().split(/\s+/);
        if (parts.length > 1) {
          const pid = parseInt(parts[1]);
          if (!isNaN(pid)) {
            console.log(`Killing existing Django process: ${pid}`);
            try { process.kill(pid, 'SIGKILL'); } catch (e) { /* ignore */ }
          }
        }
      }
    } catch (e) {
      // Ignore if no processes found
    }
  };

  const start = async () => {
    // Kill any existing instances first
    await cleanupExisting();
    let pythonCmd = "python3";
    let code = await runCommand(pythonCmd, ["--version"]);
    
    if (code !== 0) {
      console.log("python3 not found, trying python...");
      pythonCmd = "python";
      code = await runCommand(pythonCmd, ["--version"]);
      if (code !== 0) {
        console.error("Neither python3 nor python found!");
        return;
      }
    }

    console.log(`Using ${pythonCmd} for Django backend`);

    // Ensure pip is available
    console.log("Checking for pip...");
    let pipCode = await runCommand(pythonCmd, ["-m", "pip", "--version"]);
    
    if (pipCode !== 0) {
      console.log("pip not found, attempting to install via get-pip.py...");
      const getPipScript = `
import urllib.request
import subprocess
import sys
import os

url = "https://bootstrap.pypa.io/get-pip.py"
print(f"Downloading {url}...")
urllib.request.urlretrieve(url, "get-pip.py")
print("Running get-pip.py...")
subprocess.run([sys.executable, "get-pip.py", "--user"], check=True)
os.remove("get-pip.py")
`;
      fs.writeFileSync(path.join(backendDir, 'install_pip.py'), getPipScript);
      await runCommand(pythonCmd, ['install_pip.py']);
      
      // Verify again
      pipCode = await runCommand(pythonCmd, ["-m", "pip", "--version"]);
      if (pipCode !== 0) {
        console.error("Failed to install pip. Backend will not start.");
        return;
      }
    }

    console.log("Installing Python dependencies...");
    await runCommand(pythonCmd, ["-m", "pip", "install", "--user", "django", "djangorestframework", "django-cors-headers", "django-filter", "celery", "redis", "google-genai"]);

    console.log("Running Django makemigrations...");
    await runCommand(pythonCmd, ["manage.py", "makemigrations", "account", "eadmin", "efrontend"]);

    console.log("Starting Django migrations...");
    let migrateCode = await runCommand(pythonCmd, ["manage.py", "migrate"]);
    
    if (migrateCode !== 0) {
      console.log("Migrations failed. Checking if database is malformed...");
      // Try to check if it's a Malformed database error
      // A safe bet in dev is to just reset the sqlite db if migrate fails
      const dbPath = path.join(backendDir, "db.sqlite3");
      if (fs.existsSync(dbPath)) {
        console.log("Deleting potentially malformed or inconsistent database...");
        fs.unlinkSync(dbPath);
        console.log("Retrying migrations...");
        migrateCode = await runCommand(pythonCmd, ["manage.py", "migrate"]);
      }
    }
    
    if (migrateCode === 0) {
      console.log("Migrations completed successfully. Seeding products...");
      await runCommand(pythonCmd, ["manage.py", "seed_products"]);

      console.log("Starting Django server...");
      const logStream = fs.createWriteStream(path.join(process.cwd(), 'backend.log'), { flags: 'a' });
      logStream.write(`[${new Date().toISOString()}] Attempting to start Django on 8000...\n`);
      const server = spawn(pythonCmd, ["manage.py", "runserver", "0.0.0.0:8000", "--noreload"], {
        cwd: backendDir,
        stdio: ["inherit", "pipe", "pipe"],
      });

      if (server.stdout) server.stdout.pipe(logStream);
      if (server.stderr) server.stderr.pipe(logStream);

      server.on("error", (err) => {
        console.error("Failed to start Django server:", err);
      });
    } else {
      console.error(`Migrations failed with code ${migrateCode}`);
    }
  };

  start();
}
