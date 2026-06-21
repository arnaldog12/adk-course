"""Inicia os servidores A2A (research, analysis, content) de forma multiplataforma.

Este script funciona igual no Windows e no macOS:
- sobe os 3 agentes com uvicorn + to_a2a() nas portas 8001/8002/8003;
- espera cada um ficar pronto consultando o agent card (via urllib, sem curl);
- encerra todos com Ctrl+C (sem pkill/lsof).

Uso (a partir da raiz do projeto):

    uv run python a2a_example/run_servers.py

Depois, em outro terminal:

    uv run adk web a2a_example
"""

from __future__ import annotations

import os
import platform
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SERVERS: list[tuple[str, int]] = [
    ("research_agent.agent:a2a_app", 8001),
    ("analysis_agent.agent:a2a_app", 8002),
    ("content_agent.agent:a2a_app", 8003),
]

A2A_DIR = Path(__file__).resolve().parent
CARD_PATH = "/.well-known/agent-card.json"
READY_TIMEOUT_SECONDS = 60


def kill_process_on_port(port: int) -> None:
    """Encontra e encerra qualquer processo escutando na porta informada (multiplataforma)."""
    print(f"🧹 Verificando se a porta {port} está em uso...", flush=True)

    if platform.system() == "Windows":
        try:
            output = subprocess.check_output(  # noqa: S602
                ["netstat", "-ano", "-p", "tcp"],  # noqa: S607
                shell=True,
                text=True,
                errors="ignore",
            )
            pids_to_kill = set()
            for line in output.splitlines():
                line = line.strip()
                if not line:
                    continue
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit() and int(pid) > 0:
                            pids_to_kill.add(pid)

            for pid in pids_to_kill:
                print(f"  [Windows] Encerrando processo PID {pid} na porta {port}...", flush=True)
                subprocess.run(  # noqa: S603
                    ["taskkill", "/F", "/PID", pid],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception as e:
            print(f"  ⚠️ Erro ao verificar/encerrar processo na porta {port} no Windows: {e}", flush=True)
    else:
        try:
            output = subprocess.check_output(  # noqa: S603
                ["lsof", "-t", "-i", f":{port}"],  # noqa: S607
                text=True,
                stderr=subprocess.DEVNULL,
            )
            pids = [line.strip() for line in output.splitlines() if line.strip().isdigit()]
            for pid in pids:
                print(f"  [Unix] Encerrando processo PID {pid} na porta {port}...", flush=True)
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
                except PermissionError:
                    subprocess.run(["kill", "-9", pid], check=False)  # noqa: S603, S607
        except subprocess.CalledProcessError:
            pass
        except Exception as e:
            print(f"  ⚠️ Erro ao verificar/encerrar processo na porta {port}: {e}", flush=True)


def start_server(app: str, port: int) -> subprocess.Popen[bytes]:
    """Sobe um servidor uvicorn para o app/porta informados."""
    emoji = "🤖"
    agent_name = "Research Agent" if "research" in app else "Analysis Agent" if "analysis" in app else "Content Agent"
    print(f"{emoji} Iniciando {agent_name} em http://localhost:{port}...", flush=True)

    env = os.environ.copy()
    env["PYTHONWARNINGS"] = "ignore"

    return subprocess.Popen(  # noqa: S603
        [sys.executable, "-m", "uvicorn", app, "--host", "localhost", "--port", str(port)],
        cwd=A2A_DIR,
        env=env,
    )


def wait_until_ready(port: int, process: subprocess.Popen[bytes]) -> bool:
    """Aguarda o servidor responder no agent card. Retorna False se ele morrer antes."""
    url = f"http://localhost:{port}{CARD_PATH}"
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(url, timeout=2):  # noqa: S310
                return True
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError):
            time.sleep(1)
    return False


def stop_servers(processes: list[subprocess.Popen[bytes]]) -> None:
    """Encerra todos os processos de forma graciosa (e força, se necessário)."""
    print("\n🛑 Encerrando servidores A2A...", flush=True)
    for process in processes:
        if process.poll() is None:
            process.terminate()
    for process in processes:
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print("⚠️ Forçando encerramento de servidor pendente...", flush=True)
            process.kill()
    print("✅ Servidores encerrados.", flush=True)


def main() -> int:
    """Inicia todos os servidores e mantém o processo vivo até Ctrl+C."""
    print("🧹 Realizando limpeza prévia de processos nas portas dos servidores...", flush=True)
    for _, port in SERVERS:
        kill_process_on_port(port)
    print("🧹 Limpeza concluída.\n", flush=True)

    processes: list[subprocess.Popen[bytes]] = []
    try:
        print("🚀 Iniciando servidores ADK A2A...", flush=True)
        for app, port in SERVERS:
            process = start_server(app, port)
            processes.append(process)
            agent_name = (
                "Research Agent" if "research" in app else "Analysis Agent" if "analysis" in app else "Content Agent"
            )
            print(f"⏳ Aguardando {agent_name} ficar pronto na porta {port}...", flush=True)
            if wait_until_ready(port, process):
                print(f"✅ {agent_name} está pronto em http://localhost:{port}", flush=True, end="\n\n")
            else:
                print(f"❌ FALHA ao iniciar {agent_name} na porta {port}. Veja os logs acima.", flush=True)
                stop_servers(processes)
                return 1

        print("\n🎉 Todos os servidores A2A estão prontos e rodando com sucesso!", flush=True)
        print("📋 Status dos Servidores:", flush=True)
        for app, process, (_, port) in zip([s[0] for s in SERVERS], processes, SERVERS, strict=True):
            agent_name = (
                "Research Agent" if "research" in app else "Analysis Agent" if "analysis" in app else "Content Agent"
            )
            print(f"   • {agent_name}: http://localhost:{port} (PID: {process.pid})", flush=True)

        print("\n🔗 Agent Cards (gerados automaticamente):", flush=True)
        for app, (_, port) in zip([s[0] for s in SERVERS], SERVERS, strict=True):
            agent_name = (
                "Research Agent" if "research" in app else "Analysis Agent" if "analysis" in app else "Content Agent"
            )
            print(f"   • {agent_name}: http://localhost:{port}/.well-known/agent-card.json", flush=True)

        print("\n🏃 Pronto para orquestração! Em outro terminal, rode:  uv run adk web a2a_example", flush=True)
        print("🛑 Pressione Ctrl+C aqui para encerrar todos os servidores.\n", flush=True)

        while True:
            for app, process in zip([s[0] for s in SERVERS], processes, strict=True):
                if process.poll() is not None:
                    agent_name = (
                        "Research Agent"
                        if "research" in app
                        else "Analysis Agent"
                        if "analysis" in app
                        else "Content Agent"
                    )
                    print(f"⚠️ O servidor {agent_name} parou inesperadamente. Encerrando os demais.", flush=True)
                    stop_servers(processes)
                    return 1
            time.sleep(1)
    except KeyboardInterrupt:
        stop_servers(processes)
        return 0


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    raise SystemExit(main())
