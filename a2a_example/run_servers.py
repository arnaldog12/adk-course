"""Inicia os servidores A2A (research, analysis, content) de forma multiplataforma.

Substitui os scripts start/stop em bash (que usam lsof/pkill/curl e só rodam no
macOS/Linux). Este script funciona igual no Windows e no macOS:

- sobe os 3 agentes com uvicorn + to_a2a() nas portas 8001/8002/8003;
- espera cada um ficar pronto consultando o agent card (via urllib, sem curl);
- encerra todos com Ctrl+C (sem pkill/lsof).

Uso (a partir da raiz do projeto):

    uv run python a2a_example/run_servers.py

Depois, em outro terminal:

    uv run adk web a2a_example
"""

from __future__ import annotations

import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# (módulo uvicorn, porta) de cada agente. A ordem importa só para os logs.
SERVERS: list[tuple[str, int]] = [
    ("research_agent.agent:a2a_app", 8001),
    ("analysis_agent.agent:a2a_app", 8002),
    ("content_agent.agent:a2a_app", 8003),
]

A2A_DIR = Path(__file__).resolve().parent
CARD_PATH = "/.well-known/agent-card.json"
READY_TIMEOUT_SECONDS = 60


def start_server(app: str, port: int) -> subprocess.Popen[bytes]:
    """Sobe um servidor uvicorn para o app/porta informados."""
    print(f"Iniciando {app} em http://localhost:{port}")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", app, "--host", "localhost", "--port", str(port)],
        cwd=A2A_DIR,
    )


def wait_until_ready(port: int, process: subprocess.Popen[bytes]) -> bool:
    """Aguarda o servidor responder no agent card. Retorna False se ele morrer antes."""
    url = f"http://localhost:{port}{CARD_PATH}"
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(url, timeout=2):  # noqa: S310 (URL local fixa)
                return True
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError):
            time.sleep(1)
    return False


def stop_servers(processes: list[subprocess.Popen[bytes]]) -> None:
    """Encerra todos os processos de forma graciosa (e força, se necessário)."""
    print("\nEncerrando servidores A2A...")
    for process in processes:
        if process.poll() is None:
            process.terminate()
    for process in processes:
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
    print("Servidores encerrados.")


def main() -> int:
    """Inicia todos os servidores e mantém o processo vivo até Ctrl+C."""
    processes: list[subprocess.Popen[bytes]] = []
    try:
        for app, port in SERVERS:
            process = start_server(app, port)
            processes.append(process)
            if wait_until_ready(port, process):
                print(f"  pronto: http://localhost:{port}")
            else:
                print(f"  FALHA ao iniciar na porta {port}. Veja os logs acima.")
                stop_servers(processes)
                return 1

        print("\nTodos os servidores A2A estão prontos!")
        print("Agora, em outro terminal, rode:  uv run adk web a2a_example")
        print("Pressione Ctrl+C aqui para encerrar todos os servidores.\n")

        # Mantém vivo até Ctrl+C ou até algum servidor cair.
        while True:
            for app, process in zip([s[0] for s in SERVERS], processes, strict=True):
                if process.poll() is not None:
                    print(f"O servidor {app} parou inesperadamente. Encerrando os demais.")
                    stop_servers(processes)
                    return 1
            time.sleep(1)
    except KeyboardInterrupt:
        stop_servers(processes)
        return 0


if __name__ == "__main__":
    # Garante encerramento limpo também ao receber SIGTERM (ex.: dentro do container).
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    raise SystemExit(main())
