from fastapi import FastAPI
import yfinance as yf
import asyncio
import os
import uvicorn
from fastapi.responses import JSONResponse

app = FastAPI()

STOCKS = [
    "THYAO.IS", "ASELS.IS", "EREGL.IS", "KCHOL.IS", "SISE.IS", "GARAN.IS", "AKBNK.IS",
    "BIMAS.IS", "ISCTR.IS", "SAHOL.IS", "TUPRS.IS", "YKBNK.IS", "PETKM.IS", "SASA.IS",
    "HEKTS.IS", "PGSUS.IS", "ENKAI.IS", "TOASO.IS", "FROTO.IS", "ARCLK.IS", "ASTOR.IS",
    "KONTR.IS", "SMRTG.IS", "EUPWR.IS", "ALARK.IS", "GUBRF.IS", "ODAS.IS", "ZOREN.IS",
    "SKBNK.IS", "TSKB.IS", "HALKB.IS", "VAKBN.IS", "DOHOL.IS", "SOKM.IS", "MAVI.IS",
    "TCELL.IS", "TTKOM.IS", "AEFES.IS", "CCOLA.IS", "BAGFS.IS", "BRISA.IS", "KORDS.IS"
]

# استخدام قاموس بسيط للتخزين لضمان السرعة
cached_data = []

async def fetch_bist_prices():
    global cached_data
    symbols_string = " ".join(STOCKS)
    
    while True:
        try:
            # استخدام Threads لأن yf.download عملية حاصرة (Blocking)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: yf.download(
                tickers=symbols_string, 
                period="1d", 
                interval="1m", 
                group_by='ticker', 
                auto_adjust=True, 
                progress=False
            ))
            
            new_prices = []
            for symbol in STOCKS:
                try:
                    # التحقق من أن السهم موجود في البيانات المستلمة
                    if symbol in data.columns.levels[0] and not data[symbol].empty:
                        # تحويل القيم لـ float عادي لضمان توافق JSON
                        current_price = float(data[symbol]['Close'].iloc[-1])
                        open_price = float(data[symbol]['Open'].iloc[0])
                        
                        if open_price > 0:
                            change = ((current_price - open_price) / open_price) * 100
                        else:
                            change = 0

                        new_prices.append({
                            "symbol": symbol.replace(".IS", ""),
                            "price": round(current_price, 2),
                            "change": round(float(change), 2)
                        })
                except Exception:
                    continue 
            
            if new_prices:
                cached_data = new_prices
                print(f"✅ تم تحديث {len(new_prices)} سهم بنجاح")
                
        except Exception as e:
            print(f"❌ خطأ أثناء جلب البيانات: {e}")
        
        # انتظر 30 ثانية لتجنب حظر IP السيرفر من ياهو
        await asyncio.sleep(30)

@app.on_event("startup")
async def startup_event():
    # تشغيل مهمة الخلفية
    asyncio.create_task(fetch_bist_prices())

@app.get("/market")
async def get_market():
    # استخدام JSONResponse لضمان عدم حدوث خطأ 500 في الـ ASGI
    return JSONResponse(content={"status": "success", "data": cached_data})

@app.get("/")
async def root():
    return {"message": "API is Running", "count": len(cached_data)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


