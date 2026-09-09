import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP

# 1. تهيئة خادم MCP
mcp = FastMCP("Dorar-Tafsir-MCP")

@mcp.tool()
async def get_ayah_tafsir(surah_number: int, ayah_number: int) -> dict:
    """جلب التفسير المعتمد لآية محددة من الموسوعة القرآنية."""
    url = f"https://api.quran.com/api/v4/quran/tafsirs/16?verse_key={surah_number}:{ayah_number}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            res = await client.get(url)
            if res.status_code == 200:
                data = res.json()
                tafsir_text = data.get("tafsirs", [{}])[0].get("text", "لم يتم العثور على التفسير")
                return {
                    "surah": surah_number,
                    "ayah": ayah_number,
                    "tafsir_text": tafsir_text,
                    "source": "التفسير الميسر / الموسوعة القرآنية",
                    "status": "success"
                }
            return {"error": f"تعذر الجلب (رمز الحالة: {res.status_code})"}
        except Exception as e:
            return {"error": str(e)}

@mcp.tool()
async def search_dorar_tafsir(query: str) -> dict:
    """البحث في نصوص التفسير والألفاظ القرآنية."""
    search_url = f"https://api.quran.com/api/v4/search?query={query}&language=ar"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            res = await client.get(search_url)
            if res.status_code == 200:
                results_data = res.json().get("search", {}).get("results", [])
                parsed_results = []
                for item in results_data[:5]:
                    parsed_results.append({
                        "verse_key": item.get("verse_key"),
                        "text": item.get("text"),
                        "translations": [t.get("text") for t in item.get("translations", [])]
                    })
                return {
                    "query": query,
                    "results_count": len(parsed_results),
                    "results": parsed_results,
                    "source": "المحرك المعرفي المفتوح للقرآن والتفسير"
                }
            return {"error": f"خطأ في البحث: {res.status_code}"}
        except Exception as e:
            return {"error": str(e)}

# 2. إنشاء تطبيق FastAPI
app = FastAPI(title="Dorar Tafsir MCP")

# 3. إعداد CORS الشامل (مهم جداً لقبول طلبات ChatGPT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. دمج تطبيقي SSE
sse_app = mcp.sse_app
app.mount("/mcp", sse_app)
app.mount("/sse", sse_app)

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>Dorar Tafsir MCP Endpoint</title>
        <style>
            body { font-family: system-ui, sans-serif; background: #f8fafc; color: #1e293b; padding: 40px; }
            .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 12px; }
            code { background: #f1f5f9; padding: 4px 8px; color: #0f766e; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>خادم التفسير والدراسات الدلالية MCP</h1>
            <p>رابط الموصل المباشر:</p>
            <code>https://dorar-tafsir-mcp-1.onrender.com/sse/sse</code>
        </div>
    </body>
    </html>
    """

@app.get("/search")
async def search(query: str):
    return await search_dorar_tafsir(query)
