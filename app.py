import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Dorar-Tafsir-MCP")

@mcp.tool()
async def get_ayah_tafsir(surah_number: int, ayah_number: int) -> dict:
    """جلب التفسير المعتمد لآية محددة."""
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

app = FastAPI(title="Dorar Tafsir MCP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/mcp", mcp.sse_app)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Dorar Tafsir MCP Server is Running"}
