import os
import urllib.parse
import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP

# 1. تهيئة خادم MCP باسم الموسوعة
mcp = FastMCP("Dorar Tafsir MCP")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
BASE_URL = "https://dorar.net/tafsir"

@mcp.tool()
async def get_ayah_tafsir(surah_number: int, ayah_number: int) -> dict:
    """جلب التفسير المعتمد لآية محددة من موسوعة التفسير بالدرر السنية."""
    url = f"{BASE_URL}/{surah_number}/{ayah_number}"
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        response = await client.get(url)
        if response.status_code != 200:
            return {"error": f"فشل الجلب من المصدر (رمز الحالة: {response.status_code})"}

        soup = BeautifulSoup(response.text, "html.parser")
        main_content = soup.find("div", class_="content") or soup.find("main") or soup
        text_blocks = [p.get_text(strip=True) for p in main_content.find_all(["p", "div"]) if p.get_text(strip=True)]
        parsed_text = "\n\n".join(text_blocks[:10]) if text_blocks else main_content.get_text(strip=True)

        return {
            "surah": surah_number,
            "ayah": ayah_number,
            "tafsir_text": parsed_text[:4000],
            "source": "موسوعة التفسير - الدرر السنية",
            "url": url
        }

@mcp.tool()
async def search_dorar_tafsir(query: str) -> dict:
    """البحث في محتوى موسوعة التفسير بموقع الدرر السنية عن لفظة أو جذر قرآني."""
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://dorar.net/search/tafsir?q={encoded_query}"
    
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        response = await client.get(search_url)
        if response.status_code != 200:
            return {"error": f"تعذر إجراء البحث (رمز الحالة: {response.status_code})"}

        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for item in soup.find_all("div", class_="search-result")[:5]:
            title = item.find("h3") or item.find("a")
            snippet = item.find("p") or item
            results.append({
                "title": title.get_text(strip=True) if title else "نتيجة بحث",
                "snippet": snippet.get_text(strip=True)[:300],
                "link": title.find("a")["href"] if title and title.find("a") else search_url
            })

        return {
            "query": query,
            "total_results": len(results),
            "results": results,
            "source": "الدرر السنية - محرك البحث"
        }

@mcp.tool()
async def compare_tafsir_sources(surah_number: int, ayah_number: int, keywords: str = "") -> dict:
    """أداة مخصصة للأطروحة: استخراج مادة التفسير ومقارنتها بالسياق النزولي واستعمالات السلف."""
    data = await get_ayah_tafsir(surah_number, ayah_number)
    if "error" in data:
        return data

    text = data.get("tafsir_text", "")
    found_keywords = [kw for kw in keywords.split() if kw in text] if keywords else []

    return {
        "surah": surah_number,
        "ayah": ayah_number,
        "raw_text": text,
        "highlighted_keywords": found_keywords,
        "analysis_hint": "استخرج أقوال السلف وقارن بين المعنى اللغوي الجاهلي والسياق النزولي.",
        "url": data.get("url")
    }

# 2. إنشاء تطبيق FastAPI
app = FastAPI(title="Dorar Tafsir MCP Endpoint")

# 3. إتاحة جميع طلبات الاتصال الخارجية (CORS) لحل مشكلة المنع من قبل ChatGPT وPerplexity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. تضمين واجهة MCP SSE
app.mount("/mcp", mcp.sse_app)

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>Dorar Tafsir MCP Endpoint</title>
        <style>
            body { font-family: system-ui, sans-serif; background: #f8fafc; color: #1e293b; padding: 40px; line-height: 1.6; }
            .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
            h1 { color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
            code { background: #f1f5f9; padding: 4px 8px; border-radius: 4px; color: #0f766e; font-weight: bold; }
            .endpoint-box { background: #ecfdf5; border: 1px solid #a7f3d0; padding: 15px; border-radius: 8px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>خادم Dorar Tafsir MCP العام</h1>
            <p>موصل معرفي سحابي لاستخراج نتائج التفسير وأقوال السلف من موسوعة <b>الدرر السنية</b> لخدمة أبحاث التطور الدلالي.</p>
            <div class="endpoint-box">
                <strong>رابط الموصل (MCP Endpoint):</strong><br>
                <code>https://dorar-tafsir-mcp-1.onrender.com/mcp/sse</code>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/search")
async def search(query: str):
    res = await search_dorar_tafsir(query)
    return res
