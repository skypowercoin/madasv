import os
import uvicorn

if __name__ == "__main__":
    # Render يمرر المنفذ عبر متغير بيئة يسمى PORT
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)