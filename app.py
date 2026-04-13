import streamlit as st
import requests

st.title("BababouiBox")
st.write("Kanta lang boss")

query = st.text_input("search ka kanta")
submit = st.button("Confirm")

if submit and query:  
    search_url = "https://lrclib.net/api/search"
    params = {"q": query}
    response = requests.get(search_url, params=params)
    
    if response.status_code == 200:
        result = response.json()
        
        if result and len(result) > 0:
            track = result[0]
            
            if 'plainLyrics' in track and not track.get('instrumental', False):
                st.markdown("---")
                st.subheader({track.get('name', 'Unknown Title')})
                st.write(f"**Artist:** {track.get('artistName', 'Unknown Artist')}")
                st.write(f"**Album:** {track.get('albumName', 'Unknown Album')}")
                
                st.markdown("### Lyrics")
                st.text(track['plainLyrics']) 
                
            else:
                st.warning("Lyrics not available for the top result.")
        else:
            st.write("No results found for the search query.")
    else:
        st.error(f"API request failed with status code {response.status_code}.")