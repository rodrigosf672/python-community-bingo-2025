import json
import asyncio
from pyscript import document, window
from pyodide.ffi import create_proxy

# Bingo squares' text

SQUARES = [
    "Attended a Python local meetup", "Won a book in a raffle or event", "Put new stickers on my laptop", "Gave or attended a talk or workshop", "Became friends with Pythonists",
    "Visited a new city thanks to Python", "Donated to the PSF", "Contributed to open source", "Volunteered at a Python event", "Helped someone learn Python",
    "Learned a new Python library", "Got cool swag from a sponsor", "Love for Python", "Expressed public thanks to someone in the community", "Collaborated on a Python project",
    "Attended a Python conference", "Joined a Python community online", "Donated to a Python community initiative", "Asked my employer to sponsor a Python event", "Felt inspired by a talk",
    "Mentored or was mentored", "Asked a question at an event", "Supported a Python diversity initiative", "Tried a new Python tool", "Felt proud to be part of the Python community"
]

STORAGE_KEY = "python_community_bingo_state"

# State management

def load_state():
    stored = window.localStorage.getItem(STORAGE_KEY)
    if stored:
        try:
            return json.loads(stored)
        except:
            pass
    # Default state: Center square (index 12) is checked (Love for Python)!
    return [False] * 12 + [True] + [False] * 12

def save_state(state):
    window.localStorage.setItem(STORAGE_KEY, json.dumps(state))

# Global state
current_state = load_state()

# Logic

def check_bingo(state):
    # Rows
    for r in range(5):
        if all(state[r*5 + c] for c in range(5)):
            return True
    # Cols
    for c in range(5):
        if all(state[r*5 + c] for r in range(5)):
            return True
    # Diagonals
    if all(state[i*6] for i in range(5)): # 0, 6, 12, 18, 24
        return True
    if all(state[i*4 + 4] for i in range(5)): # 4, 8, 12, 16, 20
        return True
    return False


# Helpter functions

def celebrate():
    # Show banner
    banner = document.getElementById("celebration-banner")
    banner.classList.remove("hidden")
    
    # Fire confetti
    window.confetti()

def on_square_click(index, element):
    if index == 12: return # Center square is permanent
    
    # Toggle state
    current_state[index] = not current_state[index]
    save_state(current_state)
    
    # Update UI
    if current_state[index]:
        element.classList.add("checked")
        element.classList.add("bingo-pop")
    else:
        element.classList.remove("checked")
        element.classList.remove("bingo-pop")
    # Check Bingo
    if check_bingo(current_state):
        celebrate()
    else:
        # Hide banner if bingo is lost (unchecking a square)
        document.getElementById("celebration-banner").classList.add("hidden")

# UI renderering

def render_grid():
    grid = document.getElementById("bingo-grid")
    grid.innerHTML = ""
    
    for i, text in enumerate(SQUARES):
        square = document.createElement("div")
        square.className = "bingo-square"
        square.innerText = text
        
        if i == 12:
            square.classList.add("center-square")
        
        if current_state[i]:
            square.classList.add("checked")
            
        # Bind click event
        # We need to capture 'i' and 'square' correctly in the closure
        def make_handler(idx, elem):
            def handler(e):
                on_square_click(idx, elem)
            return handler
            
        square.onclick = create_proxy(make_handler(i, square))
        grid.appendChild(square)

# Button handler functions

def on_reset(e):
    global current_state
    # Keep center square checked
    current_state = [False] * 12 + [True] + [False] * 12
    save_state(current_state)
    render_grid()
    document.getElementById("celebration-banner").classList.add("hidden")

SHARE_TEXT = """I'm celebrating the Python community with this Bingo game! 🐍✨

Play here: https://python-bingo.netlify.app/

I'm thankful to the PSF for all the experiences and support. I encourage all to donate and support our ecosystem: https://donate.python.org/

#Python #SupportPSF #PSF"""

def on_share_click(e):
    modal = document.getElementById("social-share-overlay")
    modal.classList.remove("hidden")
    
    # Fill textarea
    document.getElementById("share-text-area").value = SHARE_TEXT
    encoded_text = window.encodeURIComponent(SHARE_TEXT)
    
    # Twitter/X
    document.getElementById("share-twitter").href = f"https://twitter.com/intent/tweet?text={encoded_text}"
    # LinkedIn
    document.getElementById("share-linkedin").href = f"https://www.linkedin.com/feed/?shareActive=true&text={encoded_text}"

def on_close_modal(e):
    document.getElementById("social-share-overlay").classList.add("hidden")

def on_copy_text(e):
    textarea = document.getElementById("share-text-area")
    textarea.select()
    textarea.setSelectionRange(0, 99999) # For mobile devices

    # Try modern clipboard API
    try:
        window.navigator.clipboard.writeText(textarea.value)
    except Exception:
        # Fallback
        document.execCommand("copy")
        
    # Simple visual feedback
    btn = document.getElementById("modal-copy-btn")
    original_html = "📋"
    btn.innerHTML = "✅"
    def reset_text():
        btn.innerHTML = original_html
    window.setTimeout(create_proxy(reset_text), 2000)

async def on_download(e):
    element = document.getElementById("capture-area")
    
    # Capture original aspect ratio
    canvas = await window.html2canvas(element, window.Object.fromEntries([["backgroundColor", "#0f172a"]]))
    
    # Create square canvas
    max_dim = max(canvas.width, canvas.height)
    # Add some padding
    padding = 40
    final_dim = max_dim + (padding * 2)
    
    square_canvas = document.createElement("canvas")
    square_canvas.width = final_dim
    square_canvas.height = final_dim
    ctx = square_canvas.getContext("2d")
    
    # Fill background
    ctx.fillStyle = "#0f172a"
    ctx.fillRect(0, 0, final_dim, final_dim)
    
    # Draw original centered
    x_offset = (final_dim - canvas.width) / 2
    y_offset = (final_dim - canvas.height) / 2
    ctx.drawImage(canvas, x_offset, y_offset)
    
    # Create link to download
    link = document.createElement('a')
    link.download = 'python_bingo.png'
    link.href = square_canvas.toDataURL()
    link.click()

# Initialization
async def main():
    # Set intro text
    document.getElementById("intro-title").innerText = "Welcome to the Python Holiday Bingo!"
    document.getElementById("intro-body").innerText = "Celebrate the end of 2025 by marking off your Python community achievements. This is a community initiative in support of the Python Software Foundation (PSF). Can you get a bingo? Share your card and consider donating to support our ecosystem!"
    render_grid()
    
    # Event Listeners
    document.getElementById("reset-btn").onclick = create_proxy(on_reset)
    document.getElementById("share-btn").onclick = create_proxy(on_share_click)
    document.getElementById("modal-download-btn").onclick = create_proxy(on_download)
    document.getElementById("close-modal").onclick = create_proxy(on_close_modal)
    document.getElementById("modal-copy-btn").onclick = create_proxy(on_copy_text)
    
    # Close modal on clicking outside
    def on_window_click(e):
        modal = document.getElementById("social-share-overlay")
        if e.target == modal:
            modal.classList.add("hidden")
            
    window.onclick = create_proxy(on_window_click)
    
    # Initial bingo check (in case restored state has bingo)
    if check_bingo(current_state):
        celebrate()

asyncio.ensure_future(main())
