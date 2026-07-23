#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
import time

def main():
    os.environ["NODE_OPTIONS"] = "--localstorage-file=/tmp/node_storage"
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")
    backend_script = os.path.join(root_dir, "backend", "app.py")

    print("=========================================")
    print(" Iniciando Servidores do Projeto ELiS OCR")
    print("=========================================")

    processes = []
    try:
        # Iniciar Backend
        print("[Backend] Subindo servidor Flask na porta 5000...")
        backend_proc = subprocess.Popen(
            ["uv", "run", "python", backend_script],
            cwd=root_dir
        )
        processes.append(backend_proc)

        # Iniciar Frontend
        print("[Frontend] Subindo servidor Vue.js...")
        frontend_proc = subprocess.Popen(
            ["npm", "run", "serve"],
            cwd=frontend_dir
        )
        processes.append(frontend_proc)

        # Manter o processo ativo
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        print("\n\n=========================================")
        print(" Encerrando Backend e Frontend...")
        print("=========================================")
    finally:
        for p in processes:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill()
        print("Servidores encerrados com sucesso.")

if __name__ == "__main__":
    main()
