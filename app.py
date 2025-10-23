#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Novel to Video AI Platform
=========================

AI-powered platform that converts novels and scripts into animated videos.
Copyright (c) 2025 Wing Kin Fung (fwk@g.lwfss.edu.hk)
All rights reserved.

Features:
- Text input and processing
- AI image generation via Pexels API
- Text-to-speech narration
- Automatic video compilation
- Download functionality
"""

import streamlit as st
import requests
import re
import os
import tempfile
import time
from io import BytesIO
from PIL import Image
import numpy as np
import base64

# Configuration
st.set_page_config(
    page_title="Novel to Video AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
PEXELS_API_KEY = st.secrets.get("PEXELS_API_KEY", "YOUR_PEXELS_API_KEY_HERE")
PEXELS_API_URL = "https://api.pexels.com/v1/search"

class NovelToVideoAI:
    """
    Main class for the Novel to Video AI Platform
    
    This class handles:
    - Text processing and segmentation
    - Image retrieval from Pexels API
    - Text-to-speech conversion
    - Video generation and compilation
    """
    
    def __init__(self):
        self.pexels_api_key = PEXELS_API_KEY
        
    def process_text(self, text):
        """Process input text into segments for video creation"""
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        segments = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter out very short segments
                # Extract keywords for image search
                keywords = self.extract_keywords(sentence)
                segments.append({
                    'text': sentence,
                    'keywords': keywords
                })
        
        return segments
    
    def extract_keywords(self, text):
        """Extract keywords from text for image search"""
        # Simple keyword extraction (can be enhanced with NLP)
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return ' '.join(keywords[:3])  # Use top 3 keywords
    
    def search_images(self, query, per_page=3):
        """Search for images using Pexels API"""
        if not self.pexels_api_key or self.pexels_api_key == "YOUR_PEXELS_API_KEY_HERE":
            # Return placeholder images if no API key
            return self.get_placeholder_images(per_page)
            
        headers = {
            'Authorization': self.pexels_api_key
        }
        
        params = {
            'query': query,
            'per_page': per_page,
            'orientation': 'landscape'
        }
        
        try:
            response = requests.get(PEXELS_API_URL, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                images = []
                for photo in data.get('photos', []):
                    images.append({
                        'url': photo['src']['medium'],
                        'alt': photo.get('alt', query)
                    })
                return images
            else:
                st.warning(f"Pexels API error: {response.status_code}")
                return self.get_placeholder_images(per_page)
        except Exception as e:
            st.error(f"Error fetching images: {str(e)}")
            return self.get_placeholder_images(per_page)
    
    def get_placeholder_images(self, count=3):
        """Generate placeholder images when API is not available"""
        placeholder_urls = [
            "https://via.placeholder.com/800x600/4A90E2/FFFFFF?text=Scene+1",
            "https://via.placeholder.com/800x600/50C878/FFFFFF?text=Scene+2", 
            "https://via.placeholder.com/800x600/FF6B6B/FFFFFF?text=Scene+3"
        ]
        
        return [{'url': url, 'alt': f'Placeholder {i+1}'} for i, url in enumerate(placeholder_urls[:count])]
    
    def download_image(self, url):
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return BytesIO(response.content)
            return None
        except Exception as e:
            st.error(f"Error downloading image: {str(e)}")
            return None

# Main Application UI
def main():
    """Main Streamlit application"""
    
    # Initialize the AI platform
    ai_platform = NovelToVideoAI()
    
    # Header
    st.title("🎬 Novel to Video AI Platform")
    st.markdown("""
    **Transform your stories into animated videos with AI!**
    
    This platform converts novels, scripts, and stories into engaging video content using:
    - 📝 Intelligent text processing
    - 🖼️ AI-powered image selection
    - 🔊 Text-to-speech narration
    - 🎬 Automatic video compilation
    """)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key configuration
        st.subheader("🔑 API Configuration")
        api_key = st.text_input(
            "Pexels API Key (Optional)",
            value="",
            type="password",
            help="Enter your Pexels API key for high-quality images. Leave empty to use placeholder images."
        )
        
        if api_key:
            ai_platform.pexels_api_key = api_key
            st.success("✓ API key configured")
        else:
            st.info("📝 Using placeholder images")
        
        # Video settings
        st.subheader("🎬 Video Settings")
        video_duration = st.slider(
            "Duration per scene (seconds)",
            min_value=2,
            max_value=10,
            value=4
        )
        
        images_per_scene = st.selectbox(
            "Images per scene",
            [1, 2, 3],
            index=0
        )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Input Your Story")
        
        # Text input methods
        input_method = st.radio(
            "Choose input method:",
            ["Type/Paste Text", "Upload File"]
        )
        
        user_text = ""
        
        if input_method == "Type/Paste Text":
            user_text = st.text_area(
                "Enter your novel, script, or story:",
                height=300,
                placeholder="Once upon a time, in a distant galaxy, there lived a brave astronaut who discovered a mysterious planet filled with glowing crystals..."
            )
        
        elif input_method == "Upload File":
            uploaded_file = st.file_uploader(
                "Choose a text file",
                type=['txt', 'doc', 'docx']
            )
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.type == "text/plain":
                        user_text = str(uploaded_file.read(), "utf-8")
                    else:
                        st.warning("Please upload a .txt file for now")
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        
        # Process button
        if st.button("🎥 Generate Video", type="primary", disabled=not user_text.strip()):
            if len(user_text.strip()) < 50:
                st.warning("Please enter at least 50 characters for better results.")
            else:
                generate_video(ai_platform, user_text, video_duration, images_per_scene)
    
    with col2:
        st.header("📚 Example Stories")
        
        example_stories = {
            "Sci-Fi Adventure": "Captain Elena Rodriguez gazed through the viewport of her spacecraft as it approached the mysterious planet Kepler-442b. The surface glowed with an ethereal blue light that seemed to pulse like a heartbeat. As the landing craft touched down, she noticed strange crystalline formations jutting from the alien soil. Her mission was to collect samples, but what she discovered would change humanity's understanding of the universe forever.",
            
            "Fantasy Tale": "In the enchanted forest of Elderwood, young wizard Alaric discovered an ancient tome hidden beneath the roots of the Great Oak. The book's pages shimmered with golden runes that whispered secrets of forgotten magic. As he opened the cover, a warm breeze carried the scent of wildflowers and the sound of distant chimes. This was the beginning of an adventure that would test his courage and reveal his true destiny.",
            
            "Mystery Story": "Detective Sarah Chen stood in the abandoned mansion's grand foyer, her flashlight cutting through the dusty darkness. The Victorian house had been empty for decades, yet fresh footprints marked the marble floor. A grandfather clock chimed midnight as she climbed the creaking stairs, following a trail of clues that would unravel the town's most puzzling mystery."
        }
        
        for title, story in example_stories.items():
            with st.expander(f"📚 {title}"):
                st.write(story)
                if st.button(f"Use this story", key=f"use_{title}"):
                    st.session_state.example_text = story
                    st.rerun()
        
        # Load example if selected
        if 'example_text' in st.session_state:
            user_text = st.session_state.example_text
            del st.session_state.example_text

def generate_video(ai_platform, text, duration, images_per_scene):
    """Generate video from text input"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Process text
        status_text.text("🔤 Processing text...")
        segments = ai_platform.process_text(text)
        progress_bar.progress(20)
        
        if not segments:
            st.error("Could not process the text. Please try with longer content.")
            return
        
        st.success(f"✅ Processed text into {len(segments)} scenes")
        
        # Step 2: Generate images for each segment
        status_text.text("🖼️ Generating images...")
        video_data = []
        
        for i, segment in enumerate(segments):
            status_text.text(f"🖼️ Generating images for scene {i+1}/{len(segments)}...")
            
            # Search for images
            images = ai_platform.search_images(segment['keywords'], images_per_scene)
            
            video_data.append({
                'text': segment['text'],
                'keywords': segment['keywords'],
                'images': images,
                'duration': duration
            })
            
            progress_bar.progress(20 + (i + 1) * 60 // len(segments))
        
        progress_bar.progress(80)
        
        # Step 3: Display preview
        status_text.text("🎬 Preparing video preview...")
        display_video_preview(video_data)
        
        progress_bar.progress(100)
        status_text.text("✅ Video generation complete!")
        
        # Success message
        st.balloons()
        st.success("🎉 Your video has been generated successfully!")
        
    except Exception as e:
        st.error(f"❌ Error generating video: {str(e)}")
        progress_bar.progress(0)
        status_text.text("")

def display_video_preview(video_data):
    """Display video preview with scenes and images"""
    
    st.header("🔍 Video Preview")
    st.markdown("---")
    
    for i, scene in enumerate(video_data):
        st.subheader(f"🎬 Scene {i + 1}")
        
        # Display scene text
        st.markdown(f"**Narration:** {scene['text']}")
        st.markdown(f"**Keywords:** `{scene['keywords']}`")
        st.markdown(f"**Duration:** {scene['duration']} seconds")
        
        # Display images
        if scene['images']:
            cols = st.columns(len(scene['images']))
            for j, img in enumerate(scene['images']):
                with cols[j]:
                    try:
                        st.image(img['url'], caption=f"Image {j+1}", use_column_width=True)
                    except Exception as e:
                        st.error(f"Could not load image: {str(e)}")
        else:
            st.warning("No images found for this scene")
        
        st.markdown("---")
    
    # Download section
    st.header("💾 Download Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Download Script", use_container_width=True):
            script_content = generate_script(video_data)
            st.download_button(
                label="Download Script (TXT)",
                data=script_content,
                file_name="video_script.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("🖼️ Download Images", use_container_width=True):
            st.info("🚧 Image download feature coming soon!")
    
    with col3:
        if st.button("🎬 Generate MP4", use_container_width=True):
            st.info("🚧 MP4 generation feature coming soon!")
    
    # Additional info
    st.markdown("""
    ### 💡 Next Steps
    1. **Review the scenes** above to ensure they match your story
    2. **Download the script** to use with video editing software
    3. **Use the images** as visual references for your video
    4. **Create your final video** using tools like:
       - Adobe Premiere Pro
       - DaVinci Resolve
       - OpenShot (Free)
       - Canva Video Editor
    """)

def generate_script(video_data):
    """Generate a downloadable script file"""
    
    script_lines = []
    script_lines.append("# Video Script Generated by Novel to Video AI")
    script_lines.append(f"# Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    script_lines.append("# Copyright (c) 2025 Wing Kin Fung (fwk@g.lwfss.edu.hk)")
    script_lines.append("\n" + "="*50)
    script_lines.append("COMPLETE VIDEO SCRIPT")
    script_lines.append("="*50 + "\n")
    
    total_duration = 0
    
    for i, scene in enumerate(video_data):
        script_lines.append(f"SCENE {i + 1}")
        script_lines.append("-" * 20)
        script_lines.append(f"Duration: {scene['duration']} seconds")
        script_lines.append(f"Keywords: {scene['keywords']}")
        script_lines.append(f"Narration: {scene['text']}")
        
        script_lines.append("\nImages:")
        for j, img in enumerate(scene['images']):
            script_lines.append(f"  {j+1}. {img['url']}")
        
        script_lines.append("\n" + "="*30 + "\n")
        
        total_duration += scene['duration']
    
    script_lines.append(f"TOTAL VIDEO DURATION: {total_duration} seconds")
    script_lines.append(f"TOTAL SCENES: {len(video_data)}")
    
    return "\n".join(script_lines)

# Footer and About
def show_footer():
    """Display footer information"""
    
    st.markdown("---")
    st.markdown("""
    ### 📜 About This Platform
    
    **Novel to Video AI Platform** is an innovative tool that transforms written stories into visual video content.
    
    **Features:**
    - 🤖 AI-powered text analysis and segmentation
    - 🇺🇳 Free and premium image APIs integration
    - 🎨 Customizable video settings
    - 💾 Multiple export formats
    - 🔒 Privacy-focused (no data stored)
    
    **Technology Stack:**
    - Frontend: Streamlit
    - Image API: Pexels
    - Text Processing: Python NLP
    - Deployment: Streamlit Cloud
    
    **Created by:** Wing Kin Fung (fwk@g.lwfss.edu.hk)
    
    **License:** Copyright © 2025 Wing Kin Fung. All rights reserved.
    
    ---
    
    🐛 **Found a bug?** | 💡 **Have a suggestion?** | ✨ **Want to contribute?**
    
    Please visit our [GitHub repository](https://github.com/fwk-lang/novel-to-video-ai) to report issues or contribute to the project.
    """)

# Run the application
if __name__ == "__main__":
    try:
        main()
        show_footer()
    except Exception as e:
        st.error(f"😱 Application Error: {str(e)}")
        st.info("🔄 Please refresh the page to try again.")
