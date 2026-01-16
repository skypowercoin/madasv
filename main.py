from fastapi import FastAPI
import yfinance as yf
import asyncio
import os
import uvicorn

app = FastAPI()

# قائمة أهم أسهم بورصة إسطنبول (BIST 100) - قمت باختيار عينة كبيرة منها هنا
STOCKS = [
    "THYAO.IS", "ASELS.IS", "EREGL.IS", "KCHOL.IS", "SISE.IS", "GARAN.IS", "AKBNK.IS",
    "BIMAS.IS", "ISCTR.IS", "SAHOL.IS", "TUPRS.IS", "YKBNK.IS", "PETKM.IS", "SASA.IS",
    "HEKTS.IS", "PGSUS.IS", "ENKAI.IS", "TOASO.IS", "FROTO.IS", "ARCLK.IS", "ASTOR.IS",
    "KONTR.IS", "SMRTG.IS", "EUPWR.IS", "ALARK.IS", "GUBRF.IS", "ODAS.IS", "ZOREN.IS",
    "SKBNK.IS", "TSKB.IS", "HALKB.IS", "VAKBN.IS", "DOHOL.IS", "SOKM.IS", "MAVI.IS",
    "TCELL.IS", "TTKOM.IS", "AEFES.IS", "CCOLA.IS", "BAGFS.IS", "BRISA.IS", "KORDS.IS"
]

cached_data = []

async def fetch_bist_prices():
    global cached_data
    while True:
        try:
            # جلب البيانات لكل الرموز دفعة واحدة لسرعة الأداء
            symbols_string = " ".join(STOCKS)
            data = yf.download(tickers=symbols_string, period="1d", interval="1m", group_by='ticker', progress=False)
            
            new_prices = []
            for symbol in STOCKS:
                try:
                    # التحقق من وجود بيانات للسهم
                    if not data[symbol].empty:
                        current_price = data[symbol]['Close'].iloc[-1]
                        open_price = data[symbol]['Open'].iloc[0]
                        change = ((current_price - open_price) / open_price) * 100

                        new_prices.append({
                            "symbol": symbol.replace(".IS", ""),
                            "price": round(float(current_price), 2),
                            "change": round(float(change), 2)
                        })
                except:
                    continue # تخطي السهم إذا حدث خطأ في بياناته
            
            if new_prices:
                cached_data = new_prices
                print(f"تم تحديث {len(new_prices)} سهم من بورصة إسطنبول...")
        except Exception as e:
            print(f"خطأ عام: {e}")
        
        await asyncio.sleep(20) # زيادة المدة لـ 20 ثانية لتجنب الحظر مع قائمة كبيرة

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fetch_bist_prices())

@app.get("/market")
async def get_market():
    return cached_data

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
