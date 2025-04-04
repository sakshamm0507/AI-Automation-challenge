import google.generativeai as genai
import speech_recognition as sr
from googleapiclient.discovery import build
import datetime

def get_speech_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your query (Hindi/English)...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            query = recognizer.recognize_google(audio, language="hi-IN")  # Supports Hindi/English
            print(f"You said: {query}")
            return query
        except sr.UnknownValueError:
            print("Sorry, could not understand the audio.")
        except sr.RequestError:
            print("Error connecting to the speech recognition service.")
    return None

def youtube_search(api_key, query, max_results=5):
    youtube = build("youtube", "v3", developerKey=api_key)
    try:
        search_response = youtube.search().list(
            q=query,
            type="video",
            part="id,snippet",
            maxResults=max_results
        ).execute()
        return search_response.get("items", [])
    except Exception as e:
        print(f"Error fetching YouTube results: {e}")
        return []

def analyze_and_reorder_videos(api_key, videos):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-pro-flash')
    try:
        video_data = "\n".join(
            [f"Title: {video['snippet']['title']}\nDescription: {video['snippet']['description']}" for video in videos]
        )
        prompt = f"""
        Analyze the following YouTube videos based on their titles and descriptions:
        {video_data}
        Provide a short description for each video after analyzing, not the exact description but oberve timestamps, #, etc and give around 20 word description and reorder them based on relevance and quality.
        Return the reordered list in the format:
        Title: <title>
        Description: <short description>
        """
        response = model.generate_content(prompt)
        reordered_videos = response.text.strip().split("\n\n")
        return reordered_videos
    except Exception as e:
        print(f"Error analyzing and reordering videos: {e}")
        return videos

if __name__ == "__main__":
    API_KEY = " "
    GEMINI_API_KEY = " "
    # Set API Keys

    # Ask user for input method
    input_method = input("Do you want to provide input via text or voice? (text/voice): ").strip().lower()
    if input_method == "voice":
        query = get_speech_input()
    else:
        query = input("Enter your search query: ")

    if not query:
        print("No valid query provided. Exiting.")
        exit()

    num_results = int(input("How many search results do you want? "))

    print(f"\nFetching results for query: {query}")
    results = youtube_search(API_KEY, query, max_results=num_results)

    if not results:
        print("No results found. Exiting.")
        exit()

    reordered_results = analyze_and_reorder_videos(GEMINI_API_KEY, results)

    print("\n--- Optimized YouTube Video Results ---")
    for video in reordered_results:
        print(f"Title: {video['snippet']['title']}")
        print(f"URL: https://www.youtube.com/watch?v={video['id']['videoId']}")
        print(f"Description: {video['snippet']['description']}")
        print("-" * 40)
