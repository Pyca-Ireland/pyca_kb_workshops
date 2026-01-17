import re

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import markdown

from main import search_events


def linkify_urls(text: str) -> str:
    """Convert plain URLs to clickable hyperlinks."""
    url_pattern = r'(https?://[^\s<>"]+)'
    return re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', text)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, topic: str = Form(...)):
    # Run the browser agents
    md_result = await search_events(topic)

    # Convert markdown to HTML (nl2br converts newlines to <br>)
    html_result = markdown.markdown(md_result, extensions=['nl2br'])
    html_result = linkify_urls(html_result)

    return f"""
    <div class="results-content">
        {html_result}
    </div>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
