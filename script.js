// Global variables
let movies = [];
let movieTitles = [];
let tfidfMatrix = [];
let cosineSim = [];
let indices = {};

// Load movies data
async function loadMovies() {
    try {
        const response = await fetch('movies.csv');
        const data = await response.text();
        
        // Parse CSV
        const rows = data.split('\n').slice(1); // Skip header
        movies = rows.map(row => {
            const [id, title, genres] = row.split(',');
            return { id, title, genres: genres || '' };
        });

        // Create movie titles array for autocomplete
        movieTitles = movies.map(movie => movie.title).sort();
        
        // Populate datalist for autocomplete
        const datalist = document.getElementById('movies');
        movieTitles.forEach(title => {
            const option = document.createElement('option');
            option.value = title;
            datalist.appendChild(option);
        });

        // Create title to index mapping
        movies.forEach((movie, idx) => {
            indices[movie.title] = idx;
        });

        // Create TFIDF matrix
        createTFIDFMatrix();
    } catch (error) {
        console.error('Error loading movies:', error);
        showError('Failed to load movie data. Please try again later.');
    }
}

// Create TFIDF Matrix for genre similarity
function createTFIDFMatrix() {
    // Create document frequency map
    const df = new Map();
    const documents = movies.map(movie => movie.genres.split('|'));
    
    documents.forEach(genres => {
        const uniqueGenres = new Set(genres);
        uniqueGenres.forEach(genre => {
            df.set(genre, (df.get(genre) || 0) + 1);
        });
    });

    // Calculate TF-IDF
    const N = documents.length;
    tfidfMatrix = documents.map(genres => {
        const vector = new Map();
        genres.forEach(genre => {
            if (genre) {
                const tf = 1; // Binary term frequency
                const idf = Math.log(N / df.get(genre));
                vector.set(genre, tf * idf);
            }
        });
        return vector;
    });

    // Compute cosine similarity matrix
    cosineSim = Array(N).fill().map(() => Array(N).fill(0));
    
    for (let i = 0; i < N; i++) {
        for (let j = i; j < N; j++) {
            const sim = calculateCosineSimilarity(tfidfMatrix[i], tfidfMatrix[j]);
            cosineSim[i][j] = sim;
            cosineSim[j][i] = sim;
        }
    }
}

// Calculate cosine similarity between two vectors
function calculateCosineSimilarity(vec1, vec2) {
    let dotProduct = 0;
    let norm1 = 0;
    let norm2 = 0;

    // Calculate dot product and norms
    vec1.forEach((value, key) => {
        norm1 += value * value;
        if (vec2.has(key)) {
            dotProduct += value * vec2.get(key);
        }
    });

    vec2.forEach((value) => {
        norm2 += value * value;
    });

    // Return cosine similarity
    return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2)) || 0;
}

// Fuzzy match movie title
function fuzzyMatch(title) {
    if (!title) return null;
    
    if (indices.hasOwnProperty(title)) {
        return title;
    }

    const titleLower = title.toLowerCase();
    const match = movieTitles.find(t => t && t.toLowerCase().includes(titleLower));
    return match || null;
}

// Get movie recommendations
function getRecommendations(title, n = 5) {
    const matchedTitle = fuzzyMatch(title);
    
    if (!matchedTitle) {
        return {
            status: 'error',
            message: '❌ Movie not found in dataset.',
            input_title: title,
            recommendations: []
        };
    }

    const idx = indices[matchedTitle];
    const inputGenres = new Set(movies[idx].genres.split('|'));

    // Calculate similarity scores
    const simScores = movies.map((movie, i) => {
        if (i === idx) return [-1, -1]; // Skip input movie

        const movieGenres = new Set(movie.genres.split('|'));
        const genreOverlap = intersection(inputGenres, movieGenres).size / union(inputGenres, movieGenres).size;
        const combinedScore = (cosineSim[idx][i] + genreOverlap) / 2;
        
        return [i, combinedScore];
    }).filter(score => score[1] !== -1);

    // Sort and get top N recommendations
    simScores.sort((a, b) => b[1] - a[1]);
    const topN = simScores.slice(0, n);

    const recommendations = topN.map(([movieIdx, score]) => ({
        title: movies[movieIdx].title,
        genres: movies[movieIdx].genres.split('|'),
        similarity_score: Math.round(score * 100)
    }));

    return {
        status: 'success',
        message: '✅ Found recommendations!',
        input_title: matchedTitle,
        recommendations
    };
}

// Set operations helpers
function intersection(setA, setB) {
    return new Set([...setA].filter(x => setB.has(x)));
}

function union(setA, setB) {
    return new Set([...setA, ...setB]);
}

// UI Functions
function showLoader() {
    document.getElementById('loader').classList.remove('hidden');
    document.getElementById('error').classList.add('hidden');
    document.getElementById('recommendations').innerHTML = '';
}

function hideLoader() {
    document.getElementById('loader').classList.add('hidden');
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function displaySuggestions(suggestions) {
    const container = document.getElementById('suggestions');
    if (suggestions.length === 0) {
        container.innerHTML = '<p>No matching movies found. Try a different search term!</p>';
        return;
    }

    container.innerHTML = `
        <h3>Matching Movies:</h3>
        ${suggestions.map(movie => `<p>- ${movie}</p>`).join('')}
    `;
}

function displayRecommendations(result) {
    const container = document.getElementById('recommendations');
    
    if (result.status === 'error') {
        showError(result.message);
        return;
    }

    container.innerHTML = `
        <h3>Recommendations based on '${result.input_title}':</h3>
        ${result.recommendations.map(movie => `
            <div class="movie-card">
                <h3>${movie.title}</h3>
                <p class="similarity-score">Similarity: ${movie.similarity_score}%</p>
                <p>Genres: ${movie.genres.map(genre => 
                    `<span class="genre-tag">${genre}</span>`).join(' ')}
                </p>
            </div>
        `).join('')}
    `;
}

// Event Listeners
document.getElementById('movieSearch').addEventListener('input', (e) => {
    const searchTerm = e.target.value;
    if (!searchTerm) {
        document.getElementById('suggestions').innerHTML = '';
        document.getElementById('recommendations').innerHTML = '';
        return;
    }

    // Filter and display suggestions
    const filtered = movieTitles.filter(title => 
        title && title.toLowerCase().includes(searchTerm.toLowerCase())
    ).slice(0, 5);
    
    displaySuggestions(filtered);

    if (filtered.length > 0) {
        showLoader();
        const n = parseInt(document.getElementById('numRecommendations').value);
        const result = getRecommendations(filtered[0], n);
        hideLoader();
        displayRecommendations(result);
    }
});

// Initialize
loadMovies();
