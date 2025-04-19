import argparse
import re
import os
import google.generativeai as genai
from dotenv import load_dotenv

def parse_srt(srt_path):
    """Parse an SRT file and extract subtitle text."""
    
    with open(srt_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Pattern to extract subtitle text (ignoring timecodes and index numbers)
    # This handles both Windows (CRLF) and Unix (LF) line endings
    pattern = r'\d+\s+\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\s+(.*?)(?=\s*\n\s*\n|\s*$)'
    
    # Extract all subtitle text sections
    matches = re.findall(pattern, content, re.DOTALL)
    
    # Clean up subtitle text (remove HTML tags and join)
    clean_text = []
    for match in matches:
        # Remove HTML tags if any
        text = re.sub(r'<[^>]+>', '', match)
        # Replace line breaks with spaces
        text = re.sub(r'\n', ' ', text)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        clean_text.append(text.strip())
    
    return " ".join(clean_text)

def generate_description_with_hashtags(subtitle_text, api_key):
    """Generate a description and hashtags based on subtitle text using Gemini API."""
    
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    
    try:
        # Use the specified model - gemini-2.0-flash
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Define the prompt
        prompt = f"""
        Based on the following subtitles from a video, generate:
        
        1. A concise and descriptive summary that could serve as a description for the video. 
           Focus on the main topics, themes, and content of the video. 
           The description should be 2-3 paragraphs long.
        
        2. A list of 10 relevant hashtags related to the video content. These should be presented 
           as a single line of hashtags at the end of the description, each starting with #.
        
        SUBTITLES:
        {subtitle_text}
        
        Format your response with the description first, followed by a blank line, and then the hashtags.
        """
        
        # Generate the description with hashtags
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        print(f"Error during API call: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if your API key is correct")
        print("2. Make sure you have access to the gemini-2.0-flash model")
        print("3. Check your internet connection")
        raise

def main():
    parser = argparse.ArgumentParser(description='Generate video descriptions and hashtags from SRT subtitle files using Gemini API')
    parser.add_argument('srt_file', type=str, help='Path to the .srt subtitle file')
    parser.add_argument('--output', '-o', type=str, help='Path to save the generated description (optional)')
    parser.add_argument('--api_key', '-k', type=str, help='Gemini API key (optional if set in .env file)')
    
    args = parser.parse_args()
    
    # Load API key from .env file if not provided as argument
    load_dotenv()
    api_key = args.api_key or os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("Error: Gemini API key is required. Provide it with --api_key or set GEMINI_API_KEY in .env file.")
        return
    
    # Parse the SRT file
    try:
        subtitle_text = parse_srt(args.srt_file)
        print(f"Successfully extracted text from {args.srt_file}")
        
        # Check if we have enough content to work with
        if len(subtitle_text.split()) < 10:
            print("Warning: Very little text found in subtitles. Results may not be optimal.")
        
        # Generate description with hashtags
        result = generate_description_with_hashtags(subtitle_text, api_key)
        print("\nGenerated Description with Hashtags:")
        print(result)
        
        # Save to file if output path provided
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"\nDescription and hashtags saved to {args.output}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()