import http.server
import socketserver
import json
import os
from pathlib import Path
import sys

# Ajout du chemin parent
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.assistant import query_assistant, DEFAULT_MODEL_NAME

PORT = 8000
WEB_DIR = Path(__file__).resolve().parent / "web"

class AssistantHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        if self.path == "/api/neutrality":
            try:
                report_path = Path(__file__).resolve().parent.parent / "eval" / "rapport_neutralite_miroirs.md"
                if not report_path.exists():
                    self._send_json({"error": "Rapport de neutralité introuvable. Lancez eval/test_neutrality_mirrors.py d'abord."}, status=404)
                    return
                # Lecture des métriques clés depuis le rapport Markdown
                content = report_path.read_text(encoding="utf-8")
                import re
                indice_match = re.search(r'\*\*Indice de symétrie argumentative\*\*.*?\|\s*\*\*([0-9.]+)%\*\*', content)
                ecart_match  = re.search(r'\*\*Écart moyen de traitement\*\*.*?\|\s*\*\*([0-9.]+) pts\*\*', content)
                paires_match = re.search(r'\*\*Paires miroirs évaluées\*\*.*?\|\s*\*\*(\d+) paires\*\*', content)
                indice  = float(indice_match.group(1))  if indice_match  else None
                ecart   = float(ecart_match.group(1))   if ecart_match   else None
                paires  = int(paires_match.group(1))    if paires_match  else None
                # Lecture détail des paires (lignes du tableau — on exclut les lignes d'entête :---)
                pair_rows = re.findall(
                    r'\|\s*([a-zA-Z][a-zA-Z0-9_]+)\s*\|\s*(TEST-\S+.*?)\s*\|\s*(TEST-\S+.*?)\s*\|\s*(\d+%)\s*\|\s*([0-9.]+) pts\s*\|\s*(.+?)\s*\|',
                    content
                )
                pairs = [{"theme": r[0], "texte_a": r[1], "texte_b": r[2],
                           "symetrie": r[3], "ecart_pts": float(r[4]), "verdict": r[5].strip()} for r in pair_rows]
                verdict = "VALIDÉ NEUTRE" if (indice and indice >= 90 and ecart and ecart <= 15) else "À VÉRIFIER"
                self._send_json({
                    "indice_symetrie": indice,
                    "ecart_moyen_pts": ecart,
                    "nb_paires": paires,
                    "verdict": verdict,
                    "pairs": pairs
                })
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        if self.path == "/api/logs":
            try:
                import sqlite3
                from src.logger import DB_PATH
                if not DB_PATH.exists():
                    self._send_json({"total": 0, "logs": [], "avg_latency_ms": 0, "valid_rate": 100})
                    return

                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*), AVG(latency_ms) FROM interaction_logs")
                total, avg_lat = cur.fetchone()
                
                cur.execute("SELECT COUNT(*) FROM interaction_logs WHERE is_valid_json = 1")
                valid_count = cur.fetchone()[0]

                cur.execute("""
                    SELECT timestamp, prompt_version, user_question, is_valid_json, latency_ms 
                    FROM interaction_logs 
                    ORDER BY id DESC LIMIT 10
                """)
                rows = cur.fetchall()
                conn.close()

                logs = []
                for r in rows:
                    logs.append({
                        "timestamp": r[0],
                        "version": r[1],
                        "question": (r[2][:60] + "...") if len(r[2]) > 60 else r[2],
                        "is_valid": bool(r[3]),
                        "latency_ms": round(r[4] or 0, 1)
                    })

                valid_rate = round((valid_count / total * 100) if total else 100, 1)
                self._send_json({
                    "total": total or 0,
                    "avg_latency_ms": round(avg_lat or 0, 1),
                    "valid_rate": valid_rate,
                    "logs": logs
                })
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/ask":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                # Support rétro-compatible question, texte et text
                user_text = data.get("texte") or data.get("text") or data.get("question") or ""
                user_text = user_text.strip()
                api_key = data.get("api_key") or data.get("groq_key") or None

                if not user_text:
                    self._send_json({"error": "Le texte à analyser ne peut pas être vide."}, status=400)
                    return

                resp, is_valid, latency_ms, raw_text = query_assistant(user_text, api_key=api_key)

                result = {
                    "is_valid": is_valid,
                    "latency_ms": round(latency_ms, 2),
                    "response": resp.model_dump() if resp else None,
                    "raw_text": raw_text
                }
                self._send_json(result)
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
        else:
            self.send_error(404, "Route introuvable")

    def _send_json(self, data, status=200):
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

class ReusableTCPServer(socketserver.ThreadingTCPServer):
    daemon_threads = True

def run_server():
    os.chdir(WEB_DIR)
    port = PORT
    max_tries = 5
    httpd = None

    for i in range(max_tries):
        try:
            httpd = ReusableTCPServer(("", port), AssistantHandler)
            break
        except OSError as e:
            if e.winerror == 10048 or "address" in str(e).lower():
                print(f"[Info] Le port {port} est déjà utilisé, tentative sur le port {port + 1}...")
                port += 1
            else:
                raise e

    if not httpd:
        print(f"Erreur : Impossible de trouver un port libre entre {PORT} et {PORT + max_tries - 1}.")
        return

    print("=" * 70)
    print("⚖️ ASSISTANT D'ESPRIT CRITIQUE & DÉCONSTRUCTION D'ARGUMENTS (GEMMA 2)")
    print(f"👉 Accédez à l'application web : http://localhost:{port}")
    print(f"📌 Modèle LLM configuré : Google Gemma 2 ({DEFAULT_MODEL_NAME})")
    print("Appuyez sur Ctrl+C dans cette fenêtre pour arrêter le serveur.")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run_server()
