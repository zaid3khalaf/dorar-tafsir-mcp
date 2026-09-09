import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Dorar Tafsir API",
    description="API لتفسير القرآن الكريم والبحث في الألفاظ لأغراض البحث الأكاديمي",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", summary="التحقق من حالة السيرفر")
async def root():
    return {"status": "ok", "message": "Dorar Tafsir API is running"}

@app.get("/tafsir", summary="جلب تفسير آية قرآنية")
async def get_ayah_tafsir(surah_number: int, ayah_number: int):
    """جلب التفسير المعتمد لآية محددة عبر رقم السورة ورقم الآية."""
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
                    "source": "التفسير الميسر",
                    "status": "success"
                }
            return {"error": f"تعذر الجلب (رمز الحالة: {res.status_code})"}
        except Exception as e:
            return {"error": str(e)}

@app.get("/search", summary="البحث في الألفاظ والتفاسير")
async def search_dorar_tafsir(query: str):
    """البحث عن الكلمات والجذور اللغوية في النصوص القرآنية والتفسيرية."""
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
                    "results": parsed_results
                }
            return {"error": f"خطأ في البحث: {res.status_code}"}
        except Exception as e:
            return {"error": str(e)}
