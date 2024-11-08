import streamlit as st
import subprocess
import os
from dotenv import load_dotenv
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import base64

# Fixed agent ID for CodeGPT
AGENT_ID = "403d73ce-4400-4020-8164-d2bbef542186"

def download_button(content, filename, button_text):
    """Generates a download button for the content"""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}" class="download-button">{button_text}</a>'
    return href

class FileHandler(FileSystemEventHandler):
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.files_content = {}

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            try:
                with open(event.src_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.files_content[os.path.basename(event.src_path)] = content
            except Exception as e:
                print(f"Error reading file: {e}")

def save_env_vars(api_key):
    """Save environment variables to .env file"""
    with open('.env', 'w') as f:
        f.write(f'CODEGPT_API_KEY={api_key}\n')
        f.write(f'AGENT_ID={AGENT_ID}\n')

def run_scraper(url, status_container, files_container):
    """Execute the Node.js scraper with real-time updates"""
    try:
        # Create output directory
        domain = url.replace('https://', '').replace('http://', '').split('/')[0]
        output_dir = os.path.join('out', domain)
        os.makedirs(output_dir, exist_ok=True)

        # Set up file monitoring
        event_handler = FileHandler(output_dir)
        observer = Observer()
        observer.schedule(event_handler, output_dir, recursive=False)
        observer.start()

        # Create placeholders
        file_placeholder = files_container.empty()
        combined_content = ""

        process = subprocess.Popen(
            ['node', 'crawler.mjs', url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                status_container.write(output.strip())
            
            # Update content display
            if event_handler.files_content:
                combined_content = ""
                for filename, content in sorted(event_handler.files_content.items()):
                    combined_content += f"## 📄 {filename}\n```\n{content}\n```\n\n"
                
                # Display content
                file_placeholder.markdown(combined_content)
                
                # Update the download button
                download_link = download_button(
                    combined_content,
                    f"scraped_content_{domain}.txt",
                    "⬇️ Download Content"
                )
                files_container.markdown(download_link, unsafe_allow_html=True)

            time.sleep(0.1)

        observer.stop()
        observer.join()
        return process.poll()

    except Exception as e:
        st.error(f"Error running scraper: {str(e)}")
        return 1

def main():
    st.set_page_config(
        page_title="Web Scraper AI with CodeGPT",
        page_icon="🕷️",
        layout="wide"
    )
    
    # Add custom CSS for the download button
    st.markdown("""
        <style>
        .download-button {
            display: inline-block;
            padding: 0.5em 1em;
            color: white;
            background-color: #4CAF50;
            border-radius: 4px;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
            margin: 0.5em 0;
        }
        .download-button:hover {
            background-color: #45a049;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🕷️ Web Scraper AI with CodeGPT")
    
    # Add agent information
    st.sidebar.title("Information")
    st.sidebar.info("""
    This scraper uses CodeGPT to process and analyze web content.
    
    **Configured Agent ID:**  
    ```
    403d73ce-4400-4020-8164-d2bbef542186
    ```
    """)
    
    # Main layout columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Configuration")
        api_key = st.text_input(
            "CodeGPT API Key:",
            type="password",
            help="Enter your CodeGPT API Key",
            key="api_key_input"
        )
        
        url = st.text_input(
            "Base URL for scraping:",
            help="Enter the complete URL (example: https://example.com)",
            key="url_input"
        )
        
        # URL validation
        url_valid = url.startswith(('http://', 'https://')) if url else False
        
        if not url_valid and url:
            st.warning("Please enter a valid URL starting with http:// or https://")
        
        start_button = st.button(
            "🚀 Start Scraping",
            disabled=not (api_key and url_valid),
            key="start_scraping_button"
        )

    with col2:
        st.markdown("### Scraped Content")
        # Containers for real-time updates
        status_container = st.empty()
        files_container = st.empty()
        
        if start_button:
            save_env_vars(api_key)
            
            with st.spinner('Initializing scraper...'):
                result = run_scraper(url, status_container, files_container)
                
            if result == 0:
                st.success("✅ Scraping completed successfully!")
            else:
                st.error("❌ There was an error during scraping")

    # Usage instructions in sidebar
    with st.sidebar.expander("ℹ️ Usage Instructions"):
        st.markdown("""
        1. Enter your CodeGPT API Key
        2. Enter the base URL to analyze
        3. Click "Start Scraping"
        4. Watch the results appear in real-time
        5. Use the download button to download the scraped content
        
        **Note:** The process duration depends on the site size.
        """)

if __name__ == "__main__":
    main()
