# University Chatbot Frontend

A modern, responsive web interface for the University Chatbot system.

## Features

- 🎨 **Modern UI Design** - Clean, professional interface with gradient backgrounds
- 💬 **Real-time Chat** - Interactive chat interface with the AI chatbot
- 🔍 **Document Search** - Quick search through university documents
- 📊 **System Statistics** - View system health and performance metrics
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices
- ⚡ **Fast Performance** - Optimized for quick responses and smooth interactions

## Quick Start

### Prerequisites

1. **API Server Running** - Make sure your University Chatbot API is running on port 8001
2. **Python 3.6+** - For serving the frontend files

### Running the Frontend

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Start the frontend server:**
   ```bash
   python server.py
   ```

3. **Open your browser and go to:**
   ```
   http://localhost:3000
   ```

### Alternative: Using Python's built-in server

If you prefer to use Python's built-in HTTP server:

```bash
cd frontend
python -m http.server 3000
```

## Usage

### Chat Interface

- **Type your question** in the chat input field
- **Press Enter** or click the send button to submit
- **Use suggestion buttons** for quick common questions
- **View sources and confidence** scores for each response

### Quick Search

- **Search documents** using the sidebar search box
- **View search results** with similarity scores
- **Click on suggestions** for instant searches

### System Status

The sidebar shows:
- **API Status** - Online/Offline indicator
- **Document Count** - Number of documents in the database
- **University Count** - Number of universities in the database

### Statistics Modal

Click "View Stats" to see:
- **Total Documents** in the database
- **Total Universities** in the database
- **Messages Today** - Chat activity counter
- **Average Response Time** - Performance metrics

## File Structure

```
frontend/
├── index.html          # Main HTML file
├── styles.css          # CSS styles
├── script.js           # JavaScript functionality
├── server.py           # Simple HTTP server
└── README.md           # This file
```

## API Endpoints Used

The frontend connects to these API endpoints:

- `GET /` - Health check
- `POST /chat` - Send chat messages
- `GET /search?query=<query>&k=<limit>` - Search documents

## Customization

### Changing the API URL

Edit `script.js` and update the `apiBaseUrl` in the constructor:

```javascript
this.apiBaseUrl = 'http://localhost:8001'; // Change this to your API URL
```

### Styling

Modify `styles.css` to customize:
- Colors and gradients
- Layout and spacing
- Typography
- Responsive breakpoints

### Adding Features

The JavaScript is organized in a class structure, making it easy to add new features:

```javascript
// Add new methods to the UniversityChatbot class
class UniversityChatbot {
    // ... existing code ...
    
    async newFeature() {
        // Your new functionality here
    }
}
```

## Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:
1. Make sure the frontend server is running
2. Check that the API server allows cross-origin requests
3. Verify the API URL is correct

### API Connection Issues

If the frontend can't connect to the API:
1. Ensure the API server is running on port 8001
2. Check the API URL in `script.js`
3. Verify the API endpoints are working

### Port Already in Use

If port 3000 is already in use:
1. Stop any other servers using port 3000
2. Or modify the port in `server.py`:
   ```python
   PORT = 3001  # Change to a different port
   ```

## Browser Compatibility

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+

## Development

### Adding New Features

1. **HTML** - Add elements to `index.html`
2. **CSS** - Style new elements in `styles.css`
3. **JavaScript** - Add functionality in `script.js`

### Testing

1. Start the API server
2. Start the frontend server
3. Open the browser and test all features
4. Check browser console for any errors

## Support

If you encounter issues:
1. Check the browser console for error messages
2. Verify the API server is running and accessible
3. Ensure all files are in the correct locations
4. Check that ports 3000 and 8001 are available

---

**Happy chatting! 🎓** 