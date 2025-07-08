# Studify - Spotify Top Artists Visualizer

A Flask web application that connects to the Spotify API to display your current top artists with beautiful genre-based color coding and detailed statistics.

## Features

- **Spotify OAuth Integration** - Secure login with Spotify
- **Genre-based Color Coding** - Each artist gets a unique color based on their genres
- **Artist Statistics** - View popularity scores, follower counts, and top tracks
- **Artist Images** - Display official artist photos from Spotify
- **Responsive Design** - Works on desktop and mobile devices
- **Automatic Token Refresh** - Handles Spotify token expiration automatically

## Screenshots

The app displays your top artists in a beautiful grid layout with:
- Artist images
- Popularity and follower statistics
- Top tracks from each artist
- Direct links to open artists in Spotify

## Prerequisites

Before running this application, you need:

- Python 3.7+
- A Spotify Developer Account
- Spotify App credentials (Client ID and Client Secret)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/iris1615/studify.git
cd studify
```

### 2. Create Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click "Create App"
3. Fill in the app details:
   - **App Name**: Studify (or your preferred name)
   - **App Description**: Personal Spotify top artists visualizer
   - **Redirect URI**: `http://127.0.0.1:5000/callback`
4. Save your **Client ID** and **Client Secret**

### 3. Environment Setup

Create a `.env` file in the project root:

```env
CLIENT_ID="your_spotify_client_id_here"
CLIENT_SECRET="your_spotify_client_secret_here"
REDIRECT_URI="http://127.0.0.1:5000/callback"
```

### 4. Install Dependencies

```bash
pip install flask requests python-dotenv
```

## Usage

### Running the Application

1. Start the Flask server:
```bash
python main.py
```

2. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

3. Click "Login with Spotify" and authorize the application

4. View your top artists at:
```
http://127.0.0.1:5000/top-artists
```

### Available Endpoints

- `/` - Home page with login link
- `/login` - Initiates Spotify OAuth flow
- `/callback` - Handles Spotify OAuth callback
- `/top-artists` - Displays your top artists (main feature)
- `/playlists` - Returns your playlists as JSON
- `/refresh-token` - Refreshes expired access tokens

## Project Structure

```
studify/
├── main.py                 # Main Flask utilities
├── .env                   # Environment variables (create this)
├── .gitattributes         # Git configuration
├── static/
│   └── css/
│       └── top-artists.css # Styling for the top artists page
└── templates/
    └── top-artists.html   # HTML template for displaying artists
```

## Key Files

- **[main.py](main.py)** - Main Flask application with Spotify OAuth and API integration
- **[templates/top-artists.html](templates/top-artists.html)** - Jinja2 template for artist display
- **[static/css/top-artists.css](static/css/top-artists.css)** - CSS styling for the artist cards

## Genre Color Mapping

The application includes 30 predefined genre colors in the [`spotify_genres`](main.py) dictionary, including:

- Pop → Light Pink
- Hip Hop → Light Orange  
- Rock → Light Blue
- Indie → Light Green
- And many more...

Artists without defined genres get a default alternative color (#8D99AE).

## Spotify API Permissions

The app requests the following scopes:
- `user-read-private` - Access to user profile information
- `user-read-email` - Access to user email
- `user-top-read` - Access to user's top artists and tracks

## Development

### Customizing Colors

Modify the [`spotify_genres`](main.py) dictionary in [main.py](main.py) to add new genres or change existing colors.

## Security Notes

- Never commit your `.env` file to version control
- The app uses session-based token storage (suitable for development)
- For production, consider more secure token storage methods

## Troubleshooting

### Common Issues

1. **"Invalid redirect URI"** - Ensure your Spotify app settings match the `REDIRECT_URI` in your `.env` file

2. **"Token expired"** - The app should automatically refresh tokens, but you can manually refresh at `/refresh-token`

3. **No artists showing** - Make sure you have listening history on Spotify (the app shows short-term top artists)

4. **Certain artists don't have genres** - Due to API limitations, some artists may not have genre information registered. The interpolation of these artists' genres using their related artists' genres is also impossible due to the removal of that endpoint by Spotify.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is for educational purposes. Please respect Spotify's API terms of service.