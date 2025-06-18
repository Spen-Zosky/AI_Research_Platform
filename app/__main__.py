# Questo file permette di avviare il server con 'python -m app'
import uvicorn

if __name__ == "__main__":
    # Esegue l'applicazione definita in app.main
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
