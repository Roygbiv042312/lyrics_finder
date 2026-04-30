import streamlit as st
import requests

# Page configuration
st.set_page_config(
    page_title="Lyrics Finder",
    page_icon="🎵",
    layout="centered"
)

# App styles
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .song-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    .song-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .lyrics-box {
        background: #f8f9fa;
        border-left: 4px solid #764ba2;
        padding: 20px;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        max-height: 500px;
        overflow-y: auto;
        white-space: pre-wrap;
        line-height: 1.6;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 30px;
        font-weight: bold;
        border-radius: 25px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        color: white;
    }
    .search-header {
        text-align: center;
        margin-bottom: 30px;
    }
    .artist-name {
        color: #764ba2;
        font-size: 1.1em;
        margin-top: 5px;
    }
    .album-name {
        color: #666;
        font-size: 0.9em;
        font-style: italic;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if 'search_results' not in st.session_state:
    st.session_state['search_results'] = []
if 'current_query' not in st.session_state:
    st.session_state['current_query'] = ''
if 'song_selection' not in st.session_state:
    st.session_state['song_selection'] = 0

# Helper functions

def parse_search_response(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ('results', 'data', 'tracks', 'songs'):
            if key in payload and isinstance(payload[key], list):
                return payload[key]
    return []


def fetch_search_results(query):
    try:
        response = requests.get('https://lrclib.net/api/search', params={'q': query}, timeout=10)
        response.raise_for_status()
        return parse_search_response(response.json())
    except requests.RequestException as error:
        st.error(f'❌ API request failed: {error}')
        return None


def format_track_label(track):
    title = track.get('name', 'Unknown Title')
    artist = track.get('artistName', 'Unknown Artist')
    album = track.get('albumName', 'Unknown Album')
    instrumental = track.get('instrumental', False)
    has_lyrics = bool(track.get('plainLyrics'))

    label = f'{title} - {artist}'
    if album != 'Unknown Album':
        label += f' [{album}]'
    if instrumental:
        label += ' 🎵 [Instrumental]'
    elif not has_lyrics:
        label += ' 📝 [No Lyrics]'
    return label, {'instrumental': instrumental, 'has_lyrics': has_lyrics}

# Header
st.markdown('<div class="search-header">', unsafe_allow_html=True)
st.title('🎵 Lyrics Finder')
st.markdown("<h3 style='text-align: center; color: #fff;'>Find lyrics for your favorite songs</h3>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

query = st.text_input('', value=st.session_state['current_query'], placeholder='Search for a song (e.g., Bohemian Rhapsody, Shape of You...)')
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    submit = st.button('🔍 Find Lyrics', use_container_width=True)

if submit:
    if not query:
        st.warning('🔍 Please enter a song name to search!')
    else:
        with st.spinner('Searching for lyrics...'):
            results = fetch_search_results(query)

        if results is None:
            st.error('Please try again later.')
        elif len(results) == 0:
            st.warning('😕 No results found for your search query. Try different keywords!')
        else:
            st.session_state['search_results'] = results
            st.session_state['current_query'] = query
            if st.session_state['song_selection'] >= len(results):
                st.session_state['song_selection'] = 0

results = st.session_state['search_results']
if results:
    st.success(f"✨ Found {len(results)} result(s) for '{st.session_state['current_query']}'")
    st.markdown('### 🎤 Select a version:')

    options = []
    option_details = []
    for track in results:
        label, details = format_track_label(track)
        options.append(label)
        option_details.append({'track': track, **details})

    selected_index = st.radio(
        'Choose a version:',
        options=range(len(options)),
        format_func=lambda x: options[x],
        key='song_selection'
    )

    selected_track = results[selected_index]
    selected_info = option_details[selected_index]

    st.markdown('---')
    st.markdown('<div class="song-card">', unsafe_allow_html=True)

    left_col, right_col = st.columns([3, 1])
    with left_col:
        st.markdown(f"## 🎵 {selected_track.get('name', 'Unknown Title')}")
        st.markdown(
            f'<div class="artist-name">🎤 Artist: {selected_track.get("artistName", "Unknown Artist")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="album-name">💿 Album: {selected_track.get("albumName", "Unknown Album")}</div>',
            unsafe_allow_html=True,
        )

    with right_col:
        duration = selected_track.get('duration')
        if isinstance(duration, int) and duration > 0:
            mins, secs = divmod(duration, 60)
            st.metric('Duration', f'{mins}:{secs:02d}')

    if selected_info['instrumental']:
        st.warning('🎵 This is an instrumental track - no lyrics available')
    elif not selected_info['has_lyrics']:
        st.warning('📝 Lyrics not available for this version')
    else:
        lyrics = selected_track.get('plainLyrics', '')
        st.markdown('### 📜 Lyrics')
        st.markdown('<div class="lyrics-box">', unsafe_allow_html=True)
        st.text(lyrics)
        st.markdown('</div>', unsafe_allow_html=True)

        st.download_button(
            label='💾 Download Lyrics',
            data=lyrics,
            file_name=f"{selected_track.get('name', 'song')}_lyrics.txt",
            mime='text/plain',
        )

    st.markdown('</div>', unsafe_allow_html=True)

    if len(results) > 1:
        with st.expander('📋 Other versions available'):
            for idx, track in enumerate(results):
                if idx == selected_index:
                    continue
                song_name = track.get('name', 'Unknown Title')
                artist = track.get('artistName', 'Unknown Artist')
                album = track.get('albumName', 'Unknown Album')
                instrumental = track.get('instrumental', False)
                has_lyrics = bool(track.get('plainLyrics'))
                status = '🎵 Instrumental' if instrumental else ('📝 Has Lyrics' if has_lyrics else '❌ No Lyrics')
                st.write(f'• **{song_name}** - {artist} ({album}) - {status}')

# Footer
st.markdown('---')
st.markdown(
    "<p style='text-align: center; color: #fff; font-size: 0.8em;'>"
    "Powered by LRCLIB API | Find lyrics for your favorite songs 🎶"
    "</p>",
    unsafe_allow_html=True,
)
