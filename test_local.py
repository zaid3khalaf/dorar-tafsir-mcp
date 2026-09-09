import asyncio
from app import get_ayah

async def main():
    result = await get_ayah(20, 5)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
