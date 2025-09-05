#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fastmcp import FastMCP
import uvicorn
import time

# FastAPI 앱 생성
app = FastAPI(title="Entry Studio API", version="1.0.0")

class CodeRequest(BaseModel):
    code: str

class WebDriverManager:
    def __init__(self):
        self.driver = None
        self._initialize_driver()
    
    def _initialize_driver(self):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://playentry.org/ws/new?type=normal&mode=block&lang=ko")
        time.sleep(5)
    
    def execute_js(self, script: str):
        if not self.driver:
            raise Exception("WebDriver not initialized")
        return self.driver.execute_script(script)
    
    def close(self):
        if self.driver:
            self.driver.quit()

# 전역 WebDriver 인스턴스
driver_manager = WebDriverManager()

@app.get("/editor/code")
def get_code():
    """현재 에디터의 코드를 가져옵니다"""
    try:
        code = driver_manager.execute_js("return Entry.getMainWS().vimBoard.codeMirror.getValue()")
        return {"code": code or ""}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/editor/code")
def set_code(request: CodeRequest):
    """에디터의 코드를 설정합니다"""
    try:
        script = f"Entry.getMainWS().vimBoard.codeMirror.setValue({repr(request.code)})"
        driver_manager.execute_js(script)
        return {"message": "코드 설정 완료"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/editor/insert")
def insert_code(request: CodeRequest):
    """현재 커서 위치에 코드를 삽입합니다"""
    try:
        script = f"Entry.getMainWS().vimBoard.codeMirror.replaceSelection({repr(request.code)})"
        driver_manager.execute_js(script)
        return {"message": "코드 삽입 완료"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/editor/cursor")
def get_cursor():
    """현재 커서 위치를 가져옵니다"""
    try:
        cursor = driver_manager.execute_js("return Entry.getMainWS().vimBoard.codeMirror.getCursor()")
        return {"cursor": cursor}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/editor/focus")
def focus_editor():
    """에디터에 포커스를 설정합니다"""
    try:
        driver_manager.execute_js("Entry.getMainWS().vimBoard.codeMirror.focus()")
        return {"message": "에디터 포커스 완료"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# FastAPI를 MCP로 변환하고 HTTP 앱 생성
mcp = FastMCP.from_fastapi(app=app)
mcp_app = mcp.http_app(path='/sse')

# 메인 FastAPI 앱에 MCP 마운트
main_app = FastAPI(title="Entry Studio", lifespan=mcp_app.lifespan)
main_app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    try:
        uvicorn.run(main_app, host="0.0.0.0", port=8080)
    finally:
        driver_manager.close()